from datetime import datetime, timezone

from app.filters import is_within_last_24h, basic_relevance, experience_relevant


def test_configured_48_hour_window():
    now = datetime(2026, 9, 6, 12, 0, tzinfo=timezone.utc)
    assert is_within_last_24h("2026-09-05T13:00:00+00:00", now, hours=48)
    assert not is_within_last_24h("2026-09-04T11:00:00+00:00", now, hours=48)
    assert not is_within_last_24h(None, now, hours=48)
    assert not is_within_last_24h("2026-09-07T11:00:00+00:00", now, hours=48)


def test_role_location_relevance_uses_candidate_profile():
    candidate = {
        "target_roles": ["Data Analyst"],
        "preferred_locations": ["Noida", "Remote"],
        "exclude_title_terms": ["senior", "lead", "manager"],
    }
    assert basic_relevance({"title": "Data Analyst", "location": "Noida, India"}, candidate)
    assert basic_relevance({"title": "Data Analyst", "location": "Remote"}, candidate)
    assert not basic_relevance({"title": "Java Developer", "location": "Noida"}, candidate)
    assert not basic_relevance({"title": "Senior Data Analyst", "location": "Noida"}, candidate)
    assert not basic_relevance({"title": "Data Analyst Manager", "location": "Noida"}, candidate)


def test_experience_range_rejects_clearly_senior_job():
    candidate = {"target_experience_min": 1, "target_experience_max": 3}
    assert experience_relevant({"title": "Data Analyst", "description": "1-3 years experience"}, candidate)
    assert not experience_relevant({"title": "Senior Data Analyst", "description": "5-7 years experience"}, candidate)
    assert experience_relevant({"title": "Data Analyst", "description": "Strong SQL skills"}, candidate)
