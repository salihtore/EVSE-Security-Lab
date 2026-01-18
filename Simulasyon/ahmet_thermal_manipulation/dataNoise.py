import asyncio
import logging
import random
import time
from datetime import datetime

try:
    import websockets
except ImportError:
    print("Websockets kütüphanesi eksik!")

from ocpp.v16 import ChargePoint as Cp
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus

# 🔗 CORE BAĞLANTISI
from Simulasyon.core.forward_to_real_core import forward_event

# --- AYARLAR ---
SCENARIO_NAME = "sensor_glare_noise_injection"
CP_ID = "CP_GLARE_01"
WS_URL = f"ws://localhost:9000/{CP_ID}"

logging.basicConfig(level=logging.INFO)


class EvilCP(Cp):
    pass


async def run_scenario():
    print(f"--- {SCENARIO_NAME} BAŞLATILIYOR ---")
    print(f"Hedef: {WS_URL}")

    try:
        async with websockets.connect(WS_URL, subprotocols=["ocpp1.6"]) as ws:
            print(">> Bağlantı sağlandı!")
            cp = EvilCP(CP_ID, ws)
            asyncio.create_task(cp.start())

            # 1) BOOT
            print(">> BootNotification gönderiliyor...")
            boot_request = call.BootNotification(
                charge_point_model="Auto_Glare_Test",
                charge_point_vendor="Huawei_Cloud"
            )
            response = await cp.call(boot_request)

            if response.status != RegistrationStatus.accepted:
                print("Boot reddedildi.")
                return

            print(">> Boot KABUL EDİLDİ.")

            # 2) STATUS
            await cp.call(call.StatusNotification(
                connector_id=1, error_code="NoError", status="Available"
            ))
            await asyncio.sleep(0.5)
            await cp.call(call.StatusNotification(
                connector_id=1, error_code="NoError", status="Preparing"
            ))

            # 3) START TRANSACTION
            start_request = call.StartTransaction(
                connector_id=1,
                id_tag="GLARE_TEST_01",
                meter_start=0,
                timestamp=datetime.utcnow().isoformat()
            )
            start_resp = await cp.call(start_request)
            tx_id = start_resp.transaction_id
            print(f">> Tx ID: {tx_id}")

            await cp.call(call.StatusNotification(
                connector_id=1, error_code="NoError", status="Charging"
            ))

            # 4) METER VALUES + NOISE
            current_energy = 0

            for i in range(5):
                await asyncio.sleep(1.5)

                if i == 2:
                    # 🔥 ANOMALİ ANI
                    spike_value = 9999.9
                    voltage_noise = 220 + random.randint(-50, 50)

                    print("!!! GLARE NOISE ANOMALİSİ ENJEKTE EDİLİYOR !!!")

                    forward_event({
                        "event_id": int(time.time() * 1000),
                        "timestamp": time.time(),
                        "cp_id": CP_ID,
                        "scenario": SCENARIO_NAME,
                        "event_type": "SENSOR_ANOMALY",
                        "message_type": "GLARE_NOISE_INJECTION",
                        "payload": {
                            "energy_spike": spike_value,
                            "voltage_noise": voltage_noise,
                            "reason": "Optical glare causing sensor noise"
                        }
                    })
                else:
                    spike_value = current_energy + 5.0
                    voltage_noise = 220 + random.randint(-10, 10)

                current_energy = spike_value

                await cp.call(call.MeterValues(
                    connector_id=1,
                    transaction_id=tx_id,
                    meter_value=[{
                        "timestamp": datetime.utcnow().isoformat(),
                        "sampled_value": [
                            {"value": str(current_energy), "measurand": "Energy.Active.Import.Register", "unit": "Wh"},
                            {"value": str(voltage_noise), "measurand": "Voltage", "unit": "V"}
                        ]
                    }]
                ))

            # 5) STOP
            await cp.call(call.StopTransaction(
                meter_stop=int(current_energy),
                timestamp=datetime.utcnow().isoformat(),
                transaction_id=tx_id,
                reason="Other",
                id_tag="GLARE_TEST_01"
            ))

            await cp.call(call.StatusNotification(
                connector_id=1, error_code="NoError", status="Available"
            ))

            print(">> Senaryo tamamlandı.")

    except ConnectionRefusedError:
        print("\nHATA: CSMS kapalı!")
    except Exception as e:
        print(f"\nBEKLENMEYEN HATA: {e}")


if __name__ == "__main__":
    asyncio.run(run_scenario())
