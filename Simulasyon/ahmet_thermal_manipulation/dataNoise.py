import asyncio
import logging
import random
from datetime import datetime

try:
    import websockets
except ImportError:
    print("Websockets kütüphanesi eksik!")

from ocpp.v16 import ChargePoint as Cp
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus

# --- AYARLAR ---
SCENARIO_NAME = "sensor_glare_noise_injection"
# ID'yi değiştirdik ki öncekiyle karışmasın
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

            # 1. BOOT NOTIFICATION
            # Model ismini 20 karakterin altına indirdik (Auto_Glare_Test)
            print(">> BootNotification gönderiliyor...")
            boot_request = call.BootNotification(
                charge_point_model="Auto_Glare_Test",
                charge_point_vendor="Huawei_Cloud"
            )
            response = await cp.call(boot_request)

            if response.status == RegistrationStatus.accepted:
                print(">> BootNotification KABUL EDİLDİ.")
                
                # 2. STATUS ZİNCİRİ
                await cp.call(call.StatusNotification(connector_id=1, error_code="NoError", status="Available"))
                await asyncio.sleep(0.5)
                await cp.call(call.StatusNotification(connector_id=1, error_code="NoError", status="Preparing"))
                
                # 3. START TRANSACTION
                print(">> Şarj işlemi başlatılıyor...")
                start_request = call.StartTransaction(
                    connector_id=1,
                    id_tag="GLARE_TEST_01",
                    meter_start=0,
                    timestamp=datetime.utcnow().isoformat()
                )
                start_resp = await cp.call(start_request)
                tx_id = start_resp.transaction_id
                print(f">> Şarj Başladı. Tx ID: {tx_id}")

                await cp.call(call.StatusNotification(connector_id=1, error_code="NoError", status="Charging"))

                # 4. METER VALUES (PARAZİT SİMÜLASYONU)
                # Raporda belirtilen "Ani ışık parlamaları"nı simüle ediyoruz
                
                current_energy = 0
                print(">> Veri akışı başlıyor (Gürültülü Veri Enjekte Ediliyor)...")
                
                for i in range(5): 
                    await asyncio.sleep(1.5)
                    
                    # Normal artış yerine ani sıçramalar (Spikes)
                    if i == 2:
                        # ANOMALİ ANI: Parlama kaynaklı hatalı sensör okuması
                        spike_value = 9999.9 
                        print(f"!!! PARLAMA SİMÜLASYONU: Hatalı Veri Gönderiliyor ({spike_value} Wh) !!!")
                    else:
                        spike_value = current_energy + 5.0
                        print(f">> Normal veri: {spike_value} Wh")

                    current_energy = spike_value

                    # Voltajda dalgalanma (220V +/- 50V) - Gürültü
                    voltage_noise = 220 + random.randint(-50, 50)

                    await cp.call(call.MeterValues(
                        connector_id=1,
                        transaction_id=tx_id,
                        meter_value=[{
                            "timestamp": datetime.utcnow().isoformat(),
                            "sampled_value": [
                                # Enerji değeri
                                {"value": str(current_energy), "context": "Sample.Periodic", "format": "Raw", "measurand": "Energy.Active.Import.Register", "unit": "Wh"},
                                # Voltaj değeri (Parazitli)
                                {"value": str(voltage_noise), "measurand": "Voltage", "unit": "V"} 
                            ]
                        }]
                    ))

                # 5. STOP TRANSACTION
                # Anomali sonrası güvenli duruş
                print(">> Güvenli modda durduruluyor...")
                await cp.call(call.StopTransaction(
                    meter_stop=int(current_energy),
                    timestamp=datetime.utcnow().isoformat(),
                    transaction_id=tx_id,
                    reason="Other", # Anomali sebebiyle belirsiz duruş
                    id_tag="GLARE_TEST_01"
                ))
                print(">> StopTransaction gönderildi.")

                # 6. STATUS ZİNCİRİ
                await cp.call(call.StatusNotification(connector_id=1, error_code="NoError", status="Finishing"))
                await asyncio.sleep(1)
                
                # Parlama geçtiği için tekrar Available moda dönüyor
                await cp.call(call.StatusNotification(connector_id=1, error_code="NoError", status="Available"))
                print(">> Senaryo tamamlandı.")
            
            else:
                print("Boot reddedildi.")

    except ConnectionRefusedError:
         print("\nHATA: Sunucu kapalı! Önce csms.py dosyasını çalıştırın.")
    except Exception as e:
         print(f"\nBEKLENMEYEN HATA: {e}")

if __name__ == "__main__":
    asyncio.run(run_scenario())