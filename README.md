# Job Hunting Agent MVP v4

This version focuses on the core rule: **only genuinely new jobs posted in the last 24 hours** should be surfaced.

## Candidate
- Data Analyst, SQL Developer, BI Analyst, Reporting Analyst, MIS Analyst, Database Administrator
- Delhi NCR, Noida, Gurgaon/Gurugram, Delhi, Remote
- Current profile: 4 years total experience

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

## Run
```bash
pip install -r requirements.txt
copy .env.example .env   # Windows
python run_daily.py
```

For Linux/macOS:
```bash
cp .env.example .env
python run_daily.py
```

## Tests
```bash
python -m pytest -q
```
