from fastapi import APIRouter
import json
import time
from collections import Counter

router = APIRouter()

EVENT_FILE = "logs/events.jsonl"
ALARM_FILE = "logs/alarms.jsonl"


def load_jsonl(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f]
    except FileNotFoundError:
        return []


# 1) Son 5 dakikadaki event sayısı
@router.get("/event_counts")
def event_counts():
    events = load_jsonl(EVENT_FILE)
    now = time.time()

    last5 = [e for e in events if now - e["timestamp"] <= 300]

    return {
        "last_5_min": len(last5),
        "total_events": len(events),
    }


# 2) Severity dağılımı (high/medium/low)
@router.get("/severity_stats")
def severity_stats():
    alarms = load_jsonl(ALARM_FILE)

    sev = Counter(a.get("severity", "unknown") for a in alarms)

    return {
        "high": sev.get("high", 0),
        "medium": sev.get("medium", 0),
        "low": sev.get("low", 0),
    }


# 3) En aktif CP listesi
@router.get("/cp_activity")
def cp_activity():
    events = load_jsonl(EVENT_FILE)
    cp_count = Counter(e["cp_id"] for e in events)

    return dict(cp_count.most_common(5))
