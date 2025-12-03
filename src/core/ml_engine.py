from typing import Dict, Optional, List
import os
import pickle

from src.utils.logger import logger

MODEL_PATH = os.path.join("src", "core", "model.pkl")


class MLDetector:
    """
    IsolationForest vb. ile eğitilmiş genel anomaly modeli.
    Model yoksa sessizce hiçbir şey yapmaz.
    """
    anomaly_type = "ML_ANOMALY"

    def __init__(self) -> None:
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        if not os.path.exists(MODEL_PATH):
            logger.warning(f"[MLDetector] Model dosyası bulunamadı: {MODEL_PATH}")
            return
        
        #  MODEL BOŞSA HATA VERMEDEN ÇIK
        if os.path.getsize(MODEL_PATH) < 10:
         logger.warning("[MLDetector] Model dosyası boş, ML devre dışı.")
        return

        try:
            with open(MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
            logger.info("[MLDetector] Model yüklendi.")
        except Exception as exc:
            logger.error(f"[MLDetector] Model yüklenirken hata: {exc}")
            self.model = None

    def _event_to_features(self, event: Dict) -> List[float]:
        """
        Basit feature set — burada istediğin kadar geliştirebilirsin.
        """
        msg = event["message_type"]
        mv = event.get("meter_value") or 0.0
        session_active = 1.0 if event.get("session_active") else 0.0

        return [
            1.0 if msg == "BootNotification" else 0.0,
            1.0 if msg == "StartTransaction" else 0.0,
            1.0 if msg == "MeterValues" else 0.0,
            1.0 if msg == "StopTransaction" else 0.0,
            float(mv),
            session_active,
        ]

    def process(self, event: Dict) -> Optional[Dict]:
        if self.model is None:
            return None

        try:
            x = [self._event_to_features(event)]
            score = float(self.model.decision_function(x)[0])
        except Exception as exc:
            logger.error(f"[MLDetector] Model inference hatası: {exc}")
            return None

        # IsolationForest için skor genelde 0 civarı, negatife indikçe anomali
        if score < -0.2:
            return {
                "anomaly_type": self.anomaly_type,
                "cp_id": event["cp_id"],
                "severity": "medium",
                "details": {"score": score},
            }

        return None
