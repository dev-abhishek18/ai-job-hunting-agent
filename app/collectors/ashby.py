import requests
from .base import JobCollector


class AshbyBoardCollector(JobCollector):
    """Public Ashby job-board API adapter. Uses publishedAt, never crawl time, for freshness."""

    def __init__(self, board_name, source_name=None):
        self.board_name = board_name.strip()
        self.source_name = source_name or f"ashby:{self.board_name}"

    def collect(self):
        url = f"https://api.ashbyhq.com/posting-api/job-board/{self.board_name}"
        response = requests.get(url, params={"includeCompensation": "true"}, timeout=30)
        response.raise_for_status()
        payload = response.json()
        jobs = []
        for item in payload.get("jobs", []):
            location = item.get("location") or item.get("locationName") or ""
            workplace = item.get("workplaceType") or ""
            if item.get("isRemote") and "remote" not in str(location).lower():
                location = f"{location} Remote".strip()
            jobs.append({
                "title": item.get("title", ""),
                "company": self.board_name,
                "location": location,
                "work_mode": workplace,
                "description": item.get("descriptionPlain") or item.get("descriptionHtml") or "",
                "experience_min": None,
                "experience_max": None,
                "source": self.source_name,
                "job_url": item.get("jobUrl") or item.get("applyUrl") or "",
                "posted_at": item.get("publishedAt"),
                "requisition_id": item.get("id") or item.get("jobId"),
                "freshness_source": "ashby_published_at"
            })
        return jobs
