import pandas as pd
from sklearn.ensemble import IsolationForest

# Log dosyasını oku
df = pd.read_csv("termal_yanilma_ws_log.csv")

# Boole düzeltme
df["attack"] = df["attack"].astype(str) == "True"
df["anomaly"] = df["anomaly"].astype(str) == "True"

print("İlk satırlar:")
print(df.head(), "\n")

# Özellikler: sıcaklık + akım
X = df[["temp", "current"]]

# Sadece normal (attack=False) veriyi "normal" kabul edip onunla eğitiyoruz
normal_mask = df["attack"] == False
X_train = X[normal_mask]

print(f"Train veri boyutu (normal adımlar): {len(X_train)}")

# IsolationForest modeli
model = IsolationForest(
    contamination=0.1,      # veri içindeki anomali oranı tahmini
    random_state=42
)
model.fit(X_train)

# Tüm adımlar için anomali tahmini
pred = model.predict(X)      # 1 = normal, -1 = anomali
ml_anomaly = pred == -1

df["ml_anomaly"] = ml_anomaly

# Performans hesapla (saldırıya göre)
attack = df["attack"]

tp = ((attack == True) & (ml_anomaly == True)).sum()
fp = ((attack == False) & (ml_anomaly == True)).sum()
fn = ((attack == True) & (ml_anomaly == False)).sum()
tn = ((attack == False) & (ml_anomaly == False)).sum()

total = len(df)
accuracy = (tp + tn) / total if total > 0 else 0
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0

print("\n=== IsolationForest (ML) sonuçları ===")
print(f"Toplam adım: {total}")
print(f"Attack adım sayısı: {attack.sum()}")
print()
print("Confusion Matrix (ML vs attack):")
print(f"  TP (attack & ml_anomaly): {tp}")
print(f"  FP (no attack & ml_anomaly): {fp}")
print(f"  FN (attack & no ml_anomaly): {fn}")
print(f"  TN (no attack & no ml_anomaly): {tn}")
print()
print(f"Accuracy:  {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall:    {recall:.3f}")

# Birkaç örnek satır göster (yanlış sınıflananlar)
mistakes = df[(attack != ml_anomaly)]
if not mistakes.empty:
    print("\nYanlış sınıflanan örnekler:")
    print(mistakes[["step", "temp", "current", "attack", "ml_anomaly"]].head(10))
else:
    print("\nYanlış sınıflama yok (bu simülasyon için ML de %100 uyumlu).")
