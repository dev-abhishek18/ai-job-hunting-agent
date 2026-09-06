from .config import settings
from .collectors.adzuna import AdzunaCollector
from .collectors.greenhouse import GreenhouseBoardCollector
from .collectors.lever import LeverBoardCollector
import os


def configured_collectors():
    collectors = [
        AdzunaCollector(
            queries=[
                "Data Analyst", "SQL Developer", "BI Analyst", "Reporting Analyst",
                "MIS Analyst", "Database Administrator",
            ],
            location=settings.job_location,
            pages=2,
        )
    ]

    for token in filter(None, os.getenv("GREENHOUSE_BOARDS", "").split(",")):
        collectors.append(GreenhouseBoardCollector(token.strip()))
    for site in filter(None, os.getenv("LEVER_SITES", "").split(",")):
        collectors.append(LeverBoardCollector(site.strip()))
    return collectors
