import requests
from .base import JobCollector

class GreenhouseBoardCollector(JobCollector):
    """Public Greenhouse Job Board adapter using first_published_at for freshness."""
    def __init__(self, board_token, source_name=None):
        self.board_token = board_token
        self.source_name = source_name or f"greenhouse:{board_token}"

    def collect(self):
        url = f"https://boards-api.greenhouse.io/v1/boards/{self.board_token}/jobs"
        r = requests.get(url, params={"content": "true"}, timeout=30)
        r.raise_for_status()
        jobs = []
        for item in r.json().get("jobs", []):
            jobs.append({"title": item.get("title", ""), "company": self.board_token,
                         "location": (item.get("location") or {}).get("name", ""), "work_mode": "",
                         "description": item.get("content", ""), "experience_min": None, "experience_max": None,
                         "source": self.source_name, "job_url": item.get("absolute_url", ""),
                         "posted_at": item.get("first_published_at")})
        return jobs
