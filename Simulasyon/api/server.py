# Simulasyon/api/server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LOG_PATH = os.path.join(BASE_DIR, "logs", "system.log")

ALARM_PATTERN = re.compile(
    r"ALARM \((?P<type>[^)]+)\) @ (?P<cp>[^ ]+)"
)

@app.get("/logs/alarms")
def get_alarms():
    if not os.path.exists(LOG_PATH):
        return []

    alarms = []

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f.readlines()[-300:]:
            if "ALARM" in line:
                match = ALARM_PATTERN.search(line)
                if match:
                    alarms.append({
                        "type": match.group("type"),
                        "cpId": match.group("cp"),
                        "message": line.strip(),
                    })

    return alarms
