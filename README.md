# AI Job Hunting Agent MVP v5

CV-driven job hunting agent with expanded role searches, rolling 48-hour freshness checks, duplicate protection, candidate profiles and a browser dashboard.

## Candidate search profile
The editable policy is in `data/search_profile.json`. It includes:
- Primary roles: Data Analyst, SQL Developer, SQL Data Analyst, MIS Analyst/Executive, Reporting Analyst, Power BI Analyst and BI Analyst.
- Secondary roles: ETL Developer, Database Developer, Junior DBA, Data Reporting, Data Quality, Operations Analyst and Reporting Executive.
- Locations: Delhi NCR, Noida, Gurugram/Gurgaon, Delhi and Remote.
- Target job requirement: 1–3 years; senior/lead/manager/director/principal/architect titles are excluded.
- Skills: SQL/SQL Server, Excel, Power BI/DAX, Python, ETL, Power Query, reporting and database administration.
- Target output: up to 20; 10 is a goal, not a quota. Never pad with stale or irrelevant jobs.

## Browser dashboard
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The dashboard supports CV upload/versioning, extracted skills and roles, CV change detection, job collection, skill-match breakdown and marking candidate-specific jobs as seen.

## Sources
- Adzuna: requires `ADZUNA_APP_ID` + `ADZUNA_APP_KEY`; searches role phrases in Delhi NCR and Remote.
- Greenhouse public boards: add board tokens in `GREENHOUSE_BOARDS`.
- Lever public boards: add site names in `LEVER_SITES`.
- Ashby public boards: add board names in `ASHBY_BOARDS`.
- LinkedIn, Naukri, Indeed, Foundit, Internshala, Jooble and Joblet.ai are listed as discovery sources in the search policy; this code does not scrape their websites directly. For aggregator leads, verify the same requisition and live apply link at the employer/ATS before calling them verified.

## Freshness tiers
- `VERIFIED_FRESH`: timestamp from configured Greenhouse/Lever/Ashby ATS feed, within the rolling 48-hour window.
- `LIKELY_FRESH`: dated aggregator result within 48 hours; original employer posting still needs verification.
- `DATE_UNCONFIRMED`: relevant live listing without a reliable posting date. Shown separately and never counted as fresh.
- Crawler refresh time is never substituted for a posting date. Missing or old dates are not treated as verified fresh.

## Duplicate and report behavior
- Source + requisition ID is checked first when available, then canonical URL, then content fingerprint.
- Jobs already stored are not returned as new results in later runs.
- Up to 20 new jobs are returned; fewer are reported honestly when fewer qualify.
- Source errors and date-unconfirmed leads are exposed separately in the daily result.

## Setup
Copy `.env.example` to `.env` and add the Adzuna credentials and real ATS board identifiers you want to monitor. Without credentials or configured board names, those sources will not return jobs.

## Run
```bash
uvicorn app.main:app --reload
python -m pytest -q
```

Useful endpoints:
- `GET /` — health/status
- `POST /profiles/from-cv` — create profile from PDF
- `POST /profiles/{profile_id}/cv` — update CV/profile
- `GET /profiles/{profile_id}` — inspect profile
- `GET /profiles/{profile_id}/jobs` — candidate NEW jobs
- `POST /profiles/{profile_id}/jobs/{job_id}/mark-seen` — mark seen
- `POST /daily/run?profile_id=1` — run daily collection

## Known limitation
Public ATS board names and Adzuna credentials must be configured. Direct automated access to LinkedIn/Naukri/Indeed/Foundit/Internshala is not implemented here; the policy includes them as discovery sources, and any candidate listing still needs a live original application URL check.
