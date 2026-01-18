# ⚡ EVSE Security Lab

**Cyber-Physical Security Test and Simulation Platform for Smart Charging Stations (EVSE)**

This project is a comprehensive **cyber-physical security laboratory** developed to analyze security vulnerabilities, simulate cyber-attack scenarios, and enhance security with blockchain-based logging on **OCPP (Open Charge Point Protocol)** and related hardware components used in electric vehicle charging infrastructures (EVSE).

The platform allows researchers and developers to create their own attack scenarios, simulate these attacks, and test AI/blockchain-based defense mechanisms.

---

## 🚀 Features

- **Advanced Attack Simulations:** Pre-built scenarios including thermal manipulation, time desynchronization, session hijacking, CAN bus injection, and more.
- **OCPP 1.6-J Support:** Fully correlates and simulates communication between the Charging Station (CP) and Charging Station Management System (CSMS).
- **Blockchain Integration (Sui):** **Sui Blockchain** and **Walrus** (Blob Storage) integration for the immutability of critical event logs.
- **Live Monitoring Dashboard:** A modern **React + Vite** dashboard to monitor attacks and system status in real-time.
- **Modular Architecture:** Architecture that allows for easy addition of new scenarios and defense modules.
- **AI-Powered Defense:** Integrated machine learning models (Scikit-learn) for anomaly detection.

---

## �️ Core Security & Blockchain Technologies

### **Move Language (Sui Blockchain)**
Utilized for developing secure and efficient smart contracts. Move's object-centric data model and strict resource safety guarantees ensure that critical EVSE audit logs and security events are recorded immutably on the blockchain, eliminating common vulnerabilities found in other contract languages.

### **Walrus (Decentralized Storage)**
Integrated for robust, cost-effective storage of large-scale EVSE data logs. By leveraging Walrus, the platform ensures that raw simulation data and evidence blobs are stored in a decentralized manner, providing high availability and verifiable integrity without burdening the main chain state.

### **Microsoft SEAL (Homomorphic Encryption)**
Employed to perform computations on encrypted data. This allows the system to analyze encrypted charging sessions and user data for anomalies without ever exposing the sensitive raw information, preserving user privacy while maintaining robust security monitoring.

---

## �📂 Project Structure

```
EVSE-Security-Lab/
├── Simulasyon/              # Attack scenarios and simulation logic
│   ├── ahmet_thermal_manipulation/
│   ├── berat_time_desync/
│   ├── emin_auth_bypass/
│   ├── hasan_session_hijacking/
│   ├── kadir_can_injection/
│   ├── melik_replay_attack/
│   ├── merve_phantom_current/
│   ├── omer_zero_energy_flood/
│   └── ...
├── dashboard/               # React-based web interface
├── sui_admin/               # Sui Blockchain smart contracts (Move)
├── src/                     # Python-based core simulation engine
│   ├── api/                 # Backend API (FastAPI)
│   ├── core/                # OCPP logic and simulation core
│   ├── attacks/             # Shared attack libraries
│   ├── defense/             # Defense and anomaly detection modules
│   └── utils/               # Utility functions
├── run_all.py               # Main script to run simulations
├── requirements.txt         # Python dependencies
└── ...
```

---

## 💻 Technology Stack

| Layer | Technologies | Purpose |
|-------|--------------|---------|
| **Frontend** | React, Vite, Tailwind CSS, Recharts | User Interface and Visualization |
| **Backend** | Python (FastAPI, asyncio, websockets) | Simulation Engine and API |
| **Blockchain** | Sui (Move), Walrus | Data Integrity and Log Storage |
| **Protocol** | OCPP 1.6-J | EVSE Communication Standard |
| **Simulation** | Python, Scikit-learn, Pandas | Hardware simulation and AI Analysis |

---

## 🛠 Installation

The project requires both Python (backend) and Node.js (frontend) environments.

### Prerequisites
- Python 3.8+
- Node.js 18+
- [Sui CLI](https://docs.sui.io/guides/developer/getting-started/sui-install) (For blockchain features)

### 1. Backend Setup

```bash
# Clone the project
git clone https://github.com/salihtore/EVSE-Security-Lab.git
cd EVSE-Security-Lab

# Create a virtual environment
python -m venv .venv
# Activate the virtual environment
# For Windows:
.venv\Scripts\activate
# For Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend (Dashboard) Setup

```bash
cd dashboard
npm install
```

### 3. Blockchain Setup (Optional)
To transact on the Sui network, contracts in the `sui_admin` folder may need to be published. Necessary configurations are made via the `.env` file.

---

## ▶️ Usage

### Running Simulations

You can use the `run_all.py` script in the root directory to list and run all simulations:

```bash
# With virtual environment active
python run_all.py --help

# Run a specific scenario (e.g., thermal_manipulation)
python run_all.py --scenario ahmet_thermal_manipulation --mode attack
```

To run a single scenario directly:
```bash
python Simulasyon/ahmet_thermal_manipulation/scenario.py
```

### Starting the Dashboard

To access the cybersecurity dashboard:

```bash
cd dashboard
npm run dev
```
The application will usually run at `http://localhost:5173`.

---

## 🧪 Available Scenarios

The `Simulasyon` folder contains the following scenarios:

1.  **Thermal Manipulation (ahmet_thermal_manipulation):** Simulating overheating/cooling by ensuring sensor data manipulation.
2.  **Time Desynchronization (berat_time_desync):** Disrupting log consistency by manipulating timestamps.
3.  **Auth Bypass (emin_auth_bypass):** Attempts to bypass authorization mechanisms.
4.  **Session Hijacking (hasan_session_hijacking):** Taking over active charging sessions.
5.  **CAN Injection (kadir_can_injection):** Injecting malicious messages into the CAN bus network.
6.  **Replay Attack (melik_replay_attack):** Performing operations by re-sending past messages.
7.  **Phantom Current (merve_phantom_current):** Injecting non-existent current data.
8.  **Zero Energy Flood (omer_zero_energy_flood):** Overwhelming the system with zero energy consumption data.
9.  **Attack Automation (mahmut_attack_automation):** Automated attack sequences.

---

## 🤝 Contributing

1.  Create a new folder under `Simulasyon/` for a new scenario (use English or consistent naming).
2.  Create your `scenario.py` file according to the standards.
3.  Format your code according to PEP8 standards.
4.  Pull the latest changes with `git pull` before opening a Pull Request (PR).