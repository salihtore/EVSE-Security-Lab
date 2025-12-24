# src/core/detectors/time_desync_detector.py
from typing import Dict, Optional
import time
import logging


class TimeDesyncDetector:
    """
    Event timestamp ile sistem zamanı arasında büyük fark varsa
    zaman senkronizasyonu problemi olarak işaretler.
    """
    anomaly_type = "TIME_DESYNC"

    def __init__(self, max_skew_seconds: int = 60) -> None:
        self.max_skew = max_skew_seconds

    def process(self, event: Dict) -> Optional[Dict]:
        
        # 1️⃣ Timestamp kaynağını güvenli seç

        payload = event.get("payload", {}) or {}

        event_ts = (
            payload.get("cp_timestamp")
            or payload.get("csms_time")
            or event.get("timestamp")
        )


        if event_ts is None:
            logging.warning("[TimeDesyncDetector] Event timestamp yok, atlandı")
            return None

        now = time.time()
        skew = abs(now - event_ts)

        # 2️⃣ Debug log (kritik)
        logging.debug(
            f"[TimeDesyncDetector] CP={event.get('cp_id')} skew={skew:.2f}s"
        )

        if skew > self.max_skew:
            # 3️⃣ ANA MOTORLA UYUMLU ALARM FORMAT
            return {
                "anomaly_type": self.anomaly_type,
                "cp_id": event.get("cp_id"),
                "severity": "MEDIUM",
                "details": {
                    "message": f"Time desync detected (skew={int(skew)}s)",
                    "skew_seconds": int(skew),
                    "event": event,
                }
        }
        return None
