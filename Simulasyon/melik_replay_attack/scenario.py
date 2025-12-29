import asyncio
import websockets
import logging
from .charge_point import MelikReplayCP
from ocpp.v16.enums import ChargePointStatus

# Standart Tanımlayıcılar [cite: 201-203]
SCENARIO_NAME = "replay_attack" 
CP_ID = "CP_MELIK"
WS_URL = f"ws://localhost:9000/{CP_ID}"

async def run_scenario(mode="normal"):
    """Senaryoyu normal veya saldırı modunda koşturur.""" [cite: 109, 151]
    async with websockets.connect(WS_URL, subprotocols=["ocpp1.6"]) as ws:
        cp = MelikReplayCP(CP_ID, ws)
        asyncio.create_task(cp.start()) [cite: 210]

        # 1. FAZ: Boot ve Başlangıç [cite: 216]
        await cp.send_boot()
        await cp.update_status(ChargePointStatus.available)
        
        # 2. FAZ: İlk Meşru Erişim [cite: 280]
        logging.info(">>> Meşru kullanıcı kartını okutuyor...")
        auth_response = await cp.send_authorize()
        
        if auth_response.id_tag_info['status'] == 'Accepted':
            await cp.update_status(ChargePointStatus.charging)
            logging.info(">>> Şarj başladı.")
            await asyncio.sleep(3) # Şarj süresi simülasyonu

        # 3. FAZ: Saldırı (Replay) [cite: 282, 301]
        if mode == "attack":
            logging.warning("!!! KRİTİK: Saldırgan yakaladığı paketi tekrar gönderiyor (Replay) !!!")
            # Aynı Authorize paketi tekrar gönderiliyor
            await cp.send_authorize() 
            # Not: Sistemde Freshness/Nonce kontrolü yoksa bu işlem başarılı olur 
            await asyncio.sleep(2)

        # 4. FAZ: Kapatış [cite: 221]
        await cp.update_status(ChargePointStatus.available)
        logging.info(f"Senaryo ({mode}) başarıyla tamamlandı.")
