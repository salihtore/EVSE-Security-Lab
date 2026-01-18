from typing import Dict, List
import os

from src.core.detectors.auth_bypass_detector import AuthBypassDetector
from src.core.detectors.orphan_session_detector import OrphanSessionDetector
from src.core.detectors.replay_detector import ReplayDetector
from src.core.detectors.phantom_current_detector import PhantomCurrentDetector
from src.core.detectors.zero_energy_detector import ZeroEnergyDetector
from src.core.detectors.time_desync_detector import TimeDesyncDetector
from src.core.detectors.thermal_manipulation_detector import ThermalManipulationDetector
from src.core.detectors.energy_mismatch_detector import EnergyMismatchDetector
from src.core.detectors.session_hijacking_detector import SessionHijackingDetector

from src.defense.policy_engine import PolicyEngine
from src.core.event_pipeline import event_pipeline
from src.utils.logger import logger
from Simulasyon.core.log_bundler import bundler

# ML (opsiyonel – yoksa sistem çalışmaya devam eder)
try:
    from src.core.ml.state_buffer import StateBuffer
except Exception:
    StateBuffer = None

try:
    from src.core.ml.ml_enricher import MLEnricher
except Exception as e:
    logger.error(f"ML IMPORT ERROR: {e}")
    MLEnricher = None


LOG_DIR = "logs"


class AnomalyEngine:
    """
    Rule-based anomaly detection engine.

    AŞAMA 1:
    - ML alarm üretmez.
    - ML enrichment tek noktadan yapılır: AnomalyEngine.process()
    """

    def __init__(self) -> None:
        self.policy = PolicyEngine()

        # Rule-based detector'lar
        self.detectors = [
            AuthBypassDetector(),
            OrphanSessionDetector(),
            ReplayDetector(),
            PhantomCurrentDetector(),
            ZeroEnergyDetector(),
            TimeDesyncDetector(),
            ThermalManipulationDetector(),
            EnergyMismatchDetector(),
            SessionHijackingDetector(),
        ]

        # Kısa süreli state (ML için)
        self.state_buffer = None
        if StateBuffer:
            try:
                self.state_buffer = StateBuffer()
            except Exception:
                self.state_buffer = None

        # ML enricher
        self.ml_enricher = None
        if MLEnricher:
            try:
                self.ml_enricher = MLEnricher()
            except Exception:
                self.ml_enricher = None

        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Start Bundler
        bundler.start()

    # -------------------------------------------------
    # EVENT PROCESS
    # -------------------------------------------------
    def process(self, event: Dict, mode: str = "NORMAL") -> List[Dict]:
        alarms: List[Dict] = []

        # 1) State update (ML context için)
        if self.state_buffer:
            try:
                self.state_buffer.update(event)
            except Exception:
                pass

        # 2) Rule-based detection
        for detector in self.detectors:
            try:
                alarm = detector.process(event)
            except Exception as exc:
                logger.error(f"[AnomalyEngine] {detector.__class__.__name__} hata: {exc}")
                continue

            if not alarm:
                continue

            # 3) AŞAMA 1: ML enrichment HER alarm için (central hook)
            # Contract: alarm["ml"] her zaman olacak (None olabilir)
            try:
                snapshot = self.state_buffer.snapshot(alarm.get("cp_id")) if self.state_buffer else {}
            except Exception:
                snapshot = {}

            if self.ml_enricher:
                try:
                    alarm = self.ml_enricher.enrich(
                        event=event,
                        alarm=alarm,
                        state_snapshot=snapshot,
                    )
                except Exception:
                    # Fail-safe: ml alanını yine garanti et
                    alarm["ml"] = {"score": None, "confidence": None, "model": None}
            else:
                alarm["ml"] = {"score": None, "confidence": None, "model": None}

            alarms.append(alarm)

            # 4) Defense policy (IPS katmanı - Müdahale kararını al)
            alarm = self.policy.handle_alarm(alarm)

            # 5) UI'ya giden security event
            sev = str(alarm.get("severity", "LOW")).upper()
            security_event = event_pipeline.build_security_event(
                cp_id=alarm["cp_id"],
                anomaly_type=alarm["anomaly_type"],
                severity=sev,
                details={
                    **alarm.get("details", {}),
                    "ml": alarm.get("ml"),
                    "mitigation": alarm.get("mitigation") # 🛡️ Müdahale bilgisi eklendi
                },
            )
            
            # 🏷️ Veri Seti İçin Otomatik Etiketleme
            security_event["true_label"] = mode.upper()
            
            event_pipeline.emit_event(security_event)
            
            # Walrus Anomaly Bundle Trigger
            bundler.trigger_anomaly(alarm, {
                "anomaly_type": alarm["anomaly_type"],
                "severity": alarm["severity"],
                "cp_id": alarm["cp_id"],
                "ml_score": alarm.get("ml", {}).get("score", 0.0),
                "rule_id": alarm["anomaly_type"]
            })

        # Walrus Time-Batch Ingestion (Her event için)
        bundler.ingest_log(event)

        # 6) Log output
        for alarm in alarms:
            logger.warning(
                f"🚨 ALARM ({alarm.get('anomaly_type')}) @ {alarm.get('cp_id')} → {alarm.get('details')}"
            )

        return alarms
