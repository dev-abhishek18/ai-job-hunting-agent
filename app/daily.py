from datetime import datetime, timezone

from .filters import fresh_and_relevant
from .repository import upsert_job, save_match, get_new_jobs
from .matching import score_job
from .candidate import CANDIDATE
from .profile_repository import attach_job


def collect_daily(collectors: list, target_count: int = 10, candidate: dict | None = None, candidate_id: int | None = None):
    candidate = candidate or CANDIDATE
    seen_in_run = set()
    inserted = duplicates = rejected = 0
    attached = 0
    source_errors = []

    for collector in collectors:
        try:
            collected = collector.collect()
        except Exception as exc:
            source_errors.append({"source": collector.__class__.__name__, "error": str(exc)})
            continue

        for job in collected:
            if not fresh_and_relevant(job, candidate=candidate):
                rejected += 1
                continue

            url = job.get("job_url", "").strip().lower()
            if url and url in seen_in_run:
                duplicates += 1
                continue
            if url:
                seen_in_run.add(url)

            row, is_new = upsert_job(job)
            result = score_job(job, candidate)
            save_match(row["id"], result)

            if candidate_id is not None:
                was_attached, status = attach_job(candidate_id, row["id"])
                if was_attached:
                    attached += 1
                else:
                    duplicates += 1
            elif not is_new:
                duplicates += 1

            if is_new:
                inserted += 1

    new_jobs = get_new_jobs(max(target_count, 50), candidate_id=candidate_id)
    return {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "target_count": target_count,
        "new_relevant_jobs": min(len(new_jobs), target_count),
        "inserted_new_jobs": inserted,
        "candidate_new_jobs": attached,
        "duplicates_skipped": duplicates,
        "not_fresh_or_relevant": rejected,
        "source_errors": source_errors,
        "jobs": new_jobs[:target_count],
        "note": "Only new jobs posted in the last 24 hours and matching the configured role/location/experience preference are returned. Old jobs are never used to fill the target.",
    }
