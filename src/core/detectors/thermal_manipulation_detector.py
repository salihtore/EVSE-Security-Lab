from typing import Dict, Optional

class ThermalManipulationDetector:
    anomaly_type = "THERMAL_MANIPULATION"

    def __init__(self, max_gradient: float = 10.0) -> None:
        self.last_temps: Dict[str, Dict[str, float]] = {}
        self.max_gradient = max_gradient

    def process(self, event: Dict) -> Optional[Dict]:
        cp = event.get("cp_id")
        ts = event.get("timestamp")
        data = event.get("data") or {}
        
        # 1. Override Check (Existing logic)
        if data.get("temperature_override") is True:
            return {
                "anomaly_type": self.anomaly_type,
                "cp_id": cp,
                "severity": "HIGH",
                "details": {
                    "reason": data.get("reason") or "Direct temperature override detected",
                    "temperature": data.get("temperature"),
                },
            }

        # 2. Gradient Check (Proactive enhancement)
        temp = data.get("temperature")
        if temp is not None and cp:
            prev = self.last_temps.get(cp)
            if prev:
                dt = ts - prev["ts"]
                if dt > 0:
                    gradient = abs(temp - prev["temp"]) / dt
                    if gradient > self.max_gradient:
                        return {
                            "anomaly_type": self.anomaly_type,
                            "cp_id": cp,
                            "severity": "HIGH",
                            "details": {
                                "reason": f"Physically impossible temperature gradient: {gradient:.2f}°C/s",
                                "temp": temp,
                                "prev_temp": prev["temp"],
                                "delta_t": dt
                            },
                            "timestamp": ts
                        }
            self.last_temps[cp] = {"temp": temp, "ts": ts}

        return None
