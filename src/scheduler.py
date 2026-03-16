import logging

from apscheduler.schedulers.background import BackgroundScheduler

from services.scorer import score_recent_readings
from services.trainer import train_all

logger = logging.getLogger(__name__)

def _safe_train():
    try:
        train_all()
    except Exception as exc:
        logger.warning("Scheduled training failed (expected if DB has no data yet): %s", exc)

def _safe_score():
    try:
        count = score_recent_readings(minutes=2)
        if count:
            logger.info("ML scorer flagged %d anomalies", count)
    except Exception as exc:
        logger.warning("Scheduled scoring failed: %s", exc)

def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")

    scheduler.add_job(_safe_train, "interval", hours=6, id="retrain")

    scheduler.add_job(_safe_score, "interval", minutes=2, id="score")

    scheduler.start()
    logger.info("APScheduler started (retrain=6h, score=2m)")

    _safe_train()

    return scheduler
