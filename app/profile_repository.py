import json
from datetime import datetime, timezone
from .database import get_connection


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def profile_row(row):
    if not row:
        return None
    x = dict(row)
    for k in ("target_roles", "preferred_locations", "skills"):
        x[k] = json.loads(x[k] or "[]")
    return x


def create_profile(profile, filename):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO candidate_profiles(name,total_experience_years,target_roles,preferred_locations,skills,projects_text,summary,cv_filename,cv_version,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (
            profile.get("name", ""), profile.get("total_experience_years"),
            json.dumps(profile.get("target_roles", [])),
            json.dumps(profile.get("preferred_locations", ["Delhi NCR", "Noida", "Gurgaon", "Gurugram", "Delhi", "Remote"])),
            json.dumps(profile.get("skills", [])), profile.get("projects_text", ""),
            profile.get("summary", ""), filename, 1, now_iso(), now_iso(),
        ),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM candidate_profiles WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return profile_row(row)


def get_profile(profile_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM candidate_profiles WHERE id=?", (profile_id,)).fetchone()
    conn.close()
    return profile_row(row)


def update_profile(profile_id, parsed, filename):
    old = get_profile(profile_id)
    if not old:
        return None, {}
    new = dict(old)
    for k in ("name", "total_experience_years", "projects_text", "summary", "preferred_locations"):
        if parsed.get(k) not in (None, "", []):
            new[k] = parsed[k]
    for k in ("target_roles", "skills"):
        if parsed.get(k):
            new[k] = parsed[k]
    diff = {
        "new_skills": sorted(set(new.get("skills", [])) - set(old.get("skills", []))),
        "removed_skills": sorted(set(old.get("skills", [])) - set(new.get("skills", []))),
        "new_roles": sorted(set(new.get("target_roles", [])) - set(old.get("target_roles", []))),
        "experience_changed": old.get("total_experience_years") != new.get("total_experience_years"),
        "projects_changed": old.get("projects_text", "") != new.get("projects_text", ""),
    }
    conn = get_connection()
    conn.execute(
        "UPDATE candidate_profiles SET name=?,total_experience_years=?,target_roles=?,preferred_locations=?,skills=?,projects_text=?,summary=?,cv_filename=?,cv_version=?,updated_at=? WHERE id=?",
        (
            new.get("name", ""), new.get("total_experience_years"),
            json.dumps(new.get("target_roles", [])), json.dumps(new.get("preferred_locations", [])),
            json.dumps(new.get("skills", [])), new.get("projects_text", ""), new.get("summary", ""),
            filename, int(old.get("cv_version") or 1) + 1, now_iso(), profile_id,
        ),
    )
    conn.commit()
    conn.close()
    return get_profile(profile_id), diff


def attach_job(candidate_id, job_id):
    conn = get_connection()
    before = conn.execute(
        "SELECT status FROM candidate_job_status WHERE candidate_id=? AND job_id=?",
        (candidate_id, job_id),
    ).fetchone()
    if before:
        conn.close()
        return False, before["status"]
    conn.execute(
        "INSERT INTO candidate_job_status(candidate_id,job_id,status,first_seen_at) VALUES(?,?, 'NEW',?)",
        (candidate_id, job_id, now_iso()),
    )
    conn.commit()
    conn.close()
    return True, "NEW"


def candidate_jobs(candidate_id, limit=20):
    conn = get_connection()
    rows = conn.execute(
        """SELECT j.*,m.overall_score,m.matched_skills,m.missing_skills,m.recommendation
        FROM candidate_job_status c
        JOIN jobs j ON j.id=c.job_id
        LEFT JOIN job_matches m ON m.job_id=j.id
        WHERE c.candidate_id=? AND c.status='NEW'
        ORDER BY COALESCE(m.overall_score,0) DESC,j.first_seen_at DESC LIMIT ?""",
        (candidate_id, limit),
    ).fetchall()
    conn.close()
    out = []
    for r in rows:
        x = dict(r)
        x["matched_skills"] = json.loads(x["matched_skills"] or "[]")
        x["missing_skills"] = json.loads(x["missing_skills"] or "[]")
        out.append(x)
    return out


def mark_candidate_seen(candidate_id, job_id):
    conn = get_connection()
    conn.execute(
        "UPDATE candidate_job_status SET status='SEEN',seen_at=? WHERE candidate_id=? AND job_id=?",
        (now_iso(), candidate_id, job_id),
    )
    conn.commit()
    conn.close()
