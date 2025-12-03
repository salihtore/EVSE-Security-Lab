import pandas as pd
from sklearn.ensemble import IsolationForest
import pickle

df = pd.read_csv("src/ai/dataset.csv")

X = df[["msg_type", "meter_value", "session_active"]]

model = IsolationForest(contamination=0.05)
model.fit(X)

with open("src/core/model.pkl", "wb") as f:
    pickle.dump(model, f)
