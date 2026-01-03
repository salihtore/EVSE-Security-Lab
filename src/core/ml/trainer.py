import logging
import json
import pickle
import os
import time
from typing import Dict, Any, List

from src.core.storage.walrus_client import WalrusClient
from src.core.encryption.local_crypto import LocalCrypto
from src.core.ml.feature_extractor import extract, vectorize
from sklearn.ensemble import IsolationForest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Trainer")

# Model dosyasının yolu
MODEL_PATH = "src/core/models/model.pkl"

class Trainer:
    """
    Automated Feedback Loop:
    Walrus -> Download -> Decrypt -> Preprocess -> Retrain -> Save
    """
    def __init__(self):
        self.storage = WalrusClient()
        self.crypto = LocalCrypto()
        
    def train_from_walrus(self, blob_id: str) -> Dict[str, Any]:
        """
        Şifreli Walrus blob'unu indirir, çözer ve modeli eğitir.
        """
        logger.info(f"🎓 Training started for Blob ID: {blob_id}")
        
        # 1. DOWNLOAD
        encrypted_bytes = self.storage.read_blob(blob_id)
        if not encrypted_bytes:
            logger.error("❌ Download failed. Aborting training.")
            return {"status": "failed", "reason": "download_error"}
            
        # 2. DECRYPT
        try:
            # Bytes -> JSON String (Encrypted Payload)
            payload_str = encrypted_bytes.decode('utf-8')
            encrypted_payload = json.loads(payload_str)
            
            # Decrypt -> JSON String (Bundle)
            plaintext = self.crypto.decrypt(encrypted_payload)
            bundle = json.loads(plaintext)
            
            logger.info(f"🔓 Decryption successful. Found {bundle.get('record_count')} records.")
            
        except Exception as e:
            logger.error(f"❌ Decryption failed: {e}")
            return {"status": "failed", "reason": "decryption_error"}
            
        # 3. PREPROCESS (Feature Extraction)
        logs = bundle.get("logs", [])
        if not logs:
            logger.warning("Empty batch. Skipping training.")
            return {"status": "skipped", "reason": "empty_batch"}
            
        X_train = []
        for log in logs:
            # Training için "state" bilgisi simüle edilir veya boş geçilir.
            # Batch process olduğu için gerçek zamanlı state tam olarak bilinemez.
            # Ancak stateless featurelar (meter_value, msg_type) yeterlidir.
            features = extract(log, state={}) 
            vector = vectorize(features)
            X_train.append(vector)
            
        if not X_train:
            return {"status": "skipped", "reason": "no_features"}
            
        # 4. TRAIN (Retrain from scratch or partial_fit if supported)
        # IsolationForest partial_fit desteklemez (sklearn standart).
        # Bu yüzden elimizdeki son batch ile "Incremental Learning" simülasyonu yapıyoruz
        # veya sıfırdan eğitiyoruz. Gerçek dünyada büyük veri seti birikmeli.
        # Burada demo amaçlı: Sadece bu batch ile modeli güncelliyoruz (Overfit riski var ama akış doğru)
        
        logger.info(f"🧠 Training model with {len(X_train)} samples...")
        
        # Daha sağlam model için parametreler
        model = IsolationForest(
            n_estimators=100,
            contamination=0.05, # %5 anomali varsayımı
            random_state=42
        )
        model.fit(X_train)
        
        # 5. SAVE
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        
        model_data = {
            "model": model,
            "feature_order": ["msg_type_hash", "has_meter", "..."], # Tam listeyi feature_extractor'dan almalı
            "contamination": 0.05,
            "train_samples": len(X_train),
            "timestamp": time.time(),
            "source_blob": blob_id
        }
        
        try:
            with open(MODEL_PATH, "wb") as f:
                pickle.dump(model_data, f)
            logger.info(f"💾 Model saved to {MODEL_PATH}")
        except Exception as e:
            logger.error(f"❌ Failed to save model: {e}")
            return {"status": "failed", "reason": "save_error"}
            
        return {
            "status": "success",
            "samples": len(X_train),
            "blob_id": blob_id,
            "model_path": MODEL_PATH
        }

if __name__ == "__main__":
    # Test
    # t = Trainer()
    # t.train_from_walrus("BLOB_ID_HERE")
    pass
