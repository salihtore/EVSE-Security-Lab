import pandas as pd
import matplotlib.pyplot as plt

# Log dosyasını oku
df = pd.read_csv("termal_yanilma_ws_log.csv")

# Boole string geldiyse düzelt
df["attack"] = df["attack"].astype(str) == "True"
df["anomaly"] = df["anomaly"].astype(str) == "True"

print("İlk satırlar:")
print(df.head(), "\n")

total = len(df)
attack_count = df["attack"].sum()
anomaly_count = df["anomaly"].sum()

# Performans metrikleri
tp = ((df["attack"] == True) & (df["anomaly"] == True)).sum()
fp = ((df["attack"] == False) & (df["anomaly"] == True)).sum()
fn = ((df["attack"] == True) & (df["anomaly"] == False)).sum()
tn = ((df["attack"] == False) & (df["anomaly"] == False)).sum()

accuracy = (tp + tn) / total if total > 0 else 0
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0

print(f"Toplam adım: {total}")
print(f"Attack olan adım sayısı: {attack_count}")
print(f"Anomali tespit edilen adım sayısı: {anomaly_count}")
print()
print("Confusion Matrix:")
print(f"  TP (attack & anomaly): {tp}")
print(f"  FP (no attack & anomaly): {fp}")
print(f"  FN (attack & no anomaly): {fn}")
print(f"  TN (no attack & no anomaly): {tn}")
print()
print(f"Accuracy:  {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall:    {recall:.3f}")

# Grafik
steps = df["step"]
temps = df["temp"]
currents = df["current"]

attack_steps = df[df["attack"]]["step"]
attack_temps = df[df["attack"]]["temp"]

anomaly_steps = df[df["anomaly"]]["step"]
anomaly_temps = df[df["anomaly"]]["temp"]

plt.figure()
plt.plot(steps, temps, label="Temp (°C)")
plt.plot(steps, currents, label="Current (A)")

plt.scatter(attack_steps, attack_temps, marker="x", label="Attack Phase")
plt.scatter(anomaly_steps, anomaly_temps, marker="o", label="Anomaly Detected")

plt.xlabel("Step")
plt.ylabel("Value")
plt.title("Thermal Spoofing - WS Log Analizi")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
