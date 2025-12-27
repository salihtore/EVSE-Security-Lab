from typing import Dict, List
import os

from src.core.detectors.auth_bypass_detector import AuthBypassDetector
from src.core.detectors.orphan_session_detector import SemihOrphanSessionDetector
from src.core.detectors.replay_detector import ReplayDetector
from src.core.detectors.phantom_current_detector import PhantomCurrentDetector
from src.core.detectors.zero_energy_detector import ZeroEnergyDetector
from src.core.detectors.time_desync_detector import TimeDesyncDetector
from src.core.detectors.thermal_manipulation_detector import ThermalManipulationDetector

from src.defense.policy_engine import PolicyEngine
from src.core.event_pipeline import event_pipeline
from src.utils.logger import logger


# ML STATE (opsiyonel – yoksa sistem çalışmaya devam eder)
try:
    from src.core.ml.state_buffer import StateBuffer
except Exception:
    StateBuffer = None


LOG_DIR = "logs"


class AnomalyEngine:
    """
    Rule-based anomaly detection engine.
    ML entegrasyonuna hazırdır fakat ML karar vermez.
    """

    def __init__(self) -> None:
        self.policy = PolicyEngine()

        # Rule-based detector'lar
        self.detectors = [
            AuthBypassDetector(),
            SemihOrphanSessionDetector(),
            ReplayDetector(),
            PhantomCurrentDetector(),
            ZeroEnergyDetector(),
            TimeDesyncDetector(),
            ThermalManipulationDetector(),
        ]

        # ML için state altyapısı (pasif)
        self.state_buffer = None
        if StateBuffer:
            try:
                self.state_buffer = StateBuffer()
            except Exception:
                self.state_buffer = None

        os.makedirs(LOG_DIR, exist_ok=True)

    # -------------------------------------------------
    # EVENT PROCESS
    # -------------------------------------------------
    def process(self, event: Dict) -> List[Dict]:
        alarms: List[Dict] = []

        # ML state update (opsiyonel, güvenli)
        if self.state_buffer:
            try:
                self.state_buffer.update(event)
            except Exception:
                pass

        # Rule-based detection
        for detector in self.detectors:
            try:
                alarm = detector.process(event)
            except Exception as exc:
                logger.error(
                    f"[AnomalyEngine] {detector.__class__.__name__} hata: {exc}"
                )
                continue

            if alarm:
                # ML alanı bugünden sabitleniyor
                alarm["ml_score"] = None

                alarms.append(alarm)

                # Defense policy
                self.policy.handle_alarm(alarm)

                # UI'ya giden security event
                sev = str(alarm.get("severity", "LOW")).upper()
                security_event = event_pipeline.build_security_event(
                    cp_id=alarm["cp_id"],
                    anomaly_type=alarm["anomaly_type"],
                    severity=sev,
                    details={
                        **alarm["details"],
                        "ml_score": alarm.get("ml_score"),
                    },
                )

                event_pipeline.emit_event(security_event)

        # Log output
        for alarm in alarms:
            logger.warning(
                f"🚨 ALARM ({alarm['anomaly_type']}) @ {alarm['cp_id']} → {alarm['details']}"
            )

        return alarms
