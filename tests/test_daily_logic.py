from app.filters import is_within_last_24h
from datetime import datetime, timezone

def test_24_hour_window():
    now = datetime(2026, 9, 6, 12, 0, tzinfo=timezone.utc)
    assert is_within_last_24h("2026-09-06T11:00:00+00:00", now)
    assert not is_within_last_24h("2026-09-05T11:00:00+00:00", now)
