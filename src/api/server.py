from fastapi import FastAPI
import json

app = FastAPI()

@app.get("/events")
def get_events():
    try:
        with open("logs/events.jsonl") as f:
            lines = f.readlines()
            return [json.loads(l) for l in lines[-50:]]
    except:
        return []

@app.get("/alarms")
def get_alarms():
    try:
        with open("logs/alarms.jsonl") as f:
            lines = f.readlines()
            return [json.loads(l) for l in lines[-50:]]
    except:
        return []
