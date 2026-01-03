# src/core/ml/scorer.py

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class MLScorer:
    """
    IsolationForest tabanlı anomaly scorer.
    """

    def __init__(self, model_bundle: Optional[Dict[str, Any]]):
        """
        model_bundle:
            model_loader.load_model() çıktısı olmalı.
        """
        if not model_bundle:
            self.model = None
            self.feature_order = []
            self.contamination = None
            return

        self.model = model_bundle.get("model")
        self.feature_order = model_bundle.get("feature_order", [])
        self.contamination = model_bundle.get("contamination")

    def is_ready(self) -> bool:
        """
        Model inference için hazır mı?
        """
        return self.model is not None and bool(self.feature_order)

    def score(self, feature_dict: Dict[str, float]) -> Optional[float]:
        """
        Feature dict -> anomaly score üretir.

        Returns:
            float : anomaly score (yüksek = daha anomal)
            None  : model yoksa veya hata varsa
        """
        if not self.is_ready():
            return None

        try:
            # Feature vektörünü doğru sırada oluştur
            x = [[
                float(feature_dict.get(feature, 0.0))
                for feature in self.feature_order
            ]]

            # IsolationForest decision_function:
            #   yüksek -> normal
            #   düşük  -> anomal
            raw_score = self.model.decision_function(x)[0]

            # Anomaly score:
            #   yüksek = daha anomal
            anomaly_score = -raw_score

            return float(anomaly_score)

        except Exception:
            logger.exception("ML scoring failed")
            return None
