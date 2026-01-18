from typing import Dict, Optional


class ZeroEnergyDetector:
    """
    Sürekli 0 enerji raporlanıyorsa (Zero Energy Flood senaryosu)
    veya 'Charging' durumunda enerji artmıyorsa anomali olarak işaretler.
    """
    anomaly_type = "ZERO_ENERGY_FLOOD"

    def __init__(self, threshold: int = 5) -> None:
        self.zero_counts: Dict[str, int] = {}
        self.threshold = threshold

    def process(self, event: Dict) -> Optional[Dict]:
        cp = event["cp_id"]
        msg = event["message_type"]
        payload = event.get("payload", {}) or {}
        
        # Basit "0.0" kontrolü yerine "Charging" statüsü ile korelasyon
        status = payload.get("status") or event.get("status")
        mv = event.get("meter_value")
        
        if msg == "MeterValues":
            # Eğer şarj ediliyor görünüyor ama 0 veya artmayan değer geliyorsa
            if status == "Charging" and (mv is None or mv == 0.0):
                self.zero_counts[cp] = self.zero_counts.get(cp, 0) + 1
            else:
                self.zero_counts[cp] = 0

            if self.zero_counts[cp] >= self.threshold:
                return {
                    "anomaly_type": self.anomaly_type,
                    "cp_id": cp,
                    "severity": "HIGH",
                    "details": {
                        "reason": f"Charging status with {self.zero_counts[cp]} consecutive zero meter values",
                        "status": status,
                    },
                    "timestamp": event["timestamp"]
                }

        return None
