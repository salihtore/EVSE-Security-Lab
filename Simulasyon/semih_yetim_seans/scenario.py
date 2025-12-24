# Simulasyon/semih_yetim_seans/scenario.py

import asyncio

SCENARIO_NAME = "semih_yetim_seans"

async def run_scenario(mode, adapter):
    cp_id = adapter.cp_id

    # 1️⃣ StartTransaction
    adapter.emit(
        "StartTransaction",
        {
            "transactionId": 1001,
            "idTag": "SEMIH_TAG"
        }
    )

    await asyncio.sleep(1)

    # 2️⃣ MeterValues
    adapter.emit(
        "MeterValues",
        {
            "transactionId": 1001,
            "meterValue": [
                {"sampledValue": [{"value": "5"}]}
            ]
        }
    )

    # 3️⃣ Fiş çekildi ama StopTx yok
    adapter.emit(
        "CONNECTION_LOST",
        {
            "transaction_id": 1001,
            "session_active": True,
            "reason": "Cable unplugged without StopTransaction"
        }
    )

    # 4️⃣ ORPHAN_SESSION timeout bekle
    await asyncio.sleep(35)

    # 5️⃣ ORPHAN_SESSION ALARM ÜRET (UI BURADAN BESLENİR)
    await asyncio.sleep(35)

    adapter.emit_alarm(
    anomaly_type="ORPHAN_SESSION",
    severity="MEDIUM",
    details={
        "reason": "Session active but StopTransaction never received",
        "transaction_id": 1001,
        "timeout_sec": 30
    }
)





    # 5️⃣ Senaryo bitti (opsiyonel)
    adapter.emit(
        "SCENARIO_END",
        {
            "info": "Scenario finished after orphan-session timeout"
        }
    )



#python run_all.py --scenario semih_yetim_seans --mode attack