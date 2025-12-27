import json
import csv
import os
import argparse
from pathlib import Path


def find_meter_value(obj):
    """
    Event içinden mümkün olan en mantıklı meter değerini bulmaya çalışır.
    OCPP iç içe yapılar için recursive çalışır.
    """
    if not isinstance(obj, dict):
        return None

    # Düz alanlar
    if 'meter_kWh' in obj:
        return float(obj['meter_kWh'])

    if 'meter_value' in obj and not isinstance(obj['meter_value'], list):
        return float(obj['meter_value'])

    # OCPP MeterValues yapısı
    if 'meterValue' in obj:
        try:
            for m in obj['meterValue']:
                for s in m.get('sampledValue', []):
                    val = float(s.get('value', 0))
                    unit = s.get('unit', 'Wh')
                    return val / 1000.0 if unit == 'Wh' else val
        except Exception:
            pass

    # Recursive tarama
    for v in obj.values():
        if isinstance(v, dict):
            res = find_meter_value(v)
            if res is not None:
                return res

    return None


def build_dataset():
    parser = argparse.ArgumentParser(
        description="events.jsonl log dosyasını ML eğitim datasına dönüştürür"
    )
    parser.add_argument(
        "--input",
        default="logs/events.jsonl",
        help="Giriş JSONL dosyası"
    )
    parser.add_argument(
        "--out",
        default="data/dataset.csv",
        help="Çıkış CSV dosyası"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Maksimum satır sayısı (opsiyonel)"
    )
    args = parser.parse_args()

    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "timestamp",
        "cp_id",
        "message_type",
        "transaction_id",
        "meter_value",
        "plugged",
    ]

    rows_written = 0
    rows_read = 0

    print(f"🚀 Dataset oluşturuluyor: {args.input} → {args.out}")

    if not os.path.exists(args.input):
        print(f"❌ Giriş dosyası bulunamadı: {args.input}")
        return

    with open(args.out, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        with open(args.input, "r", encoding="utf-8") as infile:
            for line in infile:
                if args.limit and rows_read >= args.limit:
                    break

                rows_read += 1

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                cp_id = (
                    data.get("cp_id")
                    or data.get("charge_point_id")
                    or "unknown"
                )

                message_type = (
                    data.get("message_type")
                    or data.get("event_type")
                    or "UNKNOWN"
                )

                transaction_id = (
                    data.get("transaction_id")
                    or data.get("transactionId")
                    or ""
                )

                mv = find_meter_value(data)
                meter_value = float(mv) if mv is not None else 0.0

                plugged = data.get("plugged", data.get("plug_state", -1))
                if isinstance(plugged, bool):
                    plugged = 1 if plugged else 0
                if plugged is None:
                    plugged = -1

                writer.writerow({
                    "timestamp": data.get("timestamp", ""),
                    "cp_id": cp_id,
                    "message_type": message_type,
                    "transaction_id": transaction_id,
                    "meter_value": round(meter_value, 4),
                    "plugged": plugged,
                })

                rows_written += 1

    print(f"✅ Bitti. Okunan: {rows_read}, Yazılan: {rows_written}")


if __name__ == "__main__":
    build_dataset()
