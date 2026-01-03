# Simulasyon/semih_yetim_seans/scenario.py

import asyncio
import logging

logging.basicConfig(level=logging.INFO)

SCENARIO_NAME = "semih_yetim_seans"

async def run_scenario(mode, adapter):
    cp_id = adapter.cp_id

    # 1️⃣ StartTransaction
    adapter.emit(
        "StartTransaction",
        {
            "transactionId": 1001,
            "idTag": "SEMIH_TAG",
            "plug_state": True
        }
    )

    await asyncio.sleep(1)

    # 2️⃣ MeterValues (Fiş Takılı)
    adapter.emit(
        "MeterValues",
        {
            "transactionId": 1001,
            "meterValue": [{"sampledValue": [{"value": "5"}]}],
            "plug_state": True
        }
    )
    
    await asyncio.sleep(2)

    # 3️⃣ Fiş Çekildi (UNPLUGGED) ama StopTransaction YOK
    logging.info("🔌 [SEMIH] Fiş çekildi! (Plug State: False)")
    adapter.emit(
        "MeterValues",
        {
            "transactionId": 1001,
            "meterValue": [{"sampledValue": [{"value": "5"}]}],
            "plug_state": False # KRİTİK: Detector buradan zaman saymaya başlar
        }
    )

    # 4️⃣ ORPHAN_SESSION timeout bekle (30 sn limitini geçmek için 32 sn bekliyoruz)
    logging.info("⏳ [SEMIH] Yetim Seans tespiti bekleniyor (32 sn)...")
    await asyncio.sleep(32)

    # 5️⃣ Trigger Event (Heartbeat)
    # Dedektör, "Fiş çekildi ve hala Stop gelmedi" durumunu bu event gelince fark edecek
    adapter.emit(
        "Heartbeat",
        {
            "plug_state": False
        }
    )
    
    logging.info("🚨 [SEMIH] Senaryo tamamlandı. Alarm bekleniyor.")



#python run_all.py --scenario semih_yetim_seans --mode attack