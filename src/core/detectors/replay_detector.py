from typing import Dict, Optional


class ReplayDetector:
    """
    Aynı CP için kısa süre içinde birebir aynı event yeniden gelirse
    basit bir replay göstergesi olarak işaretler.
    """
    anomaly_type = "REPLAY"

    def __init__(self, max_history: int = 1000) -> None:
        self.seen_hashes: Dict[str, set] = {}
        self.max_history = max_history

    def process(self, event: Dict) -> Optional[Dict]:
        cp = event["cp_id"]
        msg_hash = hash(
            (event["message_type"], event.get("transaction_id"), event.get("idTag"))
        )

        history = self.seen_hashes.setdefault(cp, set())

        if msg_hash in history:
            return {
                "anomaly_type": self.anomaly_type,
                "cp_id": cp,
                "severity": "high",
                "details": {
                    "reason": "Duplicate event signature detected for same CP",
                },
            }

        history.add(msg_hash)
        # Set büyümesin diye basit limit
        if len(history) > self.max_history:
            # Rastgele bir elemanı silebiliriz
            history.pop()

        return None
