# Dosya: Simulasyon/berat_time_desync/cp_simulator.py
import asyncio
import time

# Core sistem fonksiyonları
from core.core_cp import send_message_to_core


async def send_meter_values(cp_id: str, count: int, mode: str, get_manipulated_data=None):
    """
    MeterValue gönderir.
    NORMAL mod: sabit 50.0 kWh
    ATTACK mod: manipüle edilmiş payload
    """

    for i in range(count):
        await asyncio.sleep(1)

        if mode.upper() == "ATTACK" and get_manipulated_data:
            payload = get_manipulated_data(cp_id)
            print(f"[CP_{cp_id}] 💣 Anomali MeterValue gönderildi ({i+1}/{count}).")
        else:
            payload = {
                "timestamp": time.time(),
                "senaryo": "TimeDesync",
                "cp_id": cp_id,
                "message_type": "MeterValue",
                "value": 50.0,
                "source": "CP"
            }
            print(f"[CP_{cp_id}] 🟢 Normal MeterValue gönderildi ({i+1}/{count}).")

        await send_message_to_core(payload)


async def cp_event_flow(mode="NORMAL", get_manipulated_data=None):
    """
    CP Akışı:
    ❌ Artık StartTransaction göndermiyoruz!
    ✔ Core onu zaten otomatik gönderiyor.
    ✔ Biz sadece MeterValue gönderiyoruz.
    """

    cp_id = "CP_BERAT"

    print(f"\n[CP_{cp_id}] 🚫 StartTransaction gönderilmiyor (Core gönderecek).")

    # Sadece MeterValue gönder
    await send_meter_values(cp_id, 3, mode, get_manipulated_data)

    print(f"[CP_{cp_id}] ✅ Senaryo Akışı Tamamlandı.")
