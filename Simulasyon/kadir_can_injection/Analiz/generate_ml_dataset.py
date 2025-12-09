import sys
import os

# Proje kök dizini: ~/EVSE-Security-Lab
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from Simulasyon.termal_yanilma.charge_point import ChargePoint
from Simulasyon.termal_yanilma.anomaly_detector import AnomalyDetector
import pandas as pd

def generate_samples(num_normal=200, num_attack=200):
    cp = ChargePoint()
    detector = AnomalyDetector()

    rows = []

    # Normal veriler
    for step in range(num_normal):
        data = cp.generate_real_data()
        anomaly, reason = detector.detect(data)
        rows.append({
            "step": step,
            "temp": data["temp"],
            "current": data["current"],
            "attack": False,
            "rule_anomaly": anomaly
        })

    # Attack verileri
    cp = ChargePoint()
    detector = AnomalyDetector()

    for step in range(num_attack):
        data = cp.generate_spoofed_data()
        anomaly, reason = detector.detect(data)
        rows.append({
            "step": step,
            "temp": data["temp"],
            "current": data["current"],
            "attack": True,
            "rule_anomaly": anomaly
        })

    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    df = generate_samples()
    df.to_csv("ml_dataset.csv", index=False)
    print("Dataset kaydedildi: ml_dataset.csv")
    print(df.head())
