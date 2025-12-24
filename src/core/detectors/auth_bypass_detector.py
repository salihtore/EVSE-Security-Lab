from typing import Dict, Optional


class AuthBypassDetector:
    """
    StartTransaction öncesinde yakın zamanda Authorize gelmemişse
    Authentication Bypass olarak işaretler.
    """
    anomaly_type = "AUTH_BYPASS"

    def __init__(self, max_auth_age: int = 30) -> None:
        self.last_authorize: Dict[str, float] = {}
        self.max_auth_age = max_auth_age

    def process(self, event: Dict) -> Optional[Dict]:
        cp = event["cp_id"]
        msg = event["message_type"]
        ts = event["timestamp"]

        if msg == "Authorize":
            self.last_authorize[cp] = ts
            return None

        if msg == "StartTransaction":
            last_auth = self.last_authorize.get(cp)
            if last_auth is None or (ts - last_auth) > self.max_auth_age:
               return {
                    "anomaly_type": self.anomaly_type,
                    "cp_id": cp,
                    "severity": "HIGH",
                    "details": {
                        "reason": "StartTransaction without fresh Authorize",
                        "last_authorize": last_auth,
            },
            "timestamp": ts
            }
        return None
