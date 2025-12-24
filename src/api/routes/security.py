# src/api/routes/security.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
import time
import os

router = APIRouter(prefix="/security", tags=["Security"])

#  Alarm dosyasını buraya FIXLEDİK
SEC_FILE = "logs/alarms.jsonl"

# Dosya yoksa oluştur
os.makedirs("logs", exist_ok=True)
if not os.path.exists(SEC_FILE):
    open(SEC_FILE, "w").close()


@router.get("/history")
def history():
    with open(SEC_FILE, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    return [json.loads(l) for l in lines]


@router.get("/live")
def live():
    def event_stream():
        with open(SEC_FILE, "r", encoding="utf-8") as f:
            # İlk başta dosyanın sonuna git
            f.seek(0, os.SEEK_END)

            while True:
                line = f.readline()
                if line.strip():
                    yield f"data: {line.strip()}\n\n"
                else:
                    time.sleep(0.2)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
