import streamlit as st

from app.database import init_db
from app.profile_repository import create_profile, get_profile, update_profile, candidate_jobs, mark_candidate_seen
from app.cv_parser import parse_cv
from app.daily import collect_daily
from app.daily_config import configured_collectors

st.set_page_config(page_title="AI Job Hunting Agent", page_icon="🎯", layout="wide")
init_db()

st.title("🎯 AI Job Hunting Agent")
st.caption("CV-driven job matching • 24-hour freshness • duplicate protection • multi-source search")

if "profile_id" not in st.session_state:
    st.session_state.profile_id = None

with st.sidebar:
    st.header("👤 Candidate Profile")
    profile_id = st.number_input("Profile ID", min_value=1, value=int(st.session_state.profile_id or 1), step=1)
    if st.button("Load Profile", use_container_width=True):
        p = get_profile(profile_id)
        if p:
            st.session_state.profile_id = profile_id
            st.success("Profile loaded")
        else:
            st.error("Profile not found")

    st.divider()
    st.subheader("Upload CV")
    cv = st.file_uploader("PDF CV", type=["pdf"], key="cv_upload")
    cv_mode = st.radio("Action", ["Create profile", "Update existing profile"], label_visibility="collapsed")
    if cv and st.button("Process CV", type="primary", use_container_width=True):
        tmp_path = "data/_streamlit_cv.pdf"
        with open(tmp_path, "wb") as f:
            f.write(cv.getbuffer())
        parsed = parse_cv(tmp_path)
        parsed["preferred_locations"] = ["Delhi NCR", "Noida", "Gurgaon", "Gurugram", "Delhi", "Remote"]
        if cv_mode == "Create profile":
            p = create_profile(parsed, cv.name)
            st.session_state.profile_id = p["id"]
            st.success(f"Profile created: #{p['id']}")
        else:
            p = get_profile(profile_id)
            if not p:
                st.error("Load a valid profile ID first")
            else:
                _, diff = update_profile(profile_id, parsed, cv.name)
                st.session_state.profile_id = profile_id
                st.success("CV updated")
                st.json(diff)

pid = st.session_state.profile_id
profile = get_profile(pid) if pid else None

if not profile:
    st.info("Start by uploading your CV from the sidebar to create your candidate profile.")
    st.stop()

jobs = candidate_jobs(pid, 100)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Experience", f"{profile.get('total_experience_years') or 0} yrs")
col2.metric("Target Roles", len(profile.get("target_roles", [])))
col3.metric("Skills", len(profile.get("skills", [])))
col4.metric("New Matches", len(jobs))

st.divider()

with st.expander("📄 My Profile", expanded=True):
    left, right = st.columns(2)
    with left:
        st.write("**Name:**", profile.get("name"))
        st.write("**CV:**", profile.get("cv_filename"))
        st.write("**CV Version:**", profile.get("cv_version"))
        st.write("**Roles:**", ", ".join(profile.get("target_roles", [])))
    with right:
        st.write("**Locations:**", ", ".join(profile.get("preferred_locations", [])))
        st.write("**Skills:**", ", ".join(profile.get("skills", [])))

st.subheader("🔥 Today's Job Matches")
if st.button("Run Job Search Now", type="primary"):
    with st.spinner("Collecting, filtering, deduplicating and scoring jobs..."):
        try:
            result = collect_daily(
                configured_collectors(),
                target_count=10,
                candidate=profile,
                candidate_id=pid,
            )
            st.session_state.daily_result = result
        except Exception as e:
            st.error(f"Job collection failed: {e}")
            st.info("Check .env and configure the enabled job sources first.")

result = st.session_state.get("daily_result")
if result:
    st.write(f"**New jobs found:** {result.get('new_relevant_jobs', len(result.get('jobs', [])))} / {result.get('target_count', 10)}")
    if result.get("source_errors"):
        st.warning("One or more job sources failed:")
        st.json(result["source_errors"])
    for job in result.get("jobs", []):
        score = job.get("overall_score", "—")
        rec = job.get("recommendation", "")
        with st.container(border=True):
            a, b = st.columns([4, 1])
            with a:
                st.markdown(f"### {job.get('title', 'Untitled')}")
                st.write(f"**{job.get('company', '')}** • {job.get('location', '')}")
                st.caption(f"Posted: {job.get('posted_at', 'unknown')} • Match: {score} • {rec}")
                if job.get("matched_skills"):
                    st.write("Matched skills:", ", ".join(job["matched_skills"]))
                if job.get("missing_skills"):
                    st.write("Missing skills:", ", ".join(job["missing_skills"]))
            with b:
                if job.get("job_url"):
                    st.link_button("Apply / Open", job["job_url"], use_container_width=True)

st.subheader("📌 Stored New Matches")
if not jobs:
    st.caption("No candidate-specific NEW jobs stored yet.")
else:
    for job in jobs:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 2, 1])
            with c1:
                st.write(f"**{job.get('title')}** — {job.get('company')}")
                st.caption(f"{job.get('location')} • {job.get('recommendation') or 'No recommendation'}")
            with c2:
                st.metric("Score", job.get("overall_score") or 0)
            with c3:
                if st.button("Seen", key=f"seen_{job['id']}"):
                    mark_candidate_seen(pid, job["id"])
                    st.rerun()
