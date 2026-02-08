import logging
import signal
import sys
import time

from src.config import CHECK_INTERVAL, SEARCH_AREAS
from src.scraper import Job, scrape_jobs
from src.discord_notifier import send_job_alert

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Track jobs we've already notified about so we only alert on new ones.
seen_jobs: set[Job] = set()

running = True


def _handle_signal(signum, frame):
    global running
    logger.info("Received signal %s — shutting down", signum)
    running = False


signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)


def run_once() -> int:
    """Run a single scrape cycle. Returns count of new jobs found."""
    global seen_jobs

    logger.info("Starting scrape cycle for areas: %s", SEARCH_AREAS)
    result = scrape_jobs(SEARCH_AREAS)

    if result.error:
        logger.error("Scrape failed: %s", result.error)
        return 0

    if not result.jobs:
        logger.info("No jobs found this cycle")
        return 0

    new_jobs = [j for j in result.jobs if j not in seen_jobs]

    if new_jobs:
        logger.info("Found %d new job(s) (total scraped: %d)", len(new_jobs), len(result.jobs))
        send_job_alert(new_jobs, SEARCH_AREAS)
        seen_jobs.update(new_jobs)
    else:
        logger.info("No new jobs (all %d already seen)", len(result.jobs))

    return len(new_jobs)


def main():
    logger.info(
        "amzpydis starting — monitoring areas: %s, interval: %ds",
        SEARCH_AREAS,
        CHECK_INTERVAL,
    )

    while running:
        run_once()

        logger.info("Sleeping %ds until next check...", CHECK_INTERVAL)
        # Sleep in short intervals so we respond to signals promptly
        elapsed = 0
        while elapsed < CHECK_INTERVAL and running:
            time.sleep(min(5, CHECK_INTERVAL - elapsed))
            elapsed += 5

    logger.info("Shutdown complete")


if __name__ == "__main__":
    main()
