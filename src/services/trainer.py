import logging
import os

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

from db import get_connection

logger = logging.getLogger(__name__)

MODELS_DIR = "/app/models"
METRICS = ["temperature", "vibration", "rpm", "brake-pressure", "load-weight"]
MIN_SAMPLES = 100
TRAINING_LIMIT = 10_000

def model_path(metric: str) -> str:
    return os.path.join(MODELS_DIR, f"{metric.replace('-', '_')}.joblib")

def train_metric(metric: str) -> bool:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT value,
                       EXTRACT(HOUR FROM time)::float AS hour,
                       EXTRACT(DOW  FROM time)::float AS dow
                FROM sensor_readings
                WHERE metric = %s
                ORDER BY time DESC
                LIMIT %s
                """,
                [metric, TRAINING_LIMIT],
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    if len(rows) < MIN_SAMPLES:
        logger.info(
            "Skipping %s: only %d samples (need %d)", metric, len(rows), MIN_SAMPLES
        )
        return False

    X = np.array(rows, dtype=float)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X)

    os.makedirs(MODELS_DIR, exist_ok=True)
    path = model_path(metric)
    joblib.dump(model, path)
    logger.info("Model saved: %s  (trained on %d samples)", path, len(rows))
    return True

def train_all() -> dict[str, bool]:
    results = {}
    for metric in METRICS:
        try:
            results[metric] = train_metric(metric)
        except Exception as exc:
            logger.error("Training failed for %s: %s", metric, exc)
            results[metric] = False
    return results

def load_model(metric: str):
    path = model_path(metric)
    if not os.path.exists(path):
        return None
    return joblib.load(path)
