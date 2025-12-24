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
    ):
        self.cp_id = cp_id
        self.scenario_name = scenario_name
        self.anomaly_engine = anomaly_engine or AnomalyEngine()

    # -------------------------------------------------
    # NORMAL EVENT
    # -------------------------------------------------
    def emit(
        self,
        message_type: str,
        payload: Dict[str, Any],
    ) -> List[Dict]:
        event = event_pipeline.build_event(
            cp_id=self.cp_id,
            message_type=message_type,
            payload=payload,
            scenario_name=self.scenario_name,
        )

        # Event log
        event_pipeline.emit_event(event)

        # Anomaly detection
        alarms = self.anomaly_engine.process(event)

        if alarms:
            logger.warning(
                f"[ScenarioAdapter] {len(alarms)} alarm üretildi"
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
        security_event = event_pipeline.build_security_event(
            cp_id=self.cp_id,
            anomaly_type=anomaly_type,
            severity=severity,
            details=details,
        )

        event_pipeline.emit_event(security_event)

        logger.warning(
            f"[ScenarioAdapter] MANUAL ALARM → {anomaly_type} ({severity})"
        )
