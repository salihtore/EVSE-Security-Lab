from __future__ import annotations

import math
from typing import Any, Dict, Optional, Mapping

from src.utils.logger import logger

from src.core.ml.model_loader import load_model
from src.core.ml.scorer import MLScorer
from src.core.ml.feature_extractor import extract


class MLEnricher:
    """
    Alarm enrichment (post-processing) katmanı.

    - Alarm üretmez.
    - Rule-based alarmı, event + state context ile skorlar.
    - alarm["ml"] alanını doldurur.

    Contract:
        alarm["ml"] = {
            "score": float | None,
            "confidence": float | None,
            "model": str | None
        }
    """

    MODEL_NAME = "isolation_forest_v1"

    def __init__(self) -> None:
        logger.debug("🔥 ML ENRICHER INIT")

        self.bundle = load_model()
        self.scorer = MLScorer(self.bundle)

        ready = self.scorer.is_ready()
        logger.info(f"✅ ML READY = {ready}")

    def is_ready(self) -> bool:
        return self.scorer.is_ready()

    @staticmethod
    def _sigmoid(x: float) -> float:
        # Numerically stable-ish sigmoid for typical small magnitudes
        try:
            return 1.0 / (1.0 + math.exp(-x))
        except Exception:
            return 0.0

    def enrich(
        self,
        event: Mapping[str, Any],
        alarm: Dict[str, Any],
        state_snapshot: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        event + state_snapshot -> features -> score -> alarm["ml"]

        Asla exception fırlatmaz.
        ML hazır değilse alarm["ml"] None olarak set edilir.
        """
        try:
            logger.debug("🔥 ML ENRICHER CALISTI")
            # logger.debug(f"ML READY = {self.is_ready()}")

            # alarm objesini kırma: ml alanını her zaman yazacağız
            if not isinstance(alarm, dict):
                return {"ml": {"score": None, "confidence": None, "model": None}}

            # Model yoksa / hazır değilse: contract'ı yine doldur
            if not self.is_ready():
                alarm["ml"] = {"score": None, "confidence": None, "model": None}
                return alarm

            # Feature çıkarımı (tek doğru yol)
            state_snapshot = state_snapshot or {}
            features: Dict[str, float] = extract(event=event, state=state_snapshot)  # type: ignore

            # logger.debug(f"FEATURES = {features}")

            score = self.scorer.score(features)
            logger.debug(f"SCORE = {score}")

            if score is None:
                alarm["ml"] = {"score": None, "confidence": None, "model": self.MODEL_NAME}
                return alarm

            # Confidence: sunumda okunabilir, 0-1 aralığı
            # Not: Score dağılımı veri setine göre değişir. Sigmoid en stabil gösterim.
            confidence = float(self._sigmoid(float(score)))

            alarm["ml"] = {
                "score": float(score),
                "confidence": confidence,
                "model": self.MODEL_NAME,
            }
            return alarm

        except Exception:
            # Fail-safe: ML asla sistemi çökertmez
            try:
                alarm["ml"] = {"score": None, "confidence": None, "model": None}
                return alarm
            except Exception:
                return {"ml": {"score": None, "confidence": None, "model": None}}
