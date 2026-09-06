# AI Job Hunting Agent MVP v4

CV-driven job hunting agent with 24-hour freshness filtering, duplicate protection, candidate profiles and a browser dashboard.

## Candidate
- Data Analyst, SQL Developer, BI Analyst, Reporting Analyst, MIS Analyst, Database Administrator
- Delhi NCR, Noida, Gurgaon/Gurugram, Delhi, Remote
- Current profile: 4 years total experience

## Browser dashboard
The project now includes a Streamlit UI for local browser testing:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open the local URL shown by Streamlit (normally `http://localhost:8501`).

The dashboard supports:
- Upload a PDF CV and create a candidate profile
- Update an existing profile with a newer CV
- View extracted roles, skills, experience and CV version
- See CV change detection after an update
- Run the configured job collectors
- View match score, recommendation, matched/missing skills
- Open the application link
- Mark candidate-specific jobs as seen

## Sources
- Adzuna: requires `ADZUNA_APP_ID` + `ADZUNA_APP_KEY`
- Greenhouse public boards: add board tokens in `GREENHOUSE_BOARDS`
- Lever public boards: add site names in `LEVER_SITES`

## Anti-repeat logic
1. Canonical job URL is the primary identity when available.
2. Tracking query parameters are removed from URLs.
3. Fingerprint is a secondary identity for sources without stable URLs.
4. A job already stored is never returned as a new job again.
5. Re-running the same collector updates `last_seen_at` instead of creating a duplicate.

## Freshness rule
- A source must provide a real posting/creation timestamp.
- Unknown timestamps are rejected.
- Greenhouse uses `first_published_at` only; `updated_at` is not used as a substitute.
- Lever converts `createdAt` milliseconds to ISO time when available.
- Jobs must satisfy the exact rolling 24-hour window.

## Daily behavior
- Collect → filter → deduplicate → score → return up to 10 new jobs.
- If only 4 new relevant jobs exist, the report contains 4.
- Old jobs are **never** used to pad the daily list.

## FastAPI API
```bash
uvicorn app.main:app --reload
```

Useful endpoints:
- `GET /` — health/status
- `POST /profiles/from-cv` — create profile from PDF
- `POST /profiles/{profile_id}/cv` — update CV/profile
- `GET /profiles/{profile_id}` — inspect profile
- `POST /jobs/ingest?profile_id=1` — ingest and score a job
- `GET /profiles/{profile_id}/jobs` — candidate NEW jobs
- `POST /profiles/{profile_id}/jobs/{job_id}/mark-seen` — mark seen
- `POST /daily/run?profile_id=1` — run daily collection

## Tests
```bash
python -m pytest -q
```

## Important current limitation
The Streamlit dashboard is a local testing UI. The job source credentials/board configuration still need to be supplied in `.env`, and the daily collector currently has a global job-match storage limitation for true multi-candidate production use. This version is intended for validating the workflow before the next hardening pass.
