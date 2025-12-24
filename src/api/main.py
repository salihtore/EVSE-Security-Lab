# src/api/main.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json
import os
import time




app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



LOG_SECURITY = os.path.join("logs", "alarms.jsonl")


def sse(obj: dict) -> str:
    return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"


@app.get("/security/live")
def security_live():
    def gen():
        last_pos = 0

        while True:
            if not os.path.exists(LOG_SECURITY):
                time.sleep(1)
                continue

            with open(LOG_SECURITY, "r", encoding="utf-8") as f:
                f.seek(last_pos)

                while True:
                    line = f.readline()
                    if not line:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    try:
                        yield sse(json.loads(line))
                    except json.JSONDecodeError:
                        pass

                last_pos = f.tell()

            time.sleep(0.5)

    return StreamingResponse(gen(), media_type="text/event-stream")
