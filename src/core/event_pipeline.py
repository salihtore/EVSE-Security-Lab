import json
import os
import time
from typing import Any, Dict, Optional

from src.utils.logger import logger

LOG_DIR = "logs"
EVENT_LOG = os.path.join(LOG_DIR, "events.jsonl")


class EventPipeline:
    """
    CSMS içindeki tüm OCPP handler'ları bu sınıf üzerinden
    event oluşturup loglayacak.
    """

    def __init__(self) -> None:
        os.makedirs(LOG_DIR, exist_ok=True)

    def build_event(
        self,
        cp_id: str,
        message_type: str,
        payload: Dict[str, Any],
        scenario_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        OCPP payload -> normalize edilmiş event dict
        """
        event: Dict[str, Any] = {
            "timestamp": time.time(),
            "cp_id": cp_id or "unknown",
            "message_type": message_type,
            "scenario_name": scenario_name,
            "session_active": True,
            "transaction_id": self._extract_transaction_id(payload),
            "meter_value": self._extract_meter_value(payload),
            "idTag": self._extract_id_tag(payload),
            "extra": payload,
        }

        logger.info(
            f"[EVENT] {event['cp_id']} - {event['message_type']} "
            f"(tx={event['transaction_id']}, idTag={event['idTag']})"
        )
        return event

    # ✨ NEW FUNCTION — Standart Security Event JSON formatı
    def build_security_event(
        self,
        cp_id: str,
        anomaly_type: str,
        severity: str,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AnomalyEngine için standart güvenlik event formatı.

        Bu format dashboard backend, SIEM integrasyonu ve log tutarlılığı için zorunludur.
        """
        return {
            "event_id": str(int(time.time() * 1000)),  # hızlı uuid benzeri
            "timestamp": time.time(),
            "cp_id": cp_id,
            "event_type": "ANOMALY",
            "anomaly_type": anomaly_type,
            "severity": severity,
            "details": details,
            "meta": {
                "source": "AnomalyEngine",
                "version": "1.0"
            }
        }

    def emit_event(self, event: Dict[str, Any]) -> None:
        """
        Event'i kalıcı loga yaz.
        Dashboard & ML buradan okuyacak.
        """
        try:
            with open(EVENT_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        except Exception as exc:
            logger.error(f"[EVENT_PIPELINE] Event yazılırken hata: {exc}")

    # ---- Payload yardımcıları ----

    def _extract_transaction_id(self, payload: Dict[str, Any]) -> Optional[int]:
        if not isinstance(payload, dict):
            return None
        return payload.get("transactionId")

    def _extract_meter_value(self, payload: Dict[str, Any]) -> Optional[float]:
        """
        MeterValues formatına göre Wh değerini çekmeye çalışır.
        """
        try:
            mv_list = payload.get("meterValue") or []
            if not mv_list:
                return None
            sampled = mv_list[0].get("sampledValue") or []
            if not sampled:
                return None
            value_str = sampled[0].get("value")
            if value_str is None:
                return None
            return float(value_str)
        except Exception:
            return None

    def _extract_id_tag(self, payload: Dict[str, Any]) -> Optional[str]:
        if not isinstance(payload, dict):
            return None
        # StartTransaction veya Authorize için
        return payload.get("idTag")
