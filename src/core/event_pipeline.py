#event_pipeline.py
import json
import os
import time
from typing import Any, Dict, Optional

from src.utils.logger import logger

LOG_DIR = "logs"
EVENT_LOG = os.path.join(LOG_DIR, "events.jsonl")
ALARM_LOG = os.path.join(LOG_DIR, "alarms.jsonl")


class EventPipeline:
    """
    EVENT ve ALARM üreten TEK BORU HATTI.

    - UI events.jsonl ve alarms.jsonl okur
    - Senaryo bu sınıfa DOĞRUDAN yazmaz
    """

    def __init__(self) -> None:
        os.makedirs(LOG_DIR, exist_ok=True)

        # Dosyalar yoksa oluştur
        for path in (EVENT_LOG, ALARM_LOG):
            if not os.path.exists(path):
                open(path, "w", encoding="utf-8").close()

    # -------------------------------------------------
    # NORMAL EVENT
    # -------------------------------------------------
    def build_event(
        self,
        cp_id: str,
        message_type: str,
        payload: Dict[str, Any],
        scenario_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        event: Dict[str, Any] = {
            "timestamp": time.time(),
            "cp_id": cp_id,
            "scenario_name": scenario_name,
            "event_type": "EVENT",
            "message_type": message_type,
            "transaction_id": payload.get("transactionId"),
            "idTag": payload.get("idTag"),
            "payload": payload,
        }

        logger.info(
            f"[EVENT] {event['cp_id']} - {event['message_type']} "
            f"(tx={event['transaction_id']}, idTag={event['idTag']})"
        )
        return event

    # -------------------------------------------------
    # SECURITY EVENT (UI'YA GİDEN ALARM)
    # -------------------------------------------------
    def build_security_event(
        self,
        cp_id: str,
        anomaly_type: str,
        severity: str,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "event_id": str(int(time.time() * 1000)),
            "timestamp": time.time(),
            "cp_id": cp_id,
            "event_type": "ANOMALY",
            "anomaly_type": anomaly_type,
            "severity": severity,
            "details": details,
        }

    # -------------------------------------------------
    # LOG YAZMA
    # -------------------------------------------------
    def emit_event(self, event: Dict[str, Any]) -> None:
        try:
            # Tüm event'ler
            with open(EVENT_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")

            # Sadece alarm'lar
            if event.get("event_type") == "ANOMALY":
                with open(ALARM_LOG, "a", encoding="utf-8") as af:
                    af.write(json.dumps(event, ensure_ascii=False) + "\n")

        except Exception as exc:
            logger.error(f"[EVENT_PIPELINE] Yazma hatası: {exc}")


# 🔴 PROJEDE TEK KULLANILACAK INSTANCE
event_pipeline = EventPipeline()
