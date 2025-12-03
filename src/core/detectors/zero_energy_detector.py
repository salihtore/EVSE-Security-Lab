from typing import Dict, Optional


class ZeroEnergyDetector:
    """
    Sürekli 0 enerji raporlanıyorsa (Zero Energy Flood senaryosu),
    anomali olarak işaretler.
    """
    anomaly_type = "ZERO_ENERGY_FLOOD"

    def __init__(self, threshold_count: int = 5) -> None:
        self.zero_counts: Dict[str, int] = {}
        self.threshold = threshold_count

    def process(self, event: Dict) -> Optional[Dict]:
        if event["message_type"] != "MeterValues":
            return None

        cp = event["cp_id"]
        mv = event.get("meter_value")

        if mv == 0.0:
            self.zero_counts[cp] = self.zero_counts.get(cp, 0) + 1
        else:
            self.zero_counts[cp] = 0

        if self.zero_counts[cp] >= self.threshold:
            return {
                "anomaly_type": self.anomaly_type,
                "cp_id": cp,
                "severity": "medium",
                "details": {
                    "reason": "Consecutive zero MeterValues",
                    "count": self.zero_counts[cp],
                },
            }

        return None
