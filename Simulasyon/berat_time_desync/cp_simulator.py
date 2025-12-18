# Dosya: Simulasyon/berat_time_desync/cp_simulator.py
import asyncio
import time
import random

# Core sistem fonksiyonları
from core.core_cp import send_message_to_core

CP_ID = "CP_BERAT"
SCENARIO_NAME = "TimeDesync"


async def send_meter_values(cp_id: str, count: int, mode: str, get_manipulated_data=None):
    """
    MeterValue gönderir.
    NORMAL mod: sabit 50.0 kWh
    ATTACK mod: manipüle edilmiş payload
    """

    for i in range(1, count + 1):
        await asyncio.sleep(1)

        if mode.upper() == "ATTACK" and get_manipulated_data:
            payload = get_manipulated_data(cp_id)
            print(f"[CP_{cp_id}] 💣 Anomali MeterValue gönderildi ({i}/{count}).")
        else:
            payload = {
                "timestamp": time.time(),
                "senaryo": SCENARIO_NAME,
                "cp_id": cp_id,
                "message_type": "MeterValue",
                "value": 50.0,
                "source": "CP"
            }
            print(f"[CP_{cp_id}] 🟢 Normal MeterValue gönderildi ({i}/{count}).")

        await send_message_to_core(payload)


async def cp_event_flow(mode="NORMAL", get_manipulated_data=None):
    """
    CP Akışı:
    1) StartTransaction → artık core tarafından gönderiliyor
    2) 3 adet MeterValue
    """

    print(f"\n[CP_{CP_ID}] 📡 Senaryo akışı başlatılıyor...")
    await send_meter_values(CP_ID, 3, mode, get_manipulated_data)
    print(f"[CP_{CP_ID}] ✅ Senaryo Akışı Tamamlandı.")
