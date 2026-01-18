#build_dataset_from_logs.py
"""
EVSE Security Lab
Build Dataset From Real Logs (events.jsonl + alarms.jsonl)

Amaç:
- events.jsonl -> feature kaynağı
- alarms.jsonl -> label (ground truth)
- ML'e SADECE event davranışı gösterilir
- Alarm kayıtları feature OLMAZ

Çıktı:
data/dataset_from_logs.csv
"""

import json
import csv
from pathlib import Path

# -------------------------------------------------
# AYARLAR
# -------------------------------------------------
EVENTS_FILE = "logs/events.jsonl"
ALARMS_FILE = "logs/alarms.jsonl"
OUT_FILE = "data/dataset_from_logs.csv"

ALARM_TIME_WINDOW_SEC = 0.10  # ±100ms tolerans

FIELDNAMES = [
    "timestamp",
    "cp_id",
    "message_type",
    "transaction_id",
    "meter_value",
    "plugged",
    # META (ML GÖRMEZ)
    "label",
    "anomaly_type",
]

# -------------------------------------------------
# YARDIMCI
# -------------------------------------------------
def extract_meter_value(payload: dict) -> float:
    """
    payload içinden meter_value çıkarmaya çalışır.
    Bulamazsa 0.0 döner.
    """
    try:
        mv = payload.get("meterValue")
        if not mv:
            return 0.0
        sampled = mv[0].get("sampledValue")
        if not sampled:
            return 0.0
        return float(sampled[0].get("value", 0.0))
    except Exception:
        return 0.0


# -------------------------------------------------
# ANA FONKSİYON
# -------------------------------------------------
def build_dataset_from_logs():
    print("🚀 Gerçek loglardan dataset oluşturuluyor")

    event_seen = 0
    event_written = 0

    # -------------------------------------------------
    # 0) Daha önce yazılmış event'leri oku (idempotent)
    # -------------------------------------------------
    processed_keys = set()

    if Path(OUT_FILE).exists():
        with open(OUT_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = f"{row['cp_id']}|{row['timestamp']}|{row['message_type']}"
                processed_keys.add(key)

    # -------------------------------------------------
    # 1) Alarm index oluştur (cp_id -> [alarm])
    # -------------------------------------------------
    alarm_index = {}

    if Path(ALARMS_FILE).exists():
        with open(ALARMS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    alarm = json.loads(line)
                except Exception:
                    continue

                cp_id = alarm.get("cp_id")
                ts = alarm.get("timestamp")
                anomaly_type = alarm.get("anomaly_type", "UNKNOWN")

                if not cp_id or ts is None:
                    continue

                alarm_index.setdefault(cp_id, []).append({
                    "timestamp": float(ts),
                    "anomaly_type": anomaly_type,
                })

    total_alarms = sum(len(v) for v in alarm_index.values())
    print(f"🔎 Yüklenen alarm sayısı: {total_alarms}")

    # Aynı alarm birden fazla event'e yapışmasın
    used_alarms = set()

    # -------------------------------------------------
    # 2) CSV hazırlık
    # -------------------------------------------------
    Path(OUT_FILE).parent.mkdir(parents=True, exist_ok=True)
    file_exists = Path(OUT_FILE).exists()

    with open(OUT_FILE, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)

        if not file_exists:
            writer.writeheader()

        # -------------------------------------------------
        # 3) Event'leri işle
        # -------------------------------------------------
        with open(EVENTS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line)
                except Exception:
                    continue

                event_seen += 1

                # timestamp
                try:
                    ts = float(event.get("timestamp"))
                except Exception:
                    continue

                cp_id = event.get("cp_id")
                if not cp_id:
                    continue

                # message_type
                message_type = event.get("message_type")
                if not message_type:
                    message_type = event.get("event_type", "UNKNOWN_EVENT")

                event_key = f"{cp_id}|{ts}|{message_type}"
                if event_key in processed_keys:
                    continue

                transaction_id = event.get("transaction_id")

                payload = event.get("payload", {})
                meter_value = extract_meter_value(payload)

                # plugged bilgisi
                plugged = payload.get("plug_state")
                if plugged is None:
                    plugged = payload.get("plugged", 0)
                plugged = 1 if bool(plugged) else 0

                # -------------------------------------------------
                # 4) Alarm eşleştirme (tek alarm -> tek event)
                # -------------------------------------------------
                label = 0
                anomaly_type = "NORMAL"

                closest_alarm = None
                closest_dt = ALARM_TIME_WINDOW_SEC

                alarms_for_cp = alarm_index.get(cp_id, [])

                for alarm in alarms_for_cp:
                    alarm_key = (
                        cp_id,
                        alarm["timestamp"],
                        alarm["anomaly_type"],
                    )

                    if alarm_key in used_alarms:
                        continue

                    dt = abs(ts - alarm["timestamp"])
                    if dt <= closest_dt:
                        closest_dt = dt
                        closest_alarm = alarm

                if closest_alarm:
                    label = 1
                    anomaly_type = closest_alarm["anomaly_type"]
                    used_alarms.add(
                        (
                            cp_id,
                            closest_alarm["timestamp"],
                            closest_alarm["anomaly_type"],
                        )
                    )

                # -------------------------------------------------
                # 5) CSV yaz
                # -------------------------------------------------
                writer.writerow({
                    "timestamp": ts,
                    "cp_id": cp_id,
                    "message_type": message_type,
                    "transaction_id": transaction_id,
                    "meter_value": meter_value,
                    "plugged": plugged,
                    "label": label,
                    "anomaly_type": anomaly_type,
                })

                processed_keys.add(event_key)
                event_written += 1

    print("✅ Tamamlandı")
    print(f"📂 Çıktı: {OUT_FILE}")
    print(f"🔎 Toplam satır okundu (events.jsonl): {event_seen}")
    print(f"✅ CSV'ye yazılan satır sayısı      : {event_written}")


if __name__ == "__main__":
    build_dataset_from_logs()
