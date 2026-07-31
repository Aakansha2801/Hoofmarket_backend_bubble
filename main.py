# main.py
# Usage:
#   python main.py          → scheduled mode (30 min test / 8 h prod)
#   python main.py --once   → single run then exit
#
# Override interval at runtime:
#   SCRAPE_INTERVAL_HOURS=4 python main.py

import asyncio
import logging
import os
import sys
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from orchestrator import run_all_scrapers
from config.base import TESTING_MODE, SCRAPE_INTERVAL_HOURS

# ── Logging ───────────────────────────────────────────────────
# LOG_DIR env var can be set by the process manager to redirect logs
# to a specific path. Falls back to ./logs for local dev. If the
# configured path is not writable, we silently fall back to ./logs
# instead of crashing.
_log_dir_env = os.getenv("LOG_DIR", "")
if _log_dir_env:
    log_dir = Path(_log_dir_env)
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except (PermissionError, FileNotFoundError):
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)
else:
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / "hoofmarket.log"),
    ],
)
logger = logging.getLogger(__name__)


def run_job():
    logger.info("🚀 Job started")
    scraped = asyncio.run(run_all_scrapers())
    logger.info(f"🏁 Job complete — scraped={scraped}")


def start_scheduler():
    # SCRAPE_INTERVAL_HOURS comes from config.base — env override wins,
    # otherwise 0.5h in TESTING_MODE and 8h in production.
    hours = SCRAPE_INTERVAL_HOURS
    trigger = IntervalTrigger(hours=hours)
    if TESTING_MODE:
        logger.info(f"⏰ Scheduler: every {hours} h (TESTING_MODE)")
    else:
        logger.info(f"⏰ Scheduler: every {hours} h (PRODUCTION)")

    scheduler = BlockingScheduler(timezone="America/Chicago")
    scheduler.add_job(run_job, trigger, id="scrape_job", max_instances=1)

    logger.info("▶️  Running first job immediately...")
    run_job()

    logger.info("⏳ Scheduler running — Ctrl+C to stop")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Scheduler stopped")


if __name__ == "__main__":
    if "--once" in sys.argv:
        run_job()
    else:
        start_scheduler()
