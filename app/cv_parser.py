import re
from pathlib import Path
from typing import Any


def extract_text_from_pdf(path: str) -> str:
    from pypdf import PdfReader
    reader = PdfReader(path)
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _section(text: str, names: list[str]) -> str:
    pattern = r"(?is)(?:^|\n)\s*(?:" + "|".join(map(re.escape, names)) + r")\s*[:\-]?\s*\n?(.*?)(?=\n\s*(?:PROFESSIONAL SUMMARY|SUMMARY|SKILLS|TECHNICAL SKILLS|EXPERIENCE|WORK EXPERIENCE|PROJECTS|EDUCATION|CERTIFICATIONS)\b|\Z)"
    m = re.search(pattern, text)
    return m.group(1).strip() if m else ""


def parse_cv_text(text: str) -> dict[str, Any]:
    clean = re.sub(r"[ \t]+", " ", text)
    lower = clean.lower()
    skills_catalog = [
        "SQL", "SQL Server", "MySQL", "Advanced SQL", "CTE", "Window Functions", "Stored Procedures",
        "ETL", "Query Optimization", "Database Performance Tuning", "Python", "Pandas", "NumPy",
        "Matplotlib", "Scikit-learn", "Power BI", "DAX", "Excel", "Power Query", "Jupyter Notebook",
        "Git", "GitHub", "Streamlit", "EDA", "Data Cleaning", "Data Validation", "KPI Development",
        "Trend Analysis", "Reporting Automation", "Stakeholder Management", "React", "JavaScript",
        "TypeScript", "Node.js", "AWS", "Azure", "Snowflake", "Tableau", "Looker", "R"
    ]
    skills = [s for s in skills_catalog if s.lower() in lower]
    role_catalog = ["Data Analyst", "SQL Developer", "BI Analyst", "Reporting Analyst", "MIS Analyst", "Database Administrator", "React Developer", "Frontend Developer", "Software Developer"]
    roles = [r for r in role_catalog if r.lower() in lower]
    exp = None
    matches = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", lower)
    if matches:
        exp = max(float(x) for x in matches)
    name = clean.splitlines()[0].strip() if clean.splitlines() else ""
    projects = _section(text, ["PROJECTS", "PROJECT EXPERIENCE"])
    summary = _section(text, ["PROFESSIONAL SUMMARY", "SUMMARY"])
    return {
        "name": name,
        "total_experience_years": exp,
        "target_roles": roles,
        "skills": skills,
        "projects_text": projects,
        "summary": summary,
    }


def parse_cv(path: str) -> dict[str, Any]:
    return parse_cv_text(extract_text_from_pdf(path))
