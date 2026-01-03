# src/core/ml/model_loader.py

import os
import pickle
from typing import Optional, Dict, Any

# Varsayılan model yolu
DEFAULT_MODEL_PATH = "src/core/models/model.pkl"


def model_exists(path: str = DEFAULT_MODEL_PATH) -> bool:
    """
    Model dosyasının varlığını ve boş olmadığını kontrol eder.
    """
    try:
        return os.path.isfile(path) and os.path.getsize(path) > 0
    except Exception:
        return False


def load_model(path: str = DEFAULT_MODEL_PATH) -> Optional[Dict[str, Any]]:
    """
    Eğitilmiş ML model bundle'ını güvenli şekilde yükler.

    Dönüş:
        {
            "model": IsolationForest,
            "feature_order": [...],
            "contamination": float,
            "train_samples": int,
            "total_samples": int
        }

    Hata durumunda None döner.
    """
    if not model_exists(path):
        print(f"[MODEL LOADER] Model file NOT FOUND at: {os.path.abspath(path)}")
        return None

    try:
        with open(path, "rb") as f:
            bundle = pickle.load(f)

        # Minimum doğrulama
        if not isinstance(bundle, dict):
            return None

        if "model" not in bundle or "feature_order" not in bundle:
            return None

        return bundle

    except Exception as e:
        import traceback
        print(f"[MODEL LOADER ERROR] Path: {os.path.abspath(path)} Error: {e}")
        # traceback.print_exc()
        return None
