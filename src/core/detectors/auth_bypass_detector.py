from typing import Dict, Optional


class AuthBypassDetector:
    """
    StartTransaction öncesinde yakın zamanda Authorize gelmemişse
    veya idTag uyuşmuyorsa Authentication Bypass olarak işaretler.
    """
    anomaly_type = "AUTH_BYPASS"

    def __init__(self, max_auth_age: int = 30) -> None:
        self.last_auth_data: Dict[str, Dict] = {}
        self.max_auth_age = max_auth_age

    def process(self, event: Dict) -> Optional[Dict]:
        cp = event["cp_id"]
        msg = event["message_type"]
        ts = event["timestamp"]
        payload = event.get("payload", {}) or {}
        id_tag = payload.get("idTag") or event.get("idTag")

        if msg == "Authorize":
            self.last_auth_data[cp] = {
                "timestamp": ts,
                "idTag": id_tag
            }
            return None

        if msg == "StartTransaction":
            last_auth = self.last_auth_data.get(cp)
            
            reason = None
            if last_auth is None:
                reason = "StartTransaction without any previous Authorize"
            elif (ts - last_auth["timestamp"]) > self.max_auth_age:
                reason = f"Authorize expired ({int(ts - last_auth['timestamp'])}s ago)"
            elif last_auth["idTag"] != id_tag:
                reason = f"idTag mismatch: auth={last_auth['idTag']}, tx={id_tag}"
            elif id_tag is None:
                reason = "StartTransaction with NULL idTag"

            if reason:
                return {
                    "anomaly_type": self.anomaly_type,
                    "cp_id": cp,
                    "severity": "HIGH",
                    "details": {
                        "reason": reason,
                        "current_idTag": id_tag,
                        "last_auth": last_auth,
                    },
                    "timestamp": ts
                }
        return None
