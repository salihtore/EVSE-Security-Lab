from typing import Dict, Optional
import time


class TimeDesyncDetector:
    """
    Event timestamp ile sistem zamanı arasında büyük fark varsa
    zaman senkronizasyonu problemi olarak işaretler.
    """
    anomaly_type = "TIME_DESYNC"

    def __init__(self, max_skew_seconds: int = 60) -> None:
        self.max_skew = max_skew_seconds

    def process(self, event: Dict) -> Optional[Dict]:
        now = time.time()
        skew = abs(now - event["timestamp"])

        if skew > self.max_skew:
            return {
                "anomaly_type": self.anomaly_type,
                "cp_id": event["cp_id"],
                "severity": "medium",
                "details": {"skew_seconds": skew},
            }

        return None
