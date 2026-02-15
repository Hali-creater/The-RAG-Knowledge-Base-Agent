from apscheduler.schedulers.background import BackgroundScheduler
from database import get_daily_summary, save_lead, init_db
from scraper import RealEstateScraper
from notifier import send_email_alert, send_daily_summary_report
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_scraper_job():
    logger.info("Running scheduled scraper job...")
    scraper = RealEstateScraper()
    leads = scraper.run()

    for lead in leads:
        save_lead(lead)
        if lead.get('lead_score', 0) > 80:
            logger.info(f"High priority lead found! Sending alert. Score: {lead['lead_score']}")
            send_email_alert(lead)

def run_daily_summary_job():
    logger.info("Running daily summary job...")
    summary = get_daily_summary()
    send_daily_summary_report(summary)

def start_scheduler():
    init_db()
    scheduler = BackgroundScheduler()

    # Run scraper every 30 minutes
    scheduler.add_job(run_scraper_job, 'interval', minutes=30)

    # Run daily summary every day at midnight
    scheduler.add_job(run_daily_summary_job, 'cron', hour=0, minute=0)

    # Run immediately once for testing
    scheduler.add_job(run_scraper_job)

    scheduler.start()
    logger.info("Scheduler started.")
    return scheduler

if __name__ == "__main__":
    import time
    start_scheduler()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pass
