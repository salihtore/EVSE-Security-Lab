"""
EVSE Security Lab - Feature Extractor

Bu modül, ham event + kısa süreli state bilgisini
sabit sırada bir feature vektörüne dönüştürür.

TEK KAYNAK (single source of truth):
- FEATURE_ORDER: Tüm training ve runtime tarafı bu sırayı kullanmalıdır.

Feature'lar:
    1) msg_type_hash
       - event["message_type"] string'inin basit, deterministik hash karşılığı (%1000).
       - Amaç: Message tipini kategorik olarak encode etmek (ör: TX_KADIR_AMP, TX_REAL, vb.)

    2) has_meter
       - Bu event'te geçerli bir "meter_value" alanı var mı?
       - Yoksa: 0.0
       - Varsa: 1.0

    3) meter_value
       - Event içindeki anlık sayaç / ölçüm değeri (float).
       - Örn: sıcaklık, enerji ölçümü vb.
       - Parse edilemiyorsa veya yoksa: 0.0

    4) session_active
       - Şu anda bu CP için bir şarj oturumu aktif mi?
       - StateBuffer.snapshot(cp_id)["session_active"] alanından gelir.
       - True -> 1.0, False/None -> 0.0

    5) plugged
       - Araç fiziksel olarak takılı mı?
       - StateBuffer.snapshot(cp_id)["plugged"] veya event["plugged"] üzerinden alınır.
       - True -> 1.0, False/None -> 0.0

    6) events_last_10s
       - Son 10 saniyede bu CP için kaç event gözlendi?
       - StateBuffer.snapshot(cp_id)["events_last_10s"] değeridir.
       - Yoksa: 0.0

    7) time_since_last_event
       - Son event'ten bu yana geçen süre (saniye).
       - StateBuffer.snapshot(cp_id)["time_since_last_event"] değeridir.
       - Yoksa: 0.0

    8) has_transaction_id
       - Bu event'te transaction_id mevcut ve boş değil mi?
       - Yoksa: 0.0
       - Varsa: 1.0

    9) meter_delta_10s
       - Son 10 saniyedeki sayaç değişimi.
       - StateBuffer.snapshot(cp_id)["meter_delta_10s"] değeridir.
       - Yoksa: 0.0

Çıktı:
- Her event için, FEATURE_ORDER ile uyumlu sabit sırada bir feature vektörü.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence

# ---------------------------------------------------------
#  TEK SIRALAMA KAYNAĞI
# ---------------------------------------------------------

#: ML tarafından kullanılacak tüm feature'ların sabit sırası.
#: Training ve runtime pipeline'larının HEPSİ bu sıraya göre vektör üretmelidir.
FEATURE_ORDER: Sequence[str] = [
    "msg_type_hash",
    "has_meter",
    "meter_value",
    "session_active",
    "plugged",
    "events_last_10s",
    "time_since_last_event",
    "has_transaction_id",
    "meter_delta_10s",
]


# ---------------------------------------------------------
#  YARDIMCI FONKSİYONLAR
# ---------------------------------------------------------

def _simple_msg_type_hash(message_type: Any) -> float:
    """
    message_type -> [0, 999] aralığında basit ve deterministik hash değeri.

    Python'un built-in hash() fonksiyonu process bazlı randomize olduğu için
    burada kendi küçük hash fonksiyonumuzu kullanıyoruz.
    """
    if not message_type:
        return 0.0

    s = str(message_type)
    h = 0
    for ch in s:
        # Küçük ve deterministik bir polinomial rolling hash
        h = (h * 31 + ord(ch)) % 1000

    return float(h)


def _to_float(value: Any, default: float = 0.0) -> float:
    """
    Verilen değeri güvenli şekilde float'a çevirir.
    Başarısız olursa default döner.
    """
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _bool_to_float(value: Any) -> float:
    """
    Bool benzeri bir değeri 0.0 / 1.0'a çevirir.

    True  -> 1.0
    False veya None -> 0.0
    """
    return 1.0 if bool(value) else 0.0


# ---------------------------------------------------------
#  ANA API
# ---------------------------------------------------------

def extract(
    event: Mapping[str, Any],
    state: Mapping[str, Any] | None = None,
) -> Dict[str, float]:
    """
    Event + kısa süreli state → feature dict.

    Parametreler:
        event:
            Tek bir ham event kaydı.
            Beklenen alanlar (hepsi opsiyonel, eksikse 0 basılır):
                - "message_type": str
                - "transaction_id": str veya None
                - "meter_value": float benzeri
                - "plugged": bool benzeri
                - "session_active": bool benzeri (isteğe bağlı)
        state:
            StateBuffer.snapshot(cp_id) çıktısı.
            Beklenen alanlar:
                - "events_last_10s": int
                - "time_since_last_event": float
                - "session_active": bool
                - "meter_delta_10s": float
                - "plugged": bool

    Dönüş:
        feature_dict: Dict[str, float]
            Key'ler FEATURE_ORDER ile birebir aynı isimde.
            Eksik veya bozuk veri için default 0.0 değerler döner.
    """
    state = state or {}

    # 1) msg_type_hash
    msg_type = event.get("message_type") or event.get("msg_type")
    msg_type_hash = _simple_msg_type_hash(msg_type)

    # 2) has_meter
    has_meter = 1.0 if "meter_value" in event and event.get("meter_value") is not None else 0.0

    # 3) meter_value
    meter_value = _to_float(event.get("meter_value"), default=0.0)

    # 4) session_active (öncelik state)
    session_raw = state.get("session_active", event.get("session_active", False))
    session_active = _bool_to_float(session_raw)

    # 5) plugged (öncelik state)
    plugged_raw = state.get("plugged", event.get("plugged", False))
    plugged = _bool_to_float(plugged_raw)

    # 6) events_last_10s
    events_last_10s = _to_float(state.get("events_last_10s", 0), default=0.0)

    # 7) time_since_last_event
    time_since_last_event = _to_float(state.get("time_since_last_event", 0.0), default=0.0)

    # 8) has_transaction_id
    tx_id = event.get("transaction_id")
    has_transaction_id = 1.0 if tx_id not in (None, "", 0) else 0.0

    # 9) meter_delta_10s
    meter_delta_10s = _to_float(state.get("meter_delta_10s", 0.0), default=0.0)

    features: Dict[str, float] = {
        "msg_type_hash": msg_type_hash,
        "has_meter": has_meter,
        "meter_value": meter_value,
        "session_active": session_active,
        "plugged": plugged,
        "events_last_10s": events_last_10s,
        "time_since_last_event": time_since_last_event,
        "has_transaction_id": has_transaction_id,
        "meter_delta_10s": meter_delta_10s,
    }

    return features


def vectorize(feature_dict: Mapping[str, Any]) -> List[float]:
    """
    Feature dict → sabit sırada feature vektörü.

    Parametreler:
        feature_dict:
            Genelde `extract(event, state)` fonksiyonunun çıktısı.
            Ancak elle oluşturulmuş bir dict de olabilir.

    Dönüş:
        list[float]:
            FEATURE_ORDER sırasına göre, her feature için float değer içeren liste.
            Eksik key'ler için 0.0 basılır.
    """
    vector: List[float] = []

    for name in FEATURE_ORDER:
        value = feature_dict.get(name, 0.0)
        vector.append(_to_float(value, default=0.0))

    return vector


__all__ = ["FEATURE_ORDER", "extract", "vectorize"]
