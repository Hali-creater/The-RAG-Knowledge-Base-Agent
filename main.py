import logging
from scheduler import start_scheduler
from dashboard import run_dashboard
from database import init_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing Multi-Source Real Estate Lead Intelligence System...")
    init_db()

    # Start Scheduler
    scheduler = start_scheduler()

    # Run Dashboard
    logger.info("Dashboard available at http://localhost:8000")
    try:
        run_dashboard()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        scheduler.shutdown()

if __name__ == "__main__":
    main()
