from app.matching import score_job

def test_r_does_not_match_everything():
    result = score_job({
        "title": "Data Analyst",
        "description": "SQL, Power BI and Excel required",
        "location": "Noida",
        "work_mode": "Hybrid",
        "posted_at": "2026-09-06T10:00:00+00:00",
        "experience_min": 1,
        "experience_max": 5,
    })
    assert "R" not in result["missing_skills"]
