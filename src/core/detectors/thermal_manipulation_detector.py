from typing import Dict, Optional

class ThermalManipulationDetector:
    anomaly_type = "THERMAL_MANIPULATION"

    def process(self, event: Dict) -> Optional[Dict]:
        # 🔴 PAYLOAD DEĞİL, DATA
        data = event.get("data") or {}

        if data.get("temperature_override") is True:
            return {
                "anomaly_type": self.anomaly_type,
                "cp_id": event.get("cp_id"),
                "severity": "HIGH",
                "details": {
                    "reason": data.get("reason"),
                    "temperature": data.get("temperature"),
                    "transaction_id": data.get("transaction_id"),
                    "scenario": event.get("scenario"),
                },
            }

        return None
