import numpy as np
from sklearn.ensemble import IsolationForest


class AnomalyDetector:
    """
    Hibrit anomaly detector:
    - Basit kurallar (rule-based)
    - IsolationForest ile ML tabanlı anomaly skoru
    """

    def __init__(self, safe_limit=70):
        self.safe_limit = safe_limit
        self.model = self._train_model()

    def _train_model(self):
        """
        Normal çalışma senaryosu için sentetik veri üretip
        IsolationForest modelini eğitir.
        """
        # Normal sıcaklık: 25–55°C arası
        temps = np.random.normal(loc=35.0, scale=5.0, size=1500)
        temps = np.clip(temps, 10, self.safe_limit - 3)

        # Normal akım: 12–18 A civarı
        currents = np.random.normal(loc=16.0, scale=1.0, size=1500)
        currents = np.clip(currents, 8, 20)

        X = np.column_stack([temps, currents])

        model = IsolationForest(
            n_estimators=200,
            contamination=0.03,   # yaklaşık %3 anomali varsay
            random_state=42
        )
        model.fit(X)
        return model

    def detect(self, data):
        temp = float(data["temp"])
        current = float(data["current"])

        reasons = []

        # --- Rule-based kontroller ---
        if temp < 0:
            reasons.append("Rule: Impossible temperature (<0°C)")

        if temp > self.safe_limit + 5:
            reasons.append("Rule: Overheating above critical limit")

        if current > 20 and temp < 25:
            reasons.append("Rule: High current with unexpectedly low temperature")

        # --- ML tabanlı anomaly skoru ---
        X = np.array([[temp, current]])
        score = self.model.decision_function(X)[0]  # büyük = normal, küçük = anomali

        # Eşik, biraz agresif ama direkt ilk adımda patlatmayacak şekilde
        if score < -0.1:
            reasons.append(f"ML: IsolationForest anomaly (score={score:.3f})")

        if reasons:
            return True, " | ".join(reasons)

        return False, None
