import logging

import numpy as np

from db import get_connection
from services.trainer import METRICS, load_model

logger = logging.getLogger(__name__)

def score_recent_readings(minutes: int = 2) -> int:
    conn = get_connection()
    anomaly_count = 0

    try:
        for metric in METRICS:
            model = load_model(metric)
            if model is None:
                continue

            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT time, device_id,
                           value,
                           EXTRACT(HOUR FROM time)::float AS hour,
                           EXTRACT(DOW  FROM time)::float AS dow
                    FROM sensor_readings
                    WHERE metric = %s
                      AND time >= NOW() - INTERVAL '%s minutes'
                    ORDER BY time
                    """,
                    [metric, minutes],
                )
                rows = cur.fetchall()

            if not rows:
                continue

            times      = [r[0] for r in rows]
            device_ids = [r[1] for r in rows]
            X = np.array([[r[2], r[3], r[4]] for r in rows], dtype=float)

            preds = model.predict(X)

            anomalous = [
                (t, did)
                for t, did, pred in zip(times, device_ids, preds)
                if pred == -1
            ]

            if anomalous:
                with conn.cursor() as cur:
                    cur.executemany(
                        """
                        UPDATE sensor_readings
                           SET anomaly = TRUE
                         WHERE time = %s AND device_id = %s AND metric = %s
                        """,
                        [(t, did, metric) for t, did in anomalous],
                    )
                conn.commit()
                anomaly_count += len(anomalous)
                logger.debug(
                    "Flagged %d anomalies for metric=%s", len(anomalous), metric
                )

    except Exception as exc:
        logger.error("scorer error: %s", exc)
        conn.rollback()
    finally:
        conn.close()

    return anomaly_count
