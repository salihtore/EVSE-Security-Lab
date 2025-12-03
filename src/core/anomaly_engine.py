from typing import Dict, List

from src.core.detectors.auth_bypass_detector import AuthBypassDetector
from src.core.detectors.orphan_session_detector import OrphanSessionDetector
from src.core.detectors.replay_detector import ReplayDetector
from src.core.detectors.phantom_current_detector import PhantomCurrentDetector
from src.core.detectors.zero_energy_detector import ZeroEnergyDetector
from src.core.detectors.time_desync_detector import TimeDesyncDetector
from src.core.detectors.thermal_manipulation_detector import ThermalManipulationDetector
from src.core.ml_engine import MLDetector
from src.defense.policy_engine import PolicyEngine
from src.utils.logger import logger

from src.core.event_pipeline import EventPipeline  # ✨ NEW IMPORT

import json
import os

LOG_DIR = "logs"
ALARM_LOG = os.path.join(LOG_DIR, "alarms.jsonl")
SECURITY_EVENT_LOG = os.path.join(LOG_DIR, "security_events.jsonl")  # ✨ NEW LOG FILE


class AnomalyEngine:
    def __init__(self) -> None:
        self.policy = PolicyEngine()
        self.detectors = [
            AuthBypassDetector(),
            OrphanSessionDetector(),
            ReplayDetector(),
            PhantomCurrentDetector(),
            ZeroEnergyDetector(),
            TimeDesyncDetector(),
            ThermalManipulationDetector(),
            MLDetector(),
        ]
        os.makedirs(LOG_DIR, exist_ok=True)

        self.event_pipeline = EventPipeline()  # ✨ NEW INSTANCE

    def process(self, event: Dict) -> List[Dict]:
        alarms: List[Dict] = []

        for detector in self.detectors:
            try:
                alarm = detector.process(event)
            except Exception as exc:
                logger.error(f"[AnomalyEngine] {detector.__class__.__name__} hata: {exc}")
                continue

            if alarm:
                alarms.append(alarm)

                # Mevcut alarm logu (dokunma)
                self._log_alarm(alarm)

                # Defense/policy mekanizması
                self.policy.handle_alarm(alarm)

                # ✨ NEW: Standard security event JSON formatı yaz
                security_event = self.event_pipeline.build_security_event(
                    cp_id=alarm["cp_id"],
                    anomaly_type=alarm["anomaly_type"],
                    severity=alarm["severity"],
                    details=alarm["details"]
                )
                self._log_security_event(security_event)

        for alarm in alarms:
            logger.warning(f"🚨 ALARM ({alarm['anomaly_type']}) @ {alarm['cp_id']} → {alarm['details']}")

        return alarms

    def _log_alarm(self, alarm: Dict) -> None:
      try:
        # 1) Normal alarm logu
        with open(ALARM_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(alarm, ensure_ascii=False) + "\n")

        # 2) Dashboard'ın canlı Security Events paneli için
        with open("logs/security_events.jsonl", "a", encoding="utf-8") as f2:
            f2.write(json.dumps(alarm, ensure_ascii=False) + "\n")

      except Exception as exc:
        logger.error(f"[AnomalyEngine] Alarm yazılamadı: {exc}")


    # ✨ NEW: Security event loglama
    def _log_security_event(self, security_event: Dict) -> None:
     try:
        with open("logs/security_events.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(security_event, ensure_ascii=False) + "\n")
     except Exception as exc:
        logger.error(f"[AnomalyEngine] Security event yazılamadı: {exc}")

