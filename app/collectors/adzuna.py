import os
import requests
from .base import JobCollector

class AdzunaCollector(JobCollector):
    """Adzuna search adapter. Requires ADZUNA_APP_ID and ADZUNA_APP_KEY."""
    def __init__(self, queries, location="Delhi NCR", pages=2):
        self.queries = queries
        self.location = location
        self.pages = pages
        self.app_id = os.getenv("ADZUNA_APP_ID", "")
        self.app_key = os.getenv("ADZUNA_APP_KEY", "")
        self.country = os.getenv("ADZUNA_COUNTRY", "in")

    def collect(self):
        if not self.app_id or not self.app_key:
            return []
        jobs = []
        for query in self.queries:
            for page in range(1, self.pages + 1):
                url = f"https://api.adzuna.com/v1/api/jobs/{self.country}/search/{page}"
                params = {"app_id": self.app_id, "app_key": self.app_key, "results_per_page": 50,
                          "what": query, "where": self.location, "content-type": "application/json", "sort_by": "date"}
                r = requests.get(url, params=params, timeout=30)
                r.raise_for_status()
                for item in r.json().get("results", []):
                    jobs.append({"title": item.get("title", ""), "company": (item.get("company") or {}).get("display_name", ""),
                                 "location": (item.get("location") or {}).get("display_name", ""), "work_mode": "",
                                 "description": item.get("description", ""), "experience_min": None, "experience_max": None,
                                 "source": "adzuna", "job_url": item.get("redirect_url", ""), "posted_at": item.get("created")})
        return jobs
