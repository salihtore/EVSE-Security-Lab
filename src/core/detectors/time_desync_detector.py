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

    def __init__(self, max_skew_seconds: int = 300) -> None:
        self.max_skew = max_skew_seconds

    def process(self, event: Dict) -> Optional[Dict]:
        cp = event.get("cp_id")
        payload = event.get("payload", {}) or {}

        # Öncelik sırası: CP'nin kendi zaman damgası > CSMS'in verdiği zaman > Ham log zamanı
        event_ts = (
            payload.get("cp_timestamp")
            or payload.get("csms_time")
            or event.get("timestamp")
        )

        if event_ts is None:
            return None

        now = time.time()
        skew = abs(now - event_ts)

        if skew > self.max_skew:
            return {
                "anomaly_type": self.anomaly_type,
                "cp_id": cp,
                "severity": "MEDIUM",
                "details": {
                    "reason": f"Clock skew exceeded limits ({int(skew)}s)",
                    "skew_seconds": int(skew),
                    "cp_time": event_ts,
                    "server_time": now
                },
                "timestamp": now
            }
        return None
