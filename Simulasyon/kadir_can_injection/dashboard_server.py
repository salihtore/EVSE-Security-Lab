from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI()

history = {
    "step": [],
    "temp": [],
    "temp_real": [],
    "current": [],
    "attack": [],
    "anomaly": [],
    "reason": []
}

class UpdatePayload(BaseModel):
    step: int
    temp: float
    temp_real: float
    current: float
    attack: bool
    anomaly: bool
    reason: str = ""

@app.post("/update")
async def update(payload: UpdatePayload):
    history["step"].append(payload.step)
    history["temp"].append(payload.temp)
    history["temp_real"].append(payload.temp_real)
    history["current"].append(payload.current)
    history["attack"].append(payload.attack)
    history["anomaly"].append(payload.anomaly)
    history["reason"].append(payload.reason)
    return {"ok": True}

@app.get("/latest")
async def latest():
    if not history["step"]:
        return {}
    
    i = -1
    return {
        "step": history["step"][i],
        "temp": history["temp"][i],
        "temp_real": history["temp_real"][i],
        "current": history["current"][i],
        "attack": history["attack"][i],
        "anomaly": history["anomaly"][i],
        "reason": history["reason"][i],
    }

@app.get("/", response_class=HTMLResponse)
async def index():
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>EVSE Thermal Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>

<body style="background:#111; color:white; font-family:Arial;">

<h1>EVSE Thermal Dashboard</h1>

<div style="font-size:20px; margin-bottom:20px;">
    Measured Temp: <span id="measuredTemp">--</span> °C |
    Real Temp: <span id="realTemp">--</span> °C |
    Current: <span id="currentVal">--</span> A
</div>

<canvas id="tempChart" width="900" height="400"></canvas>

<script>
let ctx = document.getElementById('tempChart').getContext('2d');

let chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            {
                label: 'Measured Temp (°C)',
                borderColor: 'red',
                data: [],
                tension: 0.2
            },
            {
                label: 'Real Temp (°C)',
                borderColor: 'yellow',
                borderDash: [5,5],
                data: [],
                tension: 0.2
            }
        ]
    },
    options: { animation: false }
});

async function fetchLatest() {
    let res = await fetch("/latest");
    let data = await res.json();
    if (!("step" in data)) return;

    document.getElementById("measuredTemp").textContent = data.temp.toFixed(2);
    document.getElementById("realTemp").textContent = data.temp_real.toFixed(2);
    document.getElementById("currentVal").textContent = data.current.toFixed(2);

    chart.data.labels.push(data.step);
    chart.data.datasets[0].data.push(data.temp);
    chart.data.datasets[1].data.push(data.temp_real);

    chart.update();
}

setInterval(fetchLatest, 300);
</script>

</body>
</html>
"""
    return html

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
