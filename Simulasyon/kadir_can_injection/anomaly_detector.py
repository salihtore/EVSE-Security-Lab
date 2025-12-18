import numpy as np
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self, safe_limit=70):
        self.safe_limit = safe_limit
        self.model = self.train_model()

        self.prev_temp = None
        self.prev_current = None

    def train_model(self):
        temps = np.random.normal(35, 5, 1500)
        currents = np.random.normal(16, 1, 1500)

        X = np.column_stack([temps, currents])

        model = IsolationForest(n_estimators=200, contamination=0.03, random_state=42)
        model.fit(X)
        return model

    def detect(self, data):

        temp = float(data["temp"])
        current = float(data["current"])
        cooling = data["cooling"]
        ambient = data["ambient"]

        reasons = []

        # KURAL-1: Cooling OFF spoofing
        if not cooling and current > 18 and temp < self.safe_limit:
            reasons.append("Cooling OFF + low temp + high current")

        # KURAL-2: Hot ambient but sensor shows safe temp
        if ambient > 30 and current > 15 and temp < self.safe_limit:
            reasons.append("Ambient hot but critical sensor low")

        # KURAL-3: current jumps but temp flat
        if self.prev_current is not None:
            if (current - self.prev_current) > 5 and abs(temp - self.prev_temp) < 1:
                reasons.append("Current jump but temperature stagnant")

        # ML anomaly
        score = self.model.decision_function([[temp, current]])[0]
        if score < -0.1:
            reasons.append(f"ML anomaly (score={score:.3f})")

        # update previous
        self.prev_temp = temp
        self.prev_current = current

        if reasons:
            return True, " | ".join(reasons)

        return False, None
