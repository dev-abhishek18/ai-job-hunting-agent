from dataclasses import dataclass
import os

@dataclass
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./jobs.db")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

settings = Settings()
