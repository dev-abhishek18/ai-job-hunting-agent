import re

SKILL_ALIASES = {"sql server":"SQL","mysql":"SQL","advanced sql":"SQL","power bi":"Power BI","dax":"DAX","ms excel":"Excel","excel":"Excel","python":"Python","pandas":"Pandas","etl":"ETL","stored procedures":"Stored Procedures","query optimization":"Query Optimization"}

def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9+#. ]+", " ", text.lower()).strip()

def extract_candidate_skill(skill: str) -> str:
    return SKILL_ALIASES.get(normalize(skill), skill)

def score_job(job: dict, candidate: dict) -> dict:
    text = normalize(f"{job['title']} {job['description']}")
    title = normalize(job["title"])
    target_roles = [normalize(x) for x in candidate.get("target_roles", [])]
    role_score = 25.0 if any(role in title for role in target_roles) else 0.0
    matched = []
    for skill in candidate.get("skills", []):
        canonical = extract_candidate_skill(skill)
        if normalize(skill) in text or normalize(canonical) in text:
            if canonical not in matched: matched.append(canonical)
    common_skills = ["SQL","Power BI","Python","Excel","Tableau","ETL","DAX","Snowflake","Azure","AWS","Looker","R"]
    requested = [s for s in common_skills if (bool(re.search(r"(?<![a-z])r(?![a-z])", text)) if s == "R" else normalize(s) in text)]
    present = sum(1 for s in requested if s in matched)
    skill_score = 35.0 if not requested else min(35.0, 35.0 * present / len(requested))
    candidate_exp = candidate.get("total_experience_years") or 0
    emin, emax = job.get("experience_min"), job.get("experience_max")
    if emin is not None and candidate_exp < emin: exp_score = 0.0
    elif emax is not None and candidate_exp > emax + 2: exp_score = 5.0
    else: exp_score = 15.0
    location = normalize(job.get("location", ""))
    preferred = [normalize(x) for x in candidate.get("preferred_locations", [])]
    location_score = 10.0 if any(p in location for p in preferred) else 0.0
    freshness_score = 10.0 if job.get("posted_at") else 5.0
    overall = round(min(100.0, role_score + skill_score + exp_score + location_score + freshness_score), 1)
    recommendation = "APPLY_IMMEDIATELY" if overall >= 90 else "HIGH_PRIORITY" if overall >= 80 else "CONSIDER" if overall >= 70 else "SKIP"
    return {"role_score":role_score,"skill_score":round(skill_score,1),"experience_score":exp_score,"location_score":location_score,"freshness_score":freshness_score,"overall_score":overall,"matched_skills":sorted(set(matched)),"missing_skills":sorted(set(requested)-set(matched)),"recommendation":recommendation}
