import json
from pathlib import Path
from .base import JobCollector

class JsonFeedCollector(JobCollector):
    """Safe MVP adapter for a permitted JSON feed exported by a job provider or organization's career system."""
    def __init__(self, path: str, source_name: str):
        self.path = Path(path)
        self.source_name = source_name

    def collect(self) -> list[dict]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("JSON feed must contain a list of jobs")
        jobs = []
        for item in data:
            item = dict(item)
            item["source"] = self.source_name
            jobs.append(item)
        return jobs
