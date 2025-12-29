import os
import joblib

# Varsayılan model yolu
DEFAULT_MODEL_PATH = "src/core/models/anomaly_model.pkl"


def model_exists(path: str = DEFAULT_MODEL_PATH) -> bool:
    """
    Model dosyası var mı ve boş değil mi kontrol eder.
    Hiçbir durumda exception fırlatmaz.
    """
    try:
        return os.path.isfile(path) and os.path.getsize(path) > 0
    except Exception:
        return False


def load_model(path: str = DEFAULT_MODEL_PATH):
    """
    ML modelini güvenli şekilde yükler.
    - Dosya yoksa None
    - Dosya boşsa None
    - Yükleme hatası varsa None
    """
    try:
        if not model_exists(path):
            return None

        model = joblib.load(path)
        return model

    except Exception:
        return None
