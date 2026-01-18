from src.core.anomaly_engine import AnomalyEngine

_engine = AnomalyEngine()

def forward_event(event: dict):
    """
    Simülasyon tarafından üretilen event'i
    gerçek ana motora iletir.
    """
    return _engine.process(event)
