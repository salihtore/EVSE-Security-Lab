⚡ EVSE Security Lab

A Cyber-Physical Security Testing and Simulation Platform for Smart Charging Stations (EVSE)

EVSE Security Lab is a comprehensive cyber-physical security laboratory designed to analyze security vulnerabilities in electric vehicle charging infrastructures (EVSE), focusing on the OCPP (Open Charge Point Protocol) and related hardware components.
The platform enables simulation of cyber-attack scenarios and enhances system security through AI-driven defense mechanisms and blockchain-based immutable logging.

The project allows researchers and developers to design custom attack scenarios, simulate them in a controlled environment, and evaluate AI- and blockchain-based defense strategies.

🚀 Features

Advanced Attack Simulations
Predefined and extensible scenarios including thermal manipulation, time desynchronization, session hijacking, replay attacks, and more.

OCPP 1.6-J Support
Full simulation of communication between Charge Points (CP) and the Central Management System (CSMS).

Blockchain Integration (Sui)
Immutable security event logging using the Sui blockchain and Walrus (blob storage).

Live Monitoring Dashboard
Real-time visualization of attacks and system status via a modern React + Vite dashboard.

Modular Architecture
Easily extensible design for adding new attack scenarios or defense modules.

AI-Assisted Defense
Integrated machine learning models for anomaly detection and behavioral analysis.

📂 Project Structure
EVSE-Security-Lab/
├── Simulasyon/              # Attack and anomaly simulation scenarios
├── dashboard/               # React-based web dashboard
├── sui_admin/               # Sui blockchain smart contracts (Move)
├── src/                     # Python-based core simulation engine
│   ├── api/                 # Backend API
│   ├── core/                # OCPP logic and simulation core
│   ├── attacks/             # Shared attack utilities
│   └── defense/             # Defense and anomaly detection modules
├── run_all.py               # Main script to manage and run simulations
└── ...

💻 Technology Stack
Layer	Technologies	Purpose
Frontend	React, Vite, Tailwind CSS, Recharts	User interface & visualization
Backend	Python (asyncio, websockets)	Simulation engine & API
Blockchain	Sui (Move), Walrus	Data integrity & log storage
Protocol	OCPP 1.6-J	EVSE communication standard
Simulation	Python, CAN Bus libraries	Hardware & network simulation
🛠 Installation

The project requires both Python (backend) and Node.js (frontend) environments.

Prerequisites

Python 3.8+

Node.js 18+

Sui CLI (for blockchain-related features)

1. Backend Setup
# Clone the repository
git clone https://github.com/salihtore/EVSE-Security-Lab.git
cd EVSE-Security-Lab

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

2. Frontend (Dashboard) Setup
cd dashboard
npm install

3. Blockchain Setup (Optional)

To enable blockchain features, smart contracts under the sui_admin directory may need to be deployed on the Sui network.
Relevant configurations are managed via the .env file.

▶️ Usage
Running Simulations

To list and execute simulations, use the run_all.py script from the project root:

# With virtual environment activated
python run_all.py --help


Run a specific scenario (example: thermal manipulation):

python run_all.py --scenario ahmet_thermal_manipulation --mode attack


To execute a single scenario directly:

python Simulasyon/ahmet_thermal_manipulation/scenario.py

Starting the Dashboard
cd dashboard
npm run dev


The dashboard is typically available at:
http://localhost:5173

🧪 Available Scenarios

The Simulasyon/ directory contains the following (and more):

Thermal Manipulation – Simulating overheating/overcooling via sensor spoofing

Time Desync – Timestamp manipulation to disrupt log consistency

Auth Bypass – Attempts to bypass authorization mechanisms

Session Hijacking – Taking over active charging sessions

Phantom Current – Injecting fake current measurements

Zero Energy Flood – Flooding the system with zero-consumption sessions

Replay Attack – Replaying previously captured protocol messages

🤝 Contributing

To add a new scenario:

Create a new folder under Simulasyon/ (avoid non-ASCII characters).

Implement your scenario.py according to the project standards.

Format your code following PEP8 guidelines.

Before opening a Pull Request (PR), synchronize with the latest changes:

git pull
