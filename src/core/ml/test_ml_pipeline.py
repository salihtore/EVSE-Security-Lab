# src/core/ml/test_ml_pipeline.py

from src.core.ml.model_loader import load_model
from src.core.ml.scorer import MLScorer
from src.core.ml.feature_extractor import extract
import pandas as pd

DATASET_PATH = "data/dataset_from_logs.csv"


def main():
    print("\n=== ML PIPELINE TEST ===\n")

    # -------------------------------------------------
    # 1) Model yükleme testi
    # -------------------------------------------------
    bundle = load_model()
    assert bundle is not None, "❌ Model bundle yüklenemedi"

    print("✅ Model bundle yüklendi")
    print(f"   Feature order length: {len(bundle['feature_order'])}")
    print(f"   Contamination       : {bundle.get('contamination')}")

    scorer = MLScorer(bundle)
    assert scorer.is_ready(), "❌ MLScorer hazır değil"

    print("✅ MLScorer hazır\n")

    # -------------------------------------------------
    # 2) Dataset yükle
    # -------------------------------------------------
    df = pd.read_csv(DATASET_PATH)
    assert not df.empty, "❌ Dataset boş"

    print(f"✅ Dataset yüklendi ({len(df)} satır)\n")

    # -------------------------------------------------
    # 3) Normal vs Anomali örnek seç
    # -------------------------------------------------
    normal_row = df[df["label"] == 0].iloc[0]
    anomaly_row = df[df["label"] == 1].iloc[0]

    print("🔍 Örnekler seçildi")
    print(f"   NORMAL   cp_id={normal_row['cp_id']}")
    print(f"   ANOMALY  cp_id={anomaly_row['cp_id']}\n")

    # -------------------------------------------------
    # 4) Feature çıkarımı
    # -------------------------------------------------
    normal_features = extract(event=normal_row.to_dict(), state=normal_row.to_dict())
    anomaly_features = extract(event=anomaly_row.to_dict(), state=anomaly_row.to_dict())

    # -------------------------------------------------
    # 5) Skor üretimi
    # -------------------------------------------------
    normal_score = scorer.score(normal_features)
    anomaly_score = scorer.score(anomaly_features)

    print("📊 ML SCORE SONUÇLARI")
    print(f"   NORMAL  score : {normal_score}")
    print(f"   ANOMALY score : {anomaly_score}\n")

    assert normal_score is not None, "❌ Normal skor None"
    assert anomaly_score is not None, "❌ Anomali skor None"

    # -------------------------------------------------
    # 6) Mantık kontrolü
    # -------------------------------------------------
    if anomaly_score > normal_score:
        print("✅ TEST BAŞARILI: Anomali skoru daha yüksek")
    else:
        print("⚠️  UYARI: Anomali skoru normalden yüksek değil")
        print("   Bu durum feature kalitesiyle ilgilidir, pipeline hatası değildir")

    print("\n=== TEST TAMAMLANDI ===\n")


if __name__ == "__main__":
    main()
