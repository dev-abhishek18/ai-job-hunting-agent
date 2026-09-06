from datetime import datetime, timezone, timedelta
from .candidate import CANDIDATE

def parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None

def is_within_last_24h(posted_at: str, now=None) -> bool:
    dt = parse_dt(posted_at)
    if dt is None:
        return False
    now = now or datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return now - timedelta(hours=24) <= dt <= now

def basic_relevance(job: dict) -> bool:
    title = job.get("title", "").lower()
    role_ok = any(role.lower() in title for role in CANDIDATE["target_roles"])
    location_text = job.get("location", "").lower()
    location_ok = any(loc.lower() in location_text for loc in CANDIDATE["preferred_locations"])
    remote_ok = "remote" in job.get("work_mode", "").lower() or "remote" in location_text
    return role_ok and (location_ok or remote_ok)

def fresh_and_relevant(job: dict, now=None) -> bool:
    return is_within_last_24h(job.get("posted_at"), now) and basic_relevance(job)
