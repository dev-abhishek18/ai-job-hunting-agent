from pydantic import BaseModel, Field
from typing import Optional

class JobIn(BaseModel):
    title: str
    company: str
    location: str = ""
    work_mode: str = ""
    description: str
    experience_min: Optional[float] = None
    experience_max: Optional[float] = None
    source: str
    job_url: str
    posted_at: Optional[str] = None

class JobOut(JobIn):
    id: int
    fingerprint: str
    first_seen_at: str
    last_seen_at: str
    status: str
    overall_score: Optional[float] = None
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    recommendation: Optional[str] = None
