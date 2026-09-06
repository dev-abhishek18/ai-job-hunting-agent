import sqlite3
from pathlib import Path

DB_PATH = Path("jobs.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, fingerprint TEXT NOT NULL UNIQUE, canonical_url TEXT,
        title TEXT NOT NULL, company TEXT NOT NULL, location TEXT, work_mode TEXT, description TEXT NOT NULL,
        experience_min REAL, experience_max REAL, source TEXT NOT NULL, job_url TEXT NOT NULL, posted_at TEXT,
        first_seen_at TEXT NOT NULL, last_seen_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'NEW')""")
    columns = {row[1] for row in conn.execute("PRAGMA table_info(jobs)").fetchall()}
    if "canonical_url" not in columns: conn.execute("ALTER TABLE jobs ADD COLUMN canonical_url TEXT")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_jobs_canonical_url ON jobs(canonical_url) WHERE canonical_url IS NOT NULL AND canonical_url != ''")
    conn.execute("""CREATE TABLE IF NOT EXISTS job_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER NOT NULL UNIQUE, role_score REAL NOT NULL,
        skill_score REAL NOT NULL, experience_score REAL NOT NULL, location_score REAL NOT NULL,
        freshness_score REAL NOT NULL, overall_score REAL NOT NULL, matched_skills TEXT, missing_skills TEXT, recommendation TEXT,
        FOREIGN KEY(job_id) REFERENCES jobs(id))""")
    conn.execute("""CREATE TABLE IF NOT EXISTS candidate_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, total_experience_years REAL,
        target_roles TEXT NOT NULL, preferred_locations TEXT NOT NULL DEFAULT '[]', skills TEXT NOT NULL,
        projects_text TEXT DEFAULT '', summary TEXT DEFAULT '', cv_filename TEXT DEFAULT '', cv_version INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS candidate_job_status (
        candidate_id INTEGER NOT NULL, job_id INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'NEW',
        first_seen_at TEXT NOT NULL, seen_at TEXT, PRIMARY KEY(candidate_id, job_id),
        FOREIGN KEY(candidate_id) REFERENCES candidate_profiles(id), FOREIGN KEY(job_id) REFERENCES jobs(id))""")
    conn.commit()
    conn.close()
