from dataclasses import dataclass
import os
from dotenv import load_dotenv

# Load project-local .env for every entry point (CLI, FastAPI, Streamlit, tests).
load_dotenv()

@dataclass
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./jobs.db")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    job_location: str = os.getenv("JOB_LOCATION", "Delhi NCR")
    target_count: int = int(os.getenv("JOB_TARGET_COUNT", "10"))
    freshness_hours: int = int(os.getenv("JOB_FRESHNESS_HOURS", "24"))

settings = Settings()
