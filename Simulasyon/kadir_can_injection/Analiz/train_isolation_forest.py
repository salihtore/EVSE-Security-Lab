import sys
import os
import pandas as pd
from sklearn.ensemble import IsolationForest
import pickle

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

df = pd.read_csv("ml_dataset.csv")

X = df[["temp", "current"]]
attack = df["attack"]

X_train = X[attack == False]

print(f"Train veri boyutu (normal): {len(X_train)}")

model = IsolationForest(
    n_estimators=100,
    contamination=0.2,
    random_state=42
)

model.fit(X_train)

# Modeli kaydet
with open("ml_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("\nML modeli başarıyla kaydedildi: ml_model.pkl")
