from charge_point import ChargePoint
from anomaly_detector import AnomalyDetector
import time
import matplotlib.pyplot as plt
import pandas as pd

cp = ChargePoint()
detector = AnomalyDetector()

print("Termal Yanılma Senaryosu Başladı...\n")

steps = []
temps = []
currents = []
attack_flags = []
anomaly_flags = []
anomaly_reasons = []

ATTACK_START_STEP = 10
TOTAL_STEPS = 60

for step in range(TOTAL_STEPS):
    is_attack = step >= ATTACK_START_STEP

    if is_attack:
        if step == ATTACK_START_STEP:
            print("\n*** TERMAL SPOOFING ATTACK STARTED ***\n")
        data = cp.generate_spoofed_data()
    else:
        data = cp.generate_real_data()

    anomaly, reason = detector.detect(data)

    print(f"Step {step:02d} | Temp: {data['temp']}°C | Current: {data['current']}A"
          f" | Attack: {is_attack} | Anomaly: {anomaly}")

    steps.append(step)
    temps.append(data["temp"])
    currents.append(data["current"])
    attack_flags.append(is_attack)
    anomaly_flags.append(anomaly)
    anomaly_reasons.append(reason if anomaly else "")

    time.sleep(0.05)

print("\nSimülasyon Bitti. Log ve grafik hazırlanıyor...\n")

# --- Log'u CSV olarak kaydet ---
df = pd.DataFrame({
    "step": steps,
    "temp": temps,
    "current": currents,
    "attack": attack_flags,
    "anomaly": anomaly_flags,
    "reason": anomaly_reasons,
})

df.to_csv("termal_yanilma_log.csv", index=False)
print("Log kaydedildi: termal_yanilma_log.csv")

# --- Grafik çiz ---
plt.figure()
plt.plot(steps, temps, label="Reported Temp (°C)")
plt.plot(steps, currents, label="Current (A)")

# Attack ve anomaly noktalarını işaretle
attack_steps = [s for s, a in zip(steps, attack_flags) if a]
attack_temps = [t for t, a in zip(temps, attack_flags) if a]

anomaly_steps = [s for s, a in zip(steps, anomaly_flags) if a]
anomaly_temps = [t for t, a in zip(temps, anomaly_flags) if a]

if attack_steps:
    plt.scatter(attack_steps, attack_temps, marker="x", label="Attack Phase")
if anomaly_steps:
    plt.scatter(anomaly_steps, anomaly_temps, marker="o", label="Anomaly Detected")

plt.xlabel("Step")
plt.ylabel("Value")
plt.title("Thermal Spoofing Simulation")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
