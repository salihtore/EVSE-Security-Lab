from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from src.api.services.tail_reader import tail

import time
import json

router = APIRouter(prefix="/events", tags=["Events"])

LOG_FILE = "logs/events.jsonl"


@router.get("/history")
def get_history():
    lines = tail(LOG_FILE, 500)
    return [json.loads(l) for l in lines]


@router.get("/live")
def live_events():
    def event_stream():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.2)
                    continue
                yield f"data: {line}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
