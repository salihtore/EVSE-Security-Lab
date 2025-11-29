# Simulasyon/core/event_bus.py
import time
from .security_engine import handle_event

def emit_event(**data):
    """
    Tüm senaryoların çağıracağı fonksiyon.
    Aldığı key/value çiftlerini bir event'e dönüştürür ve ana motora iletir.
    """
    event = {
        "timestamp": time.time(),
        **data
    }

    # Ana motora gönder
    handle_event(event)
