import json
from typing import Dict, Optional


class ReplayDetector:
    """
    Aynı CP için kısa süre içinde birebir aynı event yeniden gelirse
    replay attack olarak işaretler.
    """
    anomaly_type = "REPLAY"

    def __init__(self, window_seconds: int = 60) -> None:
        # {cp_id: {payload_hash: timestamp}}
        self.history: Dict[str, Dict[int, float]] = {}
        self.window = window_seconds

    def process(self, event: Dict) -> Optional[Dict]:
        cp = event["cp_id"]
        ts = event["timestamp"]
        
        # Sadece hash değil, zaman bazlı kontrol
        msg_hash = hash(json.dumps(event.get("payload") or {}, sort_keys=True))
        
        cp_history = self.history.setdefault(cp, {})
        
        # Eski kayıtları temizle
        self.history[cp] = {h: t for h, t in cp_history.items() if (ts - t) < self.window}
        
        if msg_hash in self.history[cp]:
            return {
                "anomaly_type": self.anomaly_type,
                "cp_id": cp,
                "severity": "HIGH",
                "details": {
                    "reason": f"Exact payload replayed within {self.window}s",
                    "hash": msg_hash
                },
                "timestamp": ts
            }

        self.history[cp][msg_hash] = ts
        return None
