from typing import Dict, Optional


class PhantomCurrentDetector:
    """
    Fiilen şarj yokken / bağlantı kopukken sürekli ölçüm geliyorsa
    'hayalet akım' olarak işaretlenebilir.
    Burada basit bir placeholder kural var, senaryo detayına göre geliştirirsin.
    """
    anomaly_type = "PHANTOM_CURRENT"

    def process(self, event: Dict) -> Optional[Dict]:
        if event["message_type"] != "MeterValues":
            return None

        mv = event.get("meter_value")
        if mv is None:
            return None

        # Placeholder kural: çok küçük ama sürekli artan enerji olabilir.
        if 0 < mv < 1.0:
            return {
                "anomaly_type": self.anomaly_type,
                "cp_id": event["cp_id"],
                "severity": "low",
                "details": {"meter_value": mv},
            }

        return None
