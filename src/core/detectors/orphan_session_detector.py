from typing import Dict, Optional


class OrphanSessionDetector:
    """
    StopTransaction geldiğinde o CP için aktif oturum yoksa / idTag yoksa
    'Yetim seans' olarak işaretler.
    """
    anomaly_type = "ORPHAN_SESSION"

    def __init__(self) -> None:
        self.active_sessions: Dict[str, bool] = {}

    def process(self, event: Dict) -> Optional[Dict]:
        cp = event["cp_id"]
        msg = event["message_type"]

        if msg == "StartTransaction":
            self.active_sessions[cp] = True
            return None

        if msg == "StopTransaction":
            active = self.active_sessions.get(cp, False)
            id_tag = event.get("idTag")

            # Session yok veya idTag yok → anomaly
            if not active or not id_tag:
                return {
                    "anomaly_type": self.anomaly_type,
                    "cp_id": cp,
                    "severity": "medium",
                    "details": {
                        "reason": "StopTransaction without proper StartTransaction or idTag",
                        "idTag": id_tag,
                    },
                }

            # normal bitiş
            self.active_sessions[cp] = False

        return None
