from app.database import init_db
from app.daily import collect_daily
from app.daily_config import configured_collectors
from app.report import make_daily_report

if __name__ == "__main__":
    init_db()
    result = collect_daily(configured_collectors(), target_count=10)
    print(make_daily_report(result))
