import threading
import time
import logging
from scheduler import start_scheduler
from dashboard import run_dashboard
from database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing Real Estate AI Lead Intelligence System...")

    # Initialize Database
    init_db()

    # Start Scheduler in a background thread
    logger.info("Starting background scheduler...")
    scheduler = start_scheduler()

    # Run Dashboard in the main thread
    logger.info("Starting web dashboard on http://localhost:8000")
    try:
        run_dashboard()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        scheduler.shutdown()

if __name__ == "__main__":
    main()
