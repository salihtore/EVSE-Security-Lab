import asyncio
import logging
from datetime import datetime

try:
    import websockets
except ImportError:
    print("Websockets kütüphanesi eksik!")

from ocpp.v16 import ChargePoint as Cp
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus

# --- AYARLAR ---
SCENARIO_NAME = "sensor_fusion_mismatch_phantom_obj"
CP_ID = "CP_OTONOM_01"  
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

            # 1. BOOT NOTIFICATION 
            print(">> BootNotification gönderiliyor...")
            # DÜZELTME: İsim 'Autonomous_EV_Charger' (21 karakter) yerine
            # 'Auto_EV_Charger' (15 karakter) yapıldı. Sınır 20 karakterdir.
            boot_request = call.BootNotification(
                charge_point_model="Auto_EV_Charger",
                charge_point_vendor="Huawei_Cloud_Lab"
            )
            response = await cp.call(boot_request)
            
            if response.status == RegistrationStatus.accepted:
                logging.info("BootNotification KABUL EDİLDİ.")
                
                # 2. STATUS
                await cp.call(call.StatusNotification(connector_id=1, error_code="NoError", status="Available"))
                await asyncio.sleep(0.5)
                await cp.call(call.StatusNotification(connector_id=1, error_code="NoError", status="Preparing"))
                
                # 3. START TRANSACTION
                print(">> Şarj işlemi başlatılıyor...")
                start_request = call.StartTransaction(
                    connector_id=1,
                    id_tag="AUTH_SENS_01",
                    meter_start=0,
                    timestamp=datetime.utcnow().isoformat()
                )
                start_response = await cp.call(start_request)
                transaction_id = start_response.transaction_id
                print(f">> Transaction ID alındı: {transaction_id}")
                
                await cp.call(call.StatusNotification(connector_id=1, error_code="NoError", status="Charging"))

                # 4. NORMAL VERİ AKIŞI
                for i in range(3):
                    await asyncio.sleep(1.5)
                    print(f">> MeterValue {i+1} gönderiliyor...")
                    await cp.call(call.MeterValues(
                        connector_id=1,
                        transaction_id=transaction_id,
                        meter_value=[{
                            "timestamp": datetime.utcnow().isoformat(),
                            "sampled_value": [{"value": str(10 + i * 2), "unit": "Wh"}]
                        }]
                    ))

                # --- ANOMALİ ANI ---
                print("\n!!! ANOMALİ TESPİT EDİLDİ: Kamera/LiDAR Uyuşmazlığı !!!")
                print("!!! SİSTEM ACİL DURDURULUYOR (FAIL-SAFE) !!!\n")
                await asyncio.sleep(1)

                # 5. STOP TRANSACTION
                await cp.call(call.StopTransaction(
                    meter_stop=50,
                    timestamp=datetime.utcnow().isoformat(),
                    transaction_id=transaction_id,
                    reason="EmergencyStop",
                    id_tag="AUTH_SENS_01"
                ))
                print(">> StopTransaction gönderildi.")

                # 6. SON DURUM: FAULTED
                await cp.call(call.StatusNotification(
                    connector_id=1,
                    error_code="OtherError",
                    info="SensorAnomaly", 
                    status="Faulted" 
                ))
                print(">> İstasyon 'Faulted' moduna alındı.")
                
            else:
                print("BootNotification reddedildi!")

    except ConnectionRefusedError:
        print("\nHATA: Sunucu kapalı! Önce csms.py dosyasını çalıştırın.")
    except Exception as e:
        print(f"\nBEKLENMEYEN HATA: {e}")

if __name__ == "__main__":
    asyncio.run(run_scenario())