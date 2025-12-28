import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class MLScorer:
    def __init__(self, model: Any, feature_order: List[str]):
        """
        model: trained ML model (e.g. IsolationForest)
        feature_order: list defining the correct order of features
        """
        self.model = model
        self.feature_order = feature_order

    def score(self, feature_dict: Dict[str, float]) -> Optional[float]:
        """
        Generate anomaly score from given features.
        Returns:
            - float anomaly score if model exists
            - None if model is missing or error occurs
        """
        if self.model is None:
            return None

        try:
            # Vectorize features according to feature_order
            x = [[feature_dict.get(feature, 0.0) for feature in self.feature_order]]

            # Raw score from IsolationForest
            raw_score = self.model.decision_function(x)[0]

            # Invert score: higher = more anomalous
            anomaly_score = -raw_score

            return float(anomaly_score)

        except Exception as e:
            logger.exception("ML scoring failed")
            return None
