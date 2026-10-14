import json
import os
from pathlib import Path

from .config import settings
from .collectors.adzuna import AdzunaCollector
from .collectors.greenhouse import GreenhouseBoardCollector
from .collectors.lever import LeverBoardCollector
from .collectors.ashby import AshbyBoardCollector


def load_search_profile():
    path = Path(__file__).resolve().parent.parent / "data" / "search_profile.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def configured_collectors():
    profile = load_search_profile()
    search = profile.get("search", {})
    roles = search.get("primary_roles", []) + search.get("secondary_roles", [])
    # Keep requests bounded: use role phrases across NCR and remote searches, not every
    # role × every city × multiple pages. NCR searches include Noida/Gurugram/Delhi.
    queries = list(dict.fromkeys(roles))
    locations = [settings.job_location]
    remote_location = os.getenv("JOB_REMOTE_LOCATION", "Remote")
    if remote_location.lower() not in settings.job_location.lower():
        locations.append(remote_location)

    collectors = []
    for location in locations:
        collectors.append(AdzunaCollector(queries=queries, location=location, pages=1))

    for token in filter(None, os.getenv("GREENHOUSE_BOARDS", "").split(",")):
        collectors.append(GreenhouseBoardCollector(token.strip()))
    for site in filter(None, os.getenv("LEVER_SITES", "").split(",")):
        collectors.append(LeverBoardCollector(site.strip()))
    for board in filter(None, os.getenv("ASHBY_BOARDS", "").split(",")):
        collectors.append(AshbyBoardCollector(board.strip()))
    return collectors
