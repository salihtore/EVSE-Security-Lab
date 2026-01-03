# Dosya: Simulasyon/berat_time_desync/cp_simulator.py
import asyncio
import time
import random
from src.core.scenario_adapter import ScenarioAdapter

# Core sistem fonksiyonları
from Simulasyon.core.forward_to_real_core import forward_event

CP_ID = "CP_BERAT"
SCENARIO_NAME = "berat_time_desync"


async def send_meter_values(
    cp_id: str,
    count: int,
    mode: str,
    adapter: ScenarioAdapter,
    get_manipulated_data=None
):
    for i in range(1, count + 1):
        await asyncio.sleep(1)

        if mode.upper() == "ATTACK" and get_manipulated_data:
            # Drifting için iterasyon sayısı gönderiliyor
            payload = get_manipulated_data(cp_id, i)
            print(f"[CP_{cp_id}] 💣 Anomali MeterValues gönderildi ({i}/{count}).")
        else:
            payload = {
                "transactionId": 42,
                "cp_timestamp": time.time(),
                "csms_time": time.time(),
                "meterValue": [{"sampledValue": [{"value": "50"}]}],
                "note": "NORMAL_METERVALUES"
            }
            print(f"[CP_{cp_id}] 🟢 Normal MeterValues gönderildi ({i}/{count}).")

        # KRİTİK: forward_event YOK, adapter.emit VAR
        alarms = adapter.emit(message_type="MeterValues", payload=payload)
        if alarms:
            print(f"[CP_{cp_id}] 🚨 Üretilen alarmlar: {alarms}")


    forward_event(payload)


async def cp_event_flow(mode="NORMAL", adapter: ScenarioAdapter = None, get_manipulated_data=None):
    if adapter is None:
        adapter = ScenarioAdapter(cp_id=CP_ID, scenario_name=SCENARIO_NAME)

    print(f"\n[CP_{CP_ID}] 📡 Senaryo akışı başlatılıyor...")
    await send_meter_values(CP_ID, 3, mode, adapter, get_manipulated_data)
    print(f"[CP_{CP_ID}] ✅ Senaryo Akışı Tamamlandı.")



if __name__ == "__main__":
    asyncio.run(cp_event_flow(mode="NORMAL"))

    
