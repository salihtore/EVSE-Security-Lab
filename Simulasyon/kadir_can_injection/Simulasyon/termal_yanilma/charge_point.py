import numpy as np

SAFE_LIMIT = 70  # safe temperature limit (dashboard/anomaly use this idea)


class ChargePoint:
    def __init__(self):
        self.current_temp = 30.0
        self.ambient_temp = 25.0
        self.critical_temp = 120.0
        self.cooling_active = True
        self.current = 16.0

        # physical model parameters
        self.alpha = 0.002   # heating factor
        self.beta = 0.15     # cooling factor

    def update_current(self):
        """Simulate load changes."""
        noise = np.random.uniform(-2, 2)
        self.current = max(6.0, min(24.0, self.current + noise))

    def physical_model(self):
        """Real physical temperature evolution (REAL temperature)."""
        self.update_current()

        # simple non-linear heating model
        heating = self.alpha * (self.current ** 2)
        cooling = self.beta if self.cooling_active else 0.0
        noise = np.random.normal(0.0, 0.7)

        self.current_temp += heating - cooling + noise

        # clamp
        self.current_temp = max(self.current_temp, self.ambient_temp)
        self.current_temp = min(self.current_temp, self.critical_temp + 40.0)

        return round(self.current_temp, 2)

    def generate_real_data(self):
        """
        No attack: measured temp equals real temp.
        """
        temp_real = self.physical_model()
        return {
            "temp": temp_real,          # measured
            "temp_real": temp_real,     # real
            "current": round(self.current, 2),
        }

    def generate_spoofed_data(self):
        """
        Attack: real temperature grows high,
        but reported (measured) temperature is kept in a safe band (< SAFE_LIMIT).
        """
        real_temp = self.physical_model()

        # attacker tries to hide overheating:
        # keep measured temp between 40 and SAFE_LIMIT-5,
        # even if real_temp is much hotter.
        # difference will become very large when overheating happens.
        spoof_low = 40.0
        spoof_high = SAFE_LIMIT - 5.0

        # base spoof = real_temp - large offset
        spoofed = real_temp - np.random.uniform(30.0, 60.0)
        spoofed = max(spoof_low, min(spoofed, spoof_high))

        return {
            "temp": round(spoofed, 2),        # measured (spoofed, stays "safe")
            "temp_real": round(real_temp, 2), # real hot value
            "current": round(self.current, 2),
        }
