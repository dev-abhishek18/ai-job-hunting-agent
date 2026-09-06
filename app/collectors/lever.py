import requests
from datetime import datetime, timezone
from .base import JobCollector

def ms_to_iso(value):
    if value in (None, ""):
        return None
    try:
        return datetime.fromtimestamp(float(value) / 1000, tz=timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError):
        return None

class LeverBoardCollector(JobCollector):
    """Public Lever postings adapter with strict creation-time freshness."""
    def __init__(self, site, source_name=None):
        self.site = site
        self.source_name = source_name or f"lever:{site}"

    def collect(self):
        url = f"https://api.lever.co/v0/postings/{self.site}"
        r = requests.get(url, params={"mode": "json", "limit": 100}, timeout=30)
        r.raise_for_status()
        jobs = []
        for item in r.json():
            categories = item.get("categories") or {}
            jobs.append({"title": item.get("text", ""), "company": self.site,
                         "location": categories.get("location", ""), "work_mode": item.get("workplaceType", ""),
                         "description": item.get("descriptionPlain") or item.get("description", ""),
                         "experience_min": None, "experience_max": None, "source": self.source_name,
                         "job_url": item.get("hostedUrl") or item.get("applyUrl") or "",
                         "posted_at": ms_to_iso(item.get("createdAt"))})
        return jobs
