from typing import Dict, Optional


class ThermalManipulationDetector:
    """
    Payload içinde 'temperature_override' benzeri alanlar varsa
    sensör manipülasyonu olarak işaretler.
    """
    anomaly_type = "THERMAL_MANIPULATION"

    def process(self, event: Dict) -> Optional[Dict]:
        extra = event.get("extra") or {}

        if isinstance(extra, dict) and extra.get("temperature_override") is True:
            return {
                "anomaly_type": self.anomaly_type,
                "cp_id": event["cp_id"],
                "severity": "high",
                "details": {"reason": "Temperature override flag set"},
            }

        return None
