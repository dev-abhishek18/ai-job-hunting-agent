"""Optional scheduler entry point.

For production, run this from cron, Windows Task Scheduler, GitHub Actions,
or a cloud scheduler. Do not depend on an in-process scheduler for a first
deployment because a web server restart would stop it.
"""
from .database import init_db
from .daily import collect_daily
from .collectors.json_feed import JsonFeedCollector
from .report import make_daily_report

def run():
    init_db()
    collectors = [JsonFeedCollector("data/job_feed.json", "permitted_json_feed")]
    result = collect_daily(collectors, target_count=10)
    print(make_daily_report(result))

if __name__ == "__main__":
    run()
