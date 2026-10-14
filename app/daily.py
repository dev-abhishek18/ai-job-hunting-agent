from datetime import datetime, timezone

from .filters import fresh_and_relevant, basic_relevance, experience_relevant
from .repository import upsert_job, save_match
from .matching import score_job
from .candidate import CANDIDATE
from .profile_repository import attach_job


def _freshness_tier(job):
    source = str(job.get("source", "")).lower()
    if source.startswith(("greenhouse:", "lever:", "ashby:")):
        return "VERIFIED_FRESH"
    return "LIKELY_FRESH"


def collect_daily(collectors: list, target_count: int = 20, candidate: dict | None = None, candidate_id: int | None = None):
    merged_candidate = dict(CANDIDATE)
    if candidate:
        merged_candidate.update(candidate)
    candidate = merged_candidate

    seen_in_run = set()
    inserted = duplicates = rejected = 0
    attached = 0
    source_errors = []
    run_jobs = []
    date_unconfirmed_leads = []

    for collector in collectors:
        try:
            collected = collector.collect()
        except Exception as exc:
            source_errors.append({"source": collector.__class__.__name__, "error": str(exc)})
            continue

        for job in collected:
            # Keep relevant undated listings as explicitly unconfirmed leads, never as fresh jobs.
            if not job.get("posted_at"):
                if basic_relevance(job, candidate) and experience_relevant(job, candidate) and job.get("job_url"):
                    lead = dict(job)
                    lead["freshness_tier"] = "DATE_UNCONFIRMED"
                    if not any(x.get("job_url") == lead.get("job_url") for x in date_unconfirmed_leads):
                        date_unconfirmed_leads.append(lead)
                else:
                    rejected += 1
                continue

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
                was_attached, _status = attach_job(candidate_id, row["id"])
                if was_attached:
                    attached += 1
                else:
                    duplicates += 1
                    continue
            elif not is_new:
                duplicates += 1
                continue

            if is_new:
                inserted += 1
            item = dict(row)
            item.update(result)
            item["freshness_tier"] = _freshness_tier(job)
            item["matched_skills"] = result["matched_skills"]
            item["missing_skills"] = result["missing_skills"]
            item["overall_score"] = result["overall_score"]
            item["requisition_id"] = job.get("requisition_id")
            run_jobs.append(item)

    run_jobs.sort(key=lambda item: item.get("overall_score", 0), reverse=True)
    return {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "target_count": target_count,
        "new_relevant_jobs": min(len(run_jobs), target_count),
        "inserted_new_jobs": inserted,
        "candidate_new_jobs": attached,
        "duplicates_skipped": duplicates,
        "not_fresh_or_relevant": rejected,
        "source_errors": source_errors,
        "jobs": run_jobs[:target_count],
        "date_unconfirmed_leads": date_unconfirmed_leads[:target_count],
        "note": "Fresh jobs are limited to the rolling 48-hour window. ATS-dated postings are marked VERIFIED_FRESH; aggregator-dated postings are LIKELY_FRESH. Undated relevant listings appear separately as DATE_UNCONFIRMED and are not counted as fresh. Previously stored jobs are not re-reported as new.",
    }
