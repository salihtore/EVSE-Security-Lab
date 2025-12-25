#anomali_engine.py
from typing import Dict, List
import json
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

# from src.core.ml_engine import MLDetector


LOG_DIR = "logs"

class AnomalyEngine:
    """
    Rule-based + ML anomaly engine.
    EVENT alır → ALARM üretir.
    """

    def __init__(self) -> None:
        self.policy = PolicyEngine()

        # 🔒 RULE-BASED DETECTORS
        self.detectors = [
            AuthBypassDetector(),
            SemihOrphanSessionDetector(),
            ReplayDetector(),
            PhantomCurrentDetector(),
            ZeroEnergyDetector(),
            TimeDesyncDetector(),
            ThermalManipulationDetector(),
        ]

        # # ➕ ML (opsiyonel)
        # self.ml_detector = None
        # try:
        #     ml = MLDetector()
        #     if hasattr(ml, "is_ready") and ml.is_ready():
        #         self.ml_detector = ml
        #     else:
        #         logger.warning("[AnomalyEngine] ML hazır değil, rule-based devam")
        # except Exception as exc:
        #     logger.warning(f"[AnomalyEngine] ML devre dışı: {exc}")

        os.makedirs(LOG_DIR, exist_ok=True)

    # -------------------------------------------------
    # EVENT PROCESS
    # -------------------------------------------------
    def process(self, event: Dict) -> List[Dict]:
        alarms: List[Dict] = []

        for detector in self.detectors:
            try:
                alarm = detector.process(event)
            except Exception as exc:
                logger.error(
                    f"[AnomalyEngine] {detector.__class__.__name__} hata: {exc}"
                )
                continue

            if alarm:
                alarms.append(alarm)

                # 2️⃣ Defense policy
                self.policy.handle_alarm(alarm)

                # 3️⃣ UI'ya giden security event
                sev = str(alarm.get("severity", "LOW")).upper()
                security_event = event_pipeline.build_security_event(
                    cp_id=alarm["cp_id"],
                    anomaly_type=alarm["anomaly_type"],
                    severity=sev,
                    details=alarm["details"],
                )
                event_pipeline.emit_event(security_event)

        for alarm in alarms:
            logger.warning(
                f"🚨 ALARM ({alarm['anomaly_type']}) @ {alarm['cp_id']} → {alarm['details']}"
            )

        # ML inference (opsiyonel)
        # if self.ml_detector:
        #     try:
        #         self.ml_detector.process(event)
        #     except Exception as exc:
        #         logger.error(f"[AnomalyEngine] ML inference hatası: {exc}")

        # return alarms
