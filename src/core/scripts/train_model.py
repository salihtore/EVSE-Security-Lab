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
# KADİR'İN MODÜLLERİNİ IMPORT ET
# ---------------------------------------------------------
try:
    from src.core.ml.feature_extractor import extract, vectorize, FEATURE_ORDER
except ImportError as e:
    print("KRİTİK HATA: Feature Extractor bulunamadı!")
    print("Kadir'in dosyasının 'src/core/ml/feature_extractor.py' olduğundan emin ol.")
    sys.exit(1)

def train(data_path, output_path):
    print(f"[*] Veri seti okunuyor: {data_path}")
    
    # Dataset dosyasını kontrol et ve oku
    if not os.path.exists(data_path):
        print(f"HATA: '{data_path}' dosyası bulunamadı.")
        sys.exit(1)
        
    df = pd.read_csv(data_path)
    
    if len(df) == 0:
        print("HATA: Veri seti boş!")
        sys.exit(1)

    print(f"[*] Toplam {len(df)} satır veri işlenecek.")
    print(f"[*] Kullanılan Feature Sırası: {FEATURE_ORDER}")

    X = []
    
    print("[*] Veriler vektörleştiriliyor...")
    
    for index, row in df.iterrows():
        # Her satırdan event/state verilerini hazırla
        # CSV düz olduğu için satırı hem event hem state yerine kullanıyoruz.
        row_dict = row.to_dict()
        feature_dict = extract(event=row_dict, state=row_dict)
        
        # Feature vektörünü oluştur
        vector = vectorize(feature_dict)
        X.append(vector)

    X = np.array(X)
    print(f"[*] Eğitim verisi hazır. Matris Boyutu: {X.shape}")

    # IsolationForest modelini eğit
    print("[*] IsolationForest modeli eğitiliyor...")
    clf = IsolationForest(
        n_estimators=100, 
        contamination=0.1, 
        random_state=42, 
        n_jobs=-1
    )
    clf.fit(X)

    # Modeli kaydet
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'wb') as f:
        pickle.dump(clf, f)
        
    print("-" * 50)
    print(f"✅ [BAŞARILI] Model eğitildi ve kaydedildi.")
    print(f"📂 Kayıt Yeri: {output_path}")
    print("-" * 50)

if __name__ == "__main__":
    # CLI argümanlarını ayarla
    parser = argparse.ArgumentParser(description="EVSE Anomaly Detection - Model Trainer")
    
    parser.add_argument(
        '--data', 
        type=str, 
        default='data/dataset.csv', 
        help='Eğitim verisi (CSV)'
    )
    
    parser.add_argument(
        '--out', 
        type=str, 
        default='src/core/models/anomaly_model.pkl', 
        help='Çıktı model dosyası (.pkl)'
    )

    args = parser.parse_args()

    train(args.data, args.out)
