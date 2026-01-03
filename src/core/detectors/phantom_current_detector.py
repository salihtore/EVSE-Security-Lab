from typing import Dict, Optional


class PhantomCurrentDetector:
    """
    Araç fişten çekili görünürken sayaç değeri artıyorsa alarm üretir.
    """
    anomaly_type = "PHANTOM_CURRENT"

    def __init__(self) -> None:
        self.p_states: Dict[str, bool] = {} # {cp_id: plugged}
        self.last_kwh: Dict[str, float] = {}

    def process(self, event: Dict) -> Optional[Dict]:
        cp = event["cp_id"]
        msg = event["message_type"]
        payload = event.get("payload", {}) or {}
        
        # Plugged bilgisini takip et (StatusNotification veya MeterValues içinden)
        plugged = payload.get("plug_state")
        if plugged is not None:
            self.p_states[cp] = bool(plugged)

        if msg == "MeterValues":
            kwh = event.get("meter_value") or payload.get("meter_kWh")
            currently_plugged = self.p_states.get(cp, True) # Default true varsayalım
            
            last = self.last_kwh.get(cp)
            if last is not None and kwh is not None:
                # Fiş çekili ama enerji artıyor
                if not currently_plugged and kwh > last:
                    return {
                        "anomaly_type": self.anomaly_type,
                        "cp_id": cp,
                        "severity": "HIGH",
                        "details": {
                            "reason": "Energy consumption detected while UNPLUGGED",
                            "current_kwh": kwh,
                            "previous_kwh": last
                        },
                        "timestamp": event["timestamp"]
                    }
            
            if kwh is not None:
                self.last_kwh[cp] = kwh

        return None
