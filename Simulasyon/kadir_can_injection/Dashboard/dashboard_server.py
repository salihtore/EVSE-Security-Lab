from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI()

MAX_POINTS = 400

history = {
    "step": [],
    "temp": [],
    "temp_real": [],
    "current": [],
    "cooling": [],
    "ambient": [],
    "attack": [],
    "anomaly": [],
    "reason": [],
    "command": [],
}


class UpdatePayload(BaseModel):
    step: int
    temp: float
    temp_real: float
    current: float
    cooling: bool
    ambient: float
    attack: bool
    anomaly: bool
    reason: str = ""
    command: str = "CONTINUE"


@app.post("/update")
async def update(payload: UpdatePayload):
    history["step"].append(payload.step)
    history["temp"].append(payload.temp)
    history["temp_real"].append(payload.temp_real)
    history["current"].append(payload.current)
    history["cooling"].append(payload.cooling)
    history["ambient"].append(payload.ambient)
    history["attack"].append(payload.attack)
    history["anomaly"].append(payload.anomaly)
    history["reason"].append(payload.reason)
    history["command"].append(payload.command)

    # list size limit
    for k in history:
        if len(history[k]) > MAX_POINTS:
            history[k] = history[k][-MAX_POINTS:]

    return {"ok": True}


@app.get("/data")
async def data():
    if not history["step"]:
        return {"history": None, "latest": None}

    latest = {k: history[k][-1] for k in history.keys()}
    return {"history": history, "latest": latest}


@app.get("/", response_class=HTMLResponse)
async def index():
    html = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8" />
<title>EVSE Thermal Spoofing – Real-Time Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body {
  background-color: #050608;
  color: #ffffff;
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 20px;
}
h1 { margin-top: 0; }
.status-row {
  margin: 8px 0;
  font-size: 16px;
}
.status-row span.label {
  font-weight: bold;
  margin-right: 5px;
}
.green { color: #32cd32; }
.red { color: #ff5555; }
.yellow { color: #ffea00; }
.cyan { color: #00e5ff; }
.chart-container {
  width: 100%;
  max-width: 1300px;
  margin-top: 10px;
}
canvas {
  background-color: #0c0f16;
  border-radius: 8px;
}
.reason-box {
  margin-top: 10px;
  font-size: 14px;
}
</style>
</head>
<body>
<h1>⚡ EVSE Thermal Spoofing – Real-Time Dashboard</h1>

<div class="status-row">
  <span class="label">Durum:</span>
  <span id="statusText" class="green">Running</span>
</div>

<div class="status-row">
  <span class="label">Anomaly:</span>
  <span id="anomalyText" class="yellow">None</span>
</div>

<div class="status-row">
  <span class="label">Attack Mode:</span>
  <span id="attackText" class="cyan">false</span>
</div>

<div class="status-row">
  <span class="label">Measured Temp:</span>
  <span id="measuredVal" class="red">--.-</span> °C
  &nbsp;|&nbsp;
  <span class="label">Real Temp:</span>
  <span id="realVal" class="yellow">--.-</span> °C
  &nbsp;|&nbsp;
  <span class="label">Current:</span>
  <span id="currentVal" class="cyan">--.-</span> A
</div>

<div class="status-row">
  <span class="label">Cooling:</span>
  <span id="coolingVal" class="cyan">--</span>
  &nbsp;|&nbsp;
  <span class="label">Ambient:</span>
  <span id="ambientVal" class="yellow">--.-</span> °C
  &nbsp;|&nbsp;
  <span class="label">Command:</span>
  <span id="cmdVal" class="green">CONTINUE</span>
</div>

<div class="reason-box">
  <span class="label">Reason:</span>
  <span id="reasonText">-</span>
</div>

<div class="chart-container">
  <canvas id="tempChart" height="200"></canvas>
</div>
<div class="chart-container" style="margin-top: 25px;">
  <canvas id="currentChart" height="120"></canvas>
</div>

<script>
let tempCtx = document.getElementById('tempChart').getContext('2d');
let currentCtx = document.getElementById('currentChart').getContext('2d');

let tempChart = new Chart(tempCtx, {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      {
        label: 'Measured Temp (°C)',
        data: [],
        borderColor: 'red',
        backgroundColor: 'rgba(255,0,0,0.15)',
        tension: 0.2,
        pointRadius: 2,
      },
      {
        label: 'Real Temp (°C)',
        data: [],
        borderColor: 'yellow',
        backgroundColor: 'rgba(255,255,0,0.10)',
        borderDash: [5,5],
        tension: 0.2,
        pointRadius: 2,
      }
    ]
  },
  options: {
    animation: false,
    responsive: true,
    scales: {
      x: { title: { display: true, text: 'Step' } },
      y: { title: { display: true, text: 'Temperature (°C)' } }
    }
  }
});

let currentChart = new Chart(currentCtx, {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      {
        label: 'Current (A)',
        data: [],
        borderColor: 'blue',
        backgroundColor: 'rgba(0,0,255,0.15)',
        tension: 0.2,
        pointRadius: 2,
      }
    ]
  },
  options: {
    animation: false,
    responsive: true,
    scales: {
      x: { title: { display: true, text: 'Step' } },
      y: { title: { display: true, text: 'Current (A)' } }
    }
  }
});

async function fetchData() {
  try {
    const res = await fetch('/data');
    const json = await res.json();

    if (!json.history || !json.latest) {
      return;
    }

    const h = json.history;
    const latest = json.latest;

    // Top numeric values
    document.getElementById('measuredVal').textContent = latest.temp.toFixed(2);
    document.getElementById('realVal').textContent = latest.temp_real.toFixed(2);
    document.getElementById('currentVal').textContent = latest.current.toFixed(2);
    document.getElementById('attackText').textContent = String(latest.attack);
    document.getElementById('coolingVal').textContent = String(latest.cooling);
    document.getElementById('ambientVal').textContent = latest.ambient.toFixed(2);
    document.getElementById('cmdVal').textContent = latest.command;
    document.getElementById('reasonText').textContent = latest.reason || "-";

    // anomaly text + color
    const anomalyEl = document.getElementById('anomalyText');
    if (latest.anomaly) {
      anomalyEl.textContent = 'Detected';
      anomalyEl.classList.remove('yellow');
      anomalyEl.classList.add('red');
    } else {
      anomalyEl.textContent = 'None';
      anomalyEl.classList.remove('red');
      anomalyEl.classList.add('yellow');
    }

    // command color
    const cmdEl = document.getElementById('cmdVal');
    cmdEl.classList.remove('green', 'yellow', 'red');
    if (latest.command === 'STOP') {
      cmdEl.classList.add('red');
    } else if (latest.command === 'DERATE') {
      cmdEl.classList.add('yellow');
    } else {
      cmdEl.classList.add('green');
    }

    // charts
    tempChart.data.labels = h.step;
    tempChart.data.datasets[0].data = h.temp;
    tempChart.data.datasets[1].data = h.temp_real;
    tempChart.update();

    currentChart.data.labels = h.step;
    currentChart.data.datasets[0].data = h.current;
    currentChart.update();

    document.getElementById('statusText').textContent = 'Running';
    document.getElementById('statusText').classList.remove('red');
    document.getElementById('statusText').classList.add('green');

  } catch (err) {
    console.error(err);
    const st = document.getElementById('statusText');
    st.textContent = 'Disconnected';
    st.classList.remove('green');
    st.classList.add('red');
  }
}

setInterval(fetchData, 300);
</script>
</body>
</html>
"""
    return html


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
