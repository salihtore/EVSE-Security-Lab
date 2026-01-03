# train_model.py
import os
import sys
import argparse
import pandas as pd
import pickle
import numpy as np
from sklearn.ensemble import IsolationForest

# ---------------------------------------------------------
# PATH AYARLARI
# ---------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.append(project_root)

# ---------------------------------------------------------
# FEATURE EXTRACTOR
# ---------------------------------------------------------
try:
    from src.core.ml.feature_extractor import extract, vectorize, FEATURE_ORDER
except ImportError:
    print("KRİTİK HATA: feature_extractor bulunamadı!")
    sys.exit(1)


def train(data_path: str, output_path: str):
    print(f"[*] Veri seti okunuyor: {data_path}")

    if not os.path.exists(data_path):
        print(f"HATA: Dataset bulunamadı: {data_path}")
        sys.exit(1)

    df = pd.read_csv(data_path)

    if df.empty:
        print("HATA: Dataset boş!")
        sys.exit(1)

    print(f"[*] Toplam {len(df)} satır yüklendi")
    print(f"[*] Feature order: {FEATURE_ORDER}")

    X = []

    print("[*] Feature extraction başlıyor...")
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        feature_dict = extract(event=row_dict, state=row_dict)
        vector = vectorize(feature_dict)
        X.append(vector)

    X = np.array(X)
    print(f"[*] Feature matrix hazır: {X.shape}")

    print("[*] IsolationForest eğitiliyor...")
    clf = IsolationForest(
        n_estimators=100,
        contamination=0.1,
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X)

    # -----------------------------
    # MODEL BUNDLE (KRİTİK)
    # -----------------------------
    bundle = {
        "model": clf,
        "feature_order": FEATURE_ORDER,
        "contamination": 0.1
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "wb") as f:
        pickle.dump(bundle, f)

    print("\n" + "-" * 60)
    print("✅ MODEL BAŞARIYLA EĞİTİLDİ")
    print(f"📂 Model yolu          : {output_path}")
    print(f"📊 Eğitim örnek sayısı : {len(df)}")
    print("-" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="EVSE Anomaly Detection - Model Trainer"
    )

    parser.add_argument(
        "--data",
        type=str,
        default="data/dataset_from_logs.csv",
        help="Eğitim dataset (CSV)"
    )

    parser.add_argument(
        "--out",
        type=str,
        default="src/core/models/model.pkl",
        help="Çıktı model dosyası"
    )

    args = parser.parse_args()

    train(args.data, args.out)
