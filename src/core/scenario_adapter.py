#scenario_adapter.py
from typing import Any, Dict, Optional, List
from src.core.event_pipeline import event_pipeline
from src.core.anomaly_engine import AnomalyEngine
from src.utils.logger import logger


class ScenarioAdapter:
    """
    SENARYO → CORE TEK GİRİŞ NOKTASI

    Senaryo:
      ❌ log yazmaz
      ❌ detector çağırmaz
      ❌ alarm formatlamaz

    Senaryo:
      ✅ adapter.emit()
      ✅ adapter.emit_alarm()
    """

    def __init__(
        self,
        cp_id: str,
        scenario_name: str,
        anomaly_engine: Optional[AnomalyEngine] = None,
        mode: str = "normal"
    ):
        self.cp_id = cp_id
        self.scenario_name = scenario_name
        self.anomaly_engine = anomaly_engine or AnomalyEngine()
        self.mode = mode.upper() # NORMAL / ATTACK

    # -------------------------------------------------
    # NORMAL EVENT
    # -------------------------------------------------
    def emit(
        self,
        message_type: str,
        payload: Dict[str, Any],
        override_cp_id: str = None
    ) -> List[Dict]:
        event = event_pipeline.build_event(
            cp_id=override_cp_id if override_cp_id else self.cp_id,
            message_type=message_type,
            payload=payload,
            scenario_name=self.scenario_name,
        )

        # 🏷️ Veri Seti İçin Etiketleme (Ground Truth)
        event["true_label"] = self.mode

        # Event log
        event_pipeline.emit_event(event)

        # Anomaly detection (Mod bilgisini ilet)
        alarms = self.anomaly_engine.process(event, mode=self.mode)

        if alarms:
            logger.warning(
                f"[ScenarioAdapter] {len(alarms)} alarm üretildi (Label: {self.mode})"
            )

        return alarms or []

    # -------------------------------------------------
    # MANUEL / KESİN ALARM
    # -------------------------------------------------
    def emit_alarm(
        self,
        anomaly_type: str,
        severity: str,
        details: Dict[str, Any],
    ) -> None:
        # 🛡️ IPS Katmanı: Müdahale aksiyonu belirle
        alarm_stub = {
            "cp_id": self.cp_id,
            "anomaly_type": anomaly_type,
            "severity": severity,
            "details": details,
            "timestamp": event_pipeline.build_security_event("stub", "stub", "LOW", {})["timestamp"] # zaman damgası al
        }
        
        # 🧠 ML Enrichment (Manuel Alarm için de skor üret)
        if self.anomaly_engine.ml_enricher:
            try:
                # Bağlam için yapay bir event oluştur
                dummy_event = {
                    "cp_id": self.cp_id,
                    "message_type": f"MANUAL_{anomaly_type}",
                    "timestamp": alarm_stub["timestamp"],
                    "transaction_id": details.get("transaction_id"),
                    "details": details
                }
                
                # State snapshot al
                snapshot = {}
                if self.anomaly_engine.state_buffer:
                    snapshot = self.anomaly_engine.state_buffer.snapshot(self.cp_id)

                # ML motorunu çağır ve alarm["ml"] alanını doldur
                alarm_stub = self.anomaly_engine.ml_enricher.enrich(
                    event=dummy_event,
                    alarm=alarm_stub,
                    state_snapshot=snapshot
                )
            except Exception as e:
                logger.error(f"[ScenarioAdapter] ML enrichment failed: {e}")
                alarm_stub["ml"] = {"score": None, "confidence": None, "model": None}
        else:
             alarm_stub["ml"] = {"score": None, "confidence": None, "model": None}
        
        # PolicyEngine üzerinden geçir
        mitigated_alarm = self.anomaly_engine.policy.handle_alarm(alarm_stub)
        
        security_event = event_pipeline.build_security_event(
            cp_id=self.cp_id,
            anomaly_type=anomaly_type,
            severity=severity,
            details={
                **details,
                "mitigation": mitigated_alarm.get("mitigation")
            },
        )

        # 🏷️ Veri Seti İçin Etiketleme (Manual Alarm durumunda zaten ATTACK bekliyoruz)
        security_event["true_label"] = self.mode

        event_pipeline.emit_event(security_event)

        logger.warning(
            f"[ScenarioAdapter] MANUAL ALARM + IPS → {anomaly_type} ({severity}) (Label: {self.mode})"
        )
