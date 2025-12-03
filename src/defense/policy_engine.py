from typing import Dict

from src.utils.logger import logger


class PolicyEngine:
    """
    IDS/IPS davranışlarını buraya koyacaksın.
    Şimdilik sadece log atıyor.
    """

    def handle_alarm(self, alarm: Dict) -> None:
        severity = alarm.get("severity", "low")
        cp_id = alarm.get("cp_id", "unknown")

        if severity == "high":
            logger.warning(f"[POLICY] YÜKSEK RİSK! CP={cp_id} için müdahale gerekli: {alarm}")
            # TODO: RemoteStopTransaction veya benzeri aksiyonlar
        else:
            logger.info(f"[POLICY] Alarm kaydedildi: {alarm}")
