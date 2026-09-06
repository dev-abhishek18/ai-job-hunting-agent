import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from .database import init_db
from .models import JobIn
from .repository import upsert_job, save_match
from .matching import score_job
from .cv_parser import parse_cv
from .profile_repository import create_profile, get_profile, update_profile, attach_job, candidate_jobs, mark_candidate_seen
from .daily import collect_daily
from .daily_config import configured_collectors

app=FastAPI(title="AI Job Hunting Agent",version="0.4.0",description="CV-driven personalized job hunting agent.")
@app.on_event("startup")
def startup(): init_db()
@app.get("/")
def root(): return {"agent":"AI Job Hunting Agent","version":"0.4.0","status":"running","features":["CV profiles","CV versioning","profile-driven matching","per-candidate job history"]}

def _parse_upload(data):
    with tempfile.NamedTemporaryFile(suffix=".pdf",delete=False) as tmp: tmp.write(data); return parse_cv(tmp.name)

@app.post("/profiles/from-cv")
async def create_profile_from_cv(file:UploadFile=File(...)):
    if not file.filename.lower().endswith(".pdf"): raise HTTPException(400,"Only PDF CV files are supported")
    parsed=_parse_upload(await file.read()); parsed["preferred_locations"]=["Delhi NCR","Noida","Gurgaon","Gurugram","Delhi","Remote"]
    return {"profile":create_profile(parsed,file.filename),"parsed":parsed}

@app.post("/profiles/{profile_id}/cv")
async def update_profile_cv(profile_id:int,file:UploadFile=File(...)):
    if not get_profile(profile_id): raise HTTPException(404,"Profile not found")
    if not file.filename.lower().endswith(".pdf"): raise HTTPException(400,"Only PDF CV files are supported")
    parsed=_parse_upload(await file.read()); profile,diff=update_profile(profile_id,parsed,file.filename)
    return {"profile":profile,"cv_changes":diff,"message":"Profile updated; future job matching uses the latest CV profile."}

@app.get("/profiles/{profile_id}")
def profile(profile_id:int):
    p=get_profile(profile_id)
    if not p: raise HTTPException(404,"Profile not found")
    return p

@app.post("/jobs/ingest")
def ingest_job(job:JobIn,profile_id:int|None=None):
    data=job.model_dump(); row,is_new=upsert_job(data); result=None
    if profile_id is not None:
        candidate=get_profile(profile_id)
        if not candidate: raise HTTPException(404,"Profile not found")
        result=score_job(data,candidate); save_match(row["id"],result); attach_job(profile_id,row["id"])
    return {"is_new":is_new,"job_id":row["id"],"match":result}

@app.get("/profiles/{profile_id}/jobs")
def profile_jobs(profile_id:int,limit:int=20):
    if not get_profile(profile_id): raise HTTPException(404,"Profile not found")
    jobs=candidate_jobs(profile_id,limit); return {"count":len(jobs),"jobs":jobs}

@app.post("/profiles/{profile_id}/jobs/{job_id}/mark-seen")
def profile_seen(profile_id:int,job_id:int):
    if not get_profile(profile_id): raise HTTPException(404,"Profile not found")
    mark_candidate_seen(profile_id,job_id); return {"profile_id":profile_id,"job_id":job_id,"status":"SEEN"}

@app.post("/daily/run")
def daily_run(profile_id:int|None=None):
    candidate=get_profile(profile_id) if profile_id else None
    if profile_id and not candidate: raise HTTPException(404,"Profile not found")
    return collect_daily(configured_collectors(),target_count=10,candidate=candidate)
