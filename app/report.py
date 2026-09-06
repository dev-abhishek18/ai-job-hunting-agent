def make_daily_report(result: dict) -> str:
    lines = [
        "AI JOB HUNTING AGENT — DAILY REPORT",
        f"New relevant jobs: {result['new_relevant_jobs']}/{result['target_count']}",
        f"Duplicates skipped: {result['duplicates_skipped']}",
        f"Rejected (not fresh/relevant): {result['not_fresh_or_relevant']}", "",
    ]
    for i, job in enumerate(result["jobs"], start=1):
        lines.extend([
            f"{i}. {job['title']} — {job['company']}",
            f"   Location: {job.get('location','')} | Score: {job.get('overall_score')}",
            f"   Recommendation: {job.get('recommendation','')}",
            f"   Apply: {job['job_url']}",
            f"   Missing: {', '.join(job.get('missing_skills', [])) or 'None identified'}", "",
        ])
    if result["new_relevant_jobs"] < result["target_count"]:
        lines.append("No old jobs were added just to reach the target. Run the collector again later when fresh postings are available.")
    return "\n".join(lines)
