# Default candidate/search profile. Full editable search policy lives in data/search_profile.json.
# Keep this file editable so the agent can support multiple candidate profiles.

CANDIDATE = {
    "name": "Abhishek Pal",
    "total_experience_years": 4.0,
    "target_roles": [
        "Data Analyst", "SQL Developer", "SQL Data Analyst", "BI Analyst",
        "Business Intelligence Analyst", "Reporting Analyst", "MIS Analyst",
        "MIS Executive", "Power BI Analyst", "Database Administrator",
        "ETL Developer", "Database Developer", "Junior Database Administrator",
        "Data Reporting Analyst", "Data Quality Analyst", "Operations Analyst",
        "Reporting Executive",
    ],
    "preferred_locations": [
        "Delhi NCR", "Noida", "Gurgaon", "Gurugram", "Delhi", "Remote",
    ],
    # This is the desired job requirement range, not the candidate's own experience.
    "target_experience_min": 1.0,
    "target_experience_max": 3.0,
    "freshness_hours": 48,
    "exclude_title_terms": [
        "senior", "lead", "manager", "director", "principal", "architect",
    ],
    "skills": [
        "SQL", "SQL Server", "MySQL", "Advanced SQL", "CTE", "Window Functions",
        "Stored Procedures", "ETL", "Query Optimization", "Database Performance Tuning",
        "Python", "Pandas", "NumPy", "Matplotlib", "Scikit-learn", "Power BI", "DAX",
        "Excel", "Power Query", "Jupyter Notebook", "Git", "GitHub", "Streamlit", "EDA",
        "Data Cleaning", "Data Validation", "KPI Development", "Trend Analysis",
        "Reporting Automation", "Stakeholder Management", "Database Administration",
    ],
}
