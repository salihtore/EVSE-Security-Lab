from typing import Dict, Optional

class OrphanSessionDetector:
    """
    Araç fişten çekildikten sonra 30 saniye içinde StopTransaction gelmezse
    'Yetim Seans' olarak işaretler.
    """
    anomaly_type = "ORPHAN_SESSION"

    def __init__(self, timeout: int = 30) -> None:
        self.unplug_times: Dict[str, float] = {} # {cp_id: timestamp}
        self.timeout = timeout

    def process(self, event: Dict) -> Optional[Dict]:
        cp = event["cp_id"]
        ts = event["timestamp"]
        msg = event["message_type"]
        payload = event.get("payload", {}) or {}
        
        # 1. Fiş çekilme anını yakala
        if payload.get("plug_state") is False:
            if cp not in self.unplug_times:
                self.unplug_times[cp] = ts
        elif payload.get("plug_state") is True:
            self.unplug_times.pop(cp, None)

        # 2. Eğer fiş çekiliyse ve süre geçtiyse
        if cp in self.unplug_times:
            # Eğer hala seans aktifse kontrolü (bu state gerektirir ama biz zaman farkına bakıyoruz)
            # Normalde StopTransaction gelince bu record silinmeli
            if msg == "StopTransaction":
                self.unplug_times.pop(cp, None)
                return None
            
            diff = ts - self.unplug_times[cp]
            if diff > self.timeout:
                return {
                    "anomaly_type": self.anomaly_type,
                    "cp_id": cp,
                    "severity": "HIGH",
                    "details": {
                        "reason": f"No StopTransaction received {int(diff)}s after unplugging",
                        "unplug_time": self.unplug_times[cp]
                    },
                    "timestamp": ts
                }

        return None
