# Simulasyon/core/event_bus.py

from src.core.anomaly_engine import AnomalyEngine
import time

_engine = AnomalyEngine()

def emit_event(**event):
    """
    Tüm CP / senaryo event’leri buradan geçer
    """
    # timestamp yoksa ekle
    if "timestamp" not in event:
        event["timestamp"] = time.time()

    # 🔴 ASIL EKSİK OLAN YER BURASI
    _engine.process(event)
