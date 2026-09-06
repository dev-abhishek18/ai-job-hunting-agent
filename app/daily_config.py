import os
from .collectors.adzuna import AdzunaCollector
from .collectors.greenhouse import GreenhouseBoardCollector
from .collectors.lever import LeverBoardCollector

def configured_collectors():
    collectors = [AdzunaCollector(
        queries=["Data Analyst", "BI Analyst", "Reporting Analyst", "MIS Analyst", "SQL Developer", "Database Administrator"],
        location=os.getenv("JOB_LOCATION", "Delhi NCR"), pages=2
    )]
    for token in filter(None, os.getenv("GREENHOUSE_BOARDS", "").split(",")):
        collectors.append(GreenhouseBoardCollector(token.strip()))
    for site in filter(None, os.getenv("LEVER_SITES", "").split(",")):
        collectors.append(LeverBoardCollector(site.strip()))
    return collectors
