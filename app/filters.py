from datetime import datetime, timezone, timedelta
import re

from .candidate import CANDIDATE


def parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def is_within_last_24h(posted_at: str, now=None, hours=24) -> bool:
    dt = parse_dt(posted_at)
    if dt is None:
        return False
    now = now or datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return now - timedelta(hours=hours) <= dt <= now


def infer_experience_range(job: dict):
    """Infer a conservative required-experience range from title/description."""
    text = f"{job.get('title', '')} {job.get('description', '')}".lower()

    patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)\s*(?:\+?\s*)?(?:years?|yrs?)",
        r"(\d+(?:\.\d+)?)\s*\+\s*(?:years?|yrs?)",
        r"minimum\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
        r"at\s+least\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
        r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s*(?:of\s+)?experience",
    ]

    for index, pattern in enumerate(patterns):
        match = re.search(pattern, text)
        if not match:
            continue
        if index == 0:
            return float(match.group(1)), float(match.group(2))
        minimum = float(match.group(1))
        return minimum, None
    return job.get("experience_min"), job.get("experience_max")


def basic_relevance(job: dict, candidate=None) -> bool:
    candidate = candidate or CANDIDATE
    title = job.get("title", "").lower()
    role_ok = any(role.lower() in title for role in candidate.get("target_roles", []))

    location_text = job.get("location", "").lower()
    work_mode = job.get("work_mode", "").lower()
    location_ok = any(loc.lower() in location_text for loc in candidate.get("preferred_locations", []))
    remote_ok = "remote" in work_mode or "remote" in location_text
    return role_ok and (location_ok or remote_ok)


def experience_relevant(job: dict, candidate=None) -> bool:
    """Reject jobs whose explicit experience requirement is outside the desired range.

    Unknown experience is retained because many job feeds omit this field.
    """
    candidate = candidate or CANDIDATE
    minimum, maximum = infer_experience_range(job)
    if minimum is None and maximum is None:
        return True

    target_min = candidate.get("target_experience_min")
    target_max = candidate.get("target_experience_max")
    if target_min is None and target_max is None:
        return True

    # Reject only when the known job range is wholly above/below the target range.
    if maximum is not None and target_min is not None and maximum < target_min:
        return False
    if minimum is not None and target_max is not None and minimum > target_max:
        return False
    return True


def fresh_and_relevant(job: dict, now=None, candidate=None) -> bool:
    candidate = candidate or CANDIDATE
    return (
        is_within_last_24h(job.get("posted_at"), now, hours=candidate.get("freshness_hours", 24))
        and basic_relevance(job, candidate)
        and experience_relevant(job, candidate)
    )
