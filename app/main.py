from fastapi import FastAPI
from .database import init_db
from .models import JobIn
from .repository import upsert_job, save_match, get_new_jobs, mark_seen
from .matching import score_job
from .daily import collect_daily
from .report import make_daily_report
from .daily_config import configured_collectors

app = FastAPI(title="AI Job Hunting Agent", version="0.3.0", description="Fresh-job collection, 24-hour filtering, deduplication and candidate-job matching.")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"agent": "AI Job Hunting Agent", "version": "0.3.0", "status": "running"}

@app.post("/jobs/ingest")
def ingest_job(job: JobIn):
    data = job.model_dump()
    row, is_new = upsert_job(data)
    result = score_job(data)
    save_match(row["id"], result)
    return {"is_new": is_new, "job_id": row["id"], "fingerprint": row["fingerprint"], "match": result}

@app.get("/jobs/new")
def new_jobs(limit: int = 20):
    jobs = get_new_jobs(limit)
    return {"count": len(jobs), "jobs": jobs}

@app.post("/jobs/{job_id}/mark-seen")
def seen(job_id: int):
    mark_seen(job_id)
    return {"job_id": job_id, "status": "SEEN"}

@app.post("/daily/run")
def daily_run():
    return collect_daily(configured_collectors(), target_count=10)

@app.post("/daily/report")
def daily_report():
    result = collect_daily(configured_collectors(), target_count=10)
    return {"report": make_daily_report(result), "data": result}
