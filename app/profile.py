from datetime import datetime, timezone
import json
from .database import get_connection


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def _loads(value, default=None):
    if not value:
        return default if default is not None else []
    try:
        return json.loads(value)
    except Exception:
        return default if default is not None else []


def save_candidate_profile(profile: dict, cv_filename: str = "", cv_version: int | None = None):
    conn = get_connection()
    cur = conn.execute("""INSERT INTO candidate_profiles
        (name,total_experience_years,target_roles,preferred_locations,skills,projects_text,summary,cv_filename,cv_version,created_at,updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", (
        profile.get("name", ""), profile.get("total_experience_years"), json.dumps(profile.get("target_roles", [])),
        json.dumps(profile.get("preferred_locations", [])), json.dumps(profile.get("skills", [])),
        profile.get("projects_text", ""), profile.get("summary", ""), cv_filename, cv_version or 1, now_iso(), now_iso()))
    conn.commit()
    row = conn.execute("SELECT * FROM candidate_profiles WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row)


def get_profile(profile_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM candidate_profiles WHERE id=?", (profile_id,)).fetchone()
    conn.close()
    if not row:
        return None
    p = dict(row)
    for key in ("target_roles", "preferred_locations", "skills"):
        p[key] = _loads(p[key])
    return p


def update_profile_from_cv(profile_id: int, parsed: dict, cv_filename: str):
    old = get_profile(profile_id)
    if not old:
        return None
    merged = dict(old)
    for key in ("name", "total_experience_years", "projects_text", "summary"):
        if parsed.get(key) not in (None, ""):
            merged[key] = parsed[key]
    for key in ("target_roles", "skills"):
        if parsed.get(key):
            merged[key] = parsed[key]
    version = int(old.get("cv_version") or 1) + 1
    conn = get_connection()
    conn.execute("""UPDATE candidate_profiles SET name=?, total_experience_years=?, target_roles=?, skills=?, projects_text=?, summary=?, cv_filename=?, cv_version=?, updated_at=? WHERE id=?""", (
        merged.get("name", ""), merged.get("total_experience_years"), json.dumps(merged.get("target_roles", [])),
        json.dumps(merged.get("skills", [])), merged.get("projects_text", ""), merged.get("summary", ""),
        cv_filename, version, now_iso(), profile_id))
    conn.commit()
    conn.close()
    return get_profile(profile_id)


def diff_profiles(old: dict, new: dict) -> dict:
    return {
        "new_skills": sorted(set(new.get("skills", [])) - set(old.get("skills", []))),
        "removed_skills": sorted(set(old.get("skills", [])) - set(new.get("skills", []))),
        "new_roles": sorted(set(new.get("target_roles", [])) - set(old.get("target_roles", []))),
        "experience_changed": old.get("total_experience_years") != new.get("total_experience_years"),
        "projects_changed": old.get("projects_text", "") != new.get("projects_text", ""),
    }
