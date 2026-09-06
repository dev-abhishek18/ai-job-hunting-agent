import json
from datetime import datetime, timezone
from .database import get_connection
from .dedupe import make_fingerprint, canonicalize_url

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def upsert_job(job: dict):
    fingerprint = make_fingerprint(job)
    canonical_url = canonicalize_url(job.get("job_url", ""))
    now = now_iso()
    conn = get_connection()
    existing = None
    if canonical_url:
        existing = conn.execute("SELECT id FROM jobs WHERE canonical_url = ?", (canonical_url,)).fetchone()
    if not existing:
        existing = conn.execute("SELECT id FROM jobs WHERE fingerprint = ?", (fingerprint,)).fetchone()
    if existing:
        conn.execute("""UPDATE jobs SET last_seen_at=?, canonical_url=?, title=?, company=?, location=?,
               work_mode=?, description=?, experience_min=?, experience_max=?, source=?, job_url=?, posted_at=? WHERE id=?""",
            (now, canonical_url, job["title"], job["company"], job.get("location", ""), job.get("work_mode", ""),
             job["description"], job.get("experience_min"), job.get("experience_max"), job["source"], job["job_url"],
             job.get("posted_at"), existing["id"]))
        conn.commit()
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (existing["id"],)).fetchone()
        conn.close()
        return dict(row), False
    cur = conn.execute("""INSERT INTO jobs (fingerprint, canonical_url, title, company, location, work_mode, description,
            experience_min, experience_max, source, job_url, posted_at, first_seen_at, last_seen_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'NEW')""",
        (fingerprint, canonical_url, job["title"], job["company"], job.get("location", ""), job.get("work_mode", ""),
         job["description"], job.get("experience_min"), job.get("experience_max"), job["source"], job["job_url"],
         job.get("posted_at"), now, now))
    conn.commit()
    row = conn.execute("SELECT * FROM jobs WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row), True

def save_match(job_id: int, result: dict):
    conn = get_connection()
    conn.execute("""INSERT INTO job_matches (job_id, role_score, skill_score, experience_score, location_score,
        freshness_score, overall_score, matched_skills, missing_skills, recommendation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_id) DO UPDATE SET role_score=excluded.role_score, skill_score=excluded.skill_score,
        experience_score=excluded.experience_score, location_score=excluded.location_score,
        freshness_score=excluded.freshness_score, overall_score=excluded.overall_score,
        matched_skills=excluded.matched_skills, missing_skills=excluded.missing_skills,
        recommendation=excluded.recommendation""",
        (job_id, result["role_score"], result["skill_score"], result["experience_score"], result["location_score"],
         result["freshness_score"], result["overall_score"], json.dumps(result["matched_skills"]),
         json.dumps(result["missing_skills"]), result["recommendation"]))
    conn.commit()
    conn.close()

def get_new_jobs(limit: int = 20):
    conn = get_connection()
    rows = conn.execute("""SELECT j.*, m.overall_score, m.matched_skills, m.missing_skills, m.recommendation
        FROM jobs j LEFT JOIN job_matches m ON m.job_id = j.id WHERE j.status = 'NEW'
        ORDER BY COALESCE(m.overall_score, 0) DESC, j.first_seen_at DESC LIMIT ?""", (limit,)).fetchall()
    conn.close()
    result = []
    for row in rows:
        item = dict(row)
        item["matched_skills"] = json.loads(item["matched_skills"] or "[]")
        item["missing_skills"] = json.loads(item["missing_skills"] or "[]")
        result.append(item)
    return result

def mark_seen(job_id: int):
    conn = get_connection()
    conn.execute("UPDATE jobs SET status='SEEN' WHERE id=?", (job_id,))
    conn.commit()
    conn.close()
