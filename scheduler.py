from apscheduler.schedulers.background import BackgroundScheduler
from database import save_lead, init_db
from scraper import RealEstateScraper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_scraper_job():
    logger.info("Running Multi-Source Real Estate Scraper Job...")
    scraper = RealEstateScraper()
    leads = scraper.run_all()

    for lead in leads:
        save_lead(lead)
    logger.info(f"Scheduled job completed. Found {len(leads)} potential leads.")

def start_scheduler():
    init_db()
    scheduler = BackgroundScheduler()

    # Run scraper every 30 minutes
    scheduler.add_job(run_scraper_job, 'interval', minutes=30)

    # Run immediately once
    scheduler.add_job(run_scraper_job)

    scheduler.start()
    logger.info("Automation Scheduler started.")
    return scheduler

if __name__ == "__main__":
    import time
    start_scheduler()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pass
