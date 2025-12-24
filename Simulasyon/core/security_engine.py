import json
import os
import time
from collections import defaultdict
from Simulasyon.core.sse_bus import publish_alarm_threadsafe


# =====================================================
#  ALARM LOG dosyası
# =====================================================

LOG_PATH = "alarms.json"
def log_alarm_json(alarm_type, cp_id, event):
    """
    Oluşan tüm alarmları JSON dosyasına kaydeder.
    Dashboard tarafından okunur.
    """
    alarm_entry = {
        "timestamp": time.time(),
        "alarm_type": alarm_type,
        "cp_id": cp_id,
        "event": event,
    }

    # Dosya yoksa oluştur
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f:
            json.dump([], f)

    # Eski logları oku
    with open(LOG_PATH, "r") as f:
        try:
            logs = json.load(f)
        except json.JSONDecodeError:
            logs = []

    logs.append(alarm_entry)

    # Yaz
    with open(LOG_PATH, "w") as f:
        json.dump(logs, f, indent=4)


# =====================================================
#  ANA MOTOR STATE
# =====================================================

state = defaultdict(dict)

# =====================================================
#  ANA MOTOR ALARM FONKSİYONU
# =====================================================

def raise_alarm(alarm_type, cp_id, event):
    print("🔥 RAISE_ALARM ÇAĞRILDI:", alarm_type, cp_id)

    alarm = {
        "id": f"{alarm_type}_{cp_id}_{int(time.time())}",
        "type": alarm_type,
        "level": "HIGH",
        "message": event.get("reason", alarm_type),
        "cpId": cp_id,
        "time": time.strftime("%H:%M:%S"),
    }

    log_alarm_json(alarm_type, cp_id, event)

    publish_alarm_threadsafe(alarm)



# =====================================================
#  ANA OLAY YÖNLENDİRİCİ
# =====================================================

def handle_event(event):
    print("📩 HANDLE_EVENT:", event.get("message_type"), event.get("cp_id"))
    """
    event_bus.emit_event() tarafından çağrılır.
    Tüm event türleri buradan geçer.
    """
    cp_id = event.get("cp_id", "default")

    # Bu CP'ye ait state sakla
    s = state[cp_id]

    # Her event’te güncellenebilecek temel bilgiler
    if "plug_state" in event:
        # plug_state False’a düştüğü an timestamp kaydet
        if event["plug_state"] is False and s.get("plug_state") is not False:
            s["plug_false_time"] = event["timestamp"]
        # plug_state tekrar True olursa sıfırla
        if event["plug_state"] is True:
            s["plug_false_time"] = None

    # Son kWh güncellemesi
    if "meter_kWh" in event:
        s["last_kwh"] = event["meter_kWh"]

    # Kaydet
    s.update(event)

    # =============================
    #   SENARYO KONTROLLERİ
    # =============================
    check_orphan_session(cp_id, event)
    check_status_lock(cp_id, event)
    check_phantom_during_orphan(cp_id, event)
    check_phantom_current(cp_id, event)
    check_auth_bypass(cp_id, event)
    check_replay(cp_id, event)
    check_time_desync(cp_id, event)
    # Yeni senaryo eklenecekse:
    # check_your_scenario(cp_id, event)


# =====================================================
#  1) YETİM SEANS – Kural 1
# =====================================================

def check_orphan_session(cp_id, event):
    """
    Kural-1: plug_state=False olduktan sonra session_active=True ise
    ve 30 saniyeden uzun süre StopTx gelmiyorsa alarm.
    """
    s = state[cp_id]
    plug = s.get("plug_state")
    session_active = s.get("session_active")
    plug_false_time = s.get("plug_false_time")

    # plug takılı değil + session açık
    if plug is False and session_active:
        if plug_false_time and (event["timestamp"] - plug_false_time) > 30:
            raise_alarm("ORPHAN_SESSION_TIMEOUT", cp_id, event)


# =====================================================
#  2) YETİM SEANS – Kural 2 (Status Lock)
# =====================================================

def check_status_lock(cp_id, event):
    """
    Kural-2: plug_state=False iken status='Charging' geliyorsa alarm.
    """
    plug = event.get("plug_state")
    status = event.get("status")  # OCPP status

    if plug is False and status == "Charging":
        raise_alarm("STATUS_LOCK_CHARGING_WHILE_UNPLUGGED", cp_id, event)


# =====================================================
#  3) YETİM SEANS – Kural 3 (unplugged ama meter artıyor)
# =====================================================

def check_phantom_during_orphan(cp_id, event):
    """
    plug=False & session_active=True iken meter artıyorsa
    → Yetim seans phantom tüketim.
    """
    if event.get("message_type") != "MeterValues":
        return

    s = state[cp_id]
    last_kwh = s.get("last_kwh")
    plug = s.get("plug_state")
    session_active = s.get("session_active")
    kwh = event.get("meter_kWh")

    if last_kwh is None:
        return

    if plug is False and session_active and kwh > last_kwh:
        raise_alarm("ORPHAN_SESSION_PHANTOM_CONSUMPTION", cp_id, event)


# =====================================================
#  4) PHANTOM CURRENT (genel kural)
# =====================================================

def check_phantom_current(cp_id, event):
    """
    session_active=False & plug_state=False iken meter artıyorsa → Phantom Current.
    """
    if event.get("message_type") != "MeterValues":
        return

    s = state[cp_id]
    last_kwh = s.get("last_kwh")
    plug = s.get("plug_state")
    session_active = s.get("session_active")
    kwh = event.get("meter_kWh")

    if last_kwh is None:
        return

    if session_active is False and plug is False and kwh > last_kwh:
        raise_alarm("PHANTOM_CURRENT", cp_id, event)


# =====================================================
#  5) AUTH BYPASS
# =====================================================

def check_auth_bypass(cp_id, event):
    """
    Authorize yapılmadan StartTransaction geliyorsa → Auth Bypass.
    """
    s = state[cp_id]

    if event.get("message_type") == "Authorize":
        s["last_auth_idTag"] = event.get("idTag")
        return

    if event.get("message_type") == "StartTransaction":
        id_tag = event.get("idTag")
        last_auth = s.get("last_auth_idTag")

        if last_auth is None or last_auth != id_tag:
            raise_alarm("AUTH_BYPASS", cp_id, event)


# =====================================================
#  6) REPLAY ATTACK
# =====================================================

def check_replay(cp_id, event):
    """
    Aynı event payload'ı daha önce görüldüyse → Replay Attack.
    """
    s = state[cp_id]
    seen = s.setdefault("seen_payloads", set())

    payload = str(event)

    if payload in seen:
        raise_alarm("REPLAY_ATTACK", cp_id, event)
    else:
        seen.add(payload)


# =====================================================
#  7) TIME DESYNC (Berat)
# =====================================================

def check_time_desync(cp_id, event):
    """
    cp_timestamp ile csms_time arasındaki fark > 300 saniye ise → Time Desync.
    """
    cp_ts = event.get("cp_timestamp")
    csms_ts = event.get("csms_time")

    if cp_ts and csms_ts:
        if abs(cp_ts - csms_ts) > 300:
            raise_alarm("TIME_DESYNC", cp_id, event)
