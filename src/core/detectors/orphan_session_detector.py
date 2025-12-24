from typing import Dict, Optional

class SemihOrphanSessionDetector:
    anomaly_type = "ORPHAN_SESSION"

    def process(self, event: Dict) -> Optional[Dict]:
        # Örnek: StopTransaction gelmeden bağlantı koptuysa
        if event.get("event") == "CONNECTION_LOST" and event.get("session_active"):
            return {
                "anomaly_type": self.anomaly_type,
                "cp_id": event["cp_id"],
                "severity": "medium",
                "details": {
                    "reason": "Session active but connection lost",
                    "transaction_id": event.get("transaction_id")
                }
            }

        return None
