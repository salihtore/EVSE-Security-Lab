"""
EVSE Security Lab - Session Hijacking Scenario
Scenario Runner
Author: Hasan Sido

SENARYO: Oturum Çalma (Session Hijacking)
- Normal mod: Kullanıcı normal şarj akışını tamamlar
- Attack mod: Saldırgan aktif oturumu ele geçirip devralır
"""

import asyncio
import logging
import websockets
from src.core.scenario_adapter import ScenarioAdapter
from .charge_point import SimulatedChargePoint, HijackerChargePoint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# NORMAL MOD: Güvenli Şarj Akışı
# ============================================================================

async def run_normal():
    """Normal kullanıcı şarj oturumu - Anomali yok"""
    uri = "ws://127.0.0.1:9000/CP_HASAN_NORMAL"
    
    logger.info("=" * 80)
    logger.info("✅ NORMAL MOD BAŞLATILIYOR - Güvenli Şarj Oturumu")
    logger.info("=" * 80)
    
    try:
        async with websockets.connect(uri, subprotocols=["ocpp1.6"]) as ws:
            cp = SimulatedChargePoint("CP_HASAN_NORMAL", ws)
            
            await asyncio.gather(
                cp.start(),  # CSMS'ten gelen mesajları dinle
                normal_flow(cp),  # Normal şarj akışı
            )
    except Exception as e:
        logger.error(f"❌ Bağlantı hatası: {e}")


async def normal_flow(cp: SimulatedChargePoint):
    """Normal şarj akışı: Boot -> Start -> MeterValues -> Stop"""
    try:
        # 1. Boot Notification
        await cp.send_boot_notification()
        await asyncio.sleep(1)
        
        # 2. Şarj Başlat
        logger.info("\n🔋 Kullanıcı şarj oturumu başlatıyor...")
        await cp.start_charging()
        await asyncio.sleep(2)
        
        # 3. Şarj devam ediyor - MeterValues gönder
        logger.info("\n⚡ Şarj devam ediyor, MeterValues gönderiliyor...")
        for i in range(5):
            await cp.simulate_meter_values(step_kwh=0.5)
            await asyncio.sleep(2)
        
        # 4. Şarj Sonlandır
        logger.info("\n🛑 Kullanıcı şarj oturumunu sonlandırıyor...")
        await cp.stop_charging()
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ NORMAL MOD TAMAMLANDI - Anomali tespit edilmedi")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Normal akış hatası: {e}")


# ============================================================================
# ATTACK MOD: Session Hijacking (Oturum Çalma)
# ============================================================================

async def run_attack():
    """Saldırı senaryosu: Aktif oturum ele geçirilip devralınıyor"""
    logger.info("=" * 80)
    logger.info("🚨 SALDIRI MODU BAŞLATILIYOR - SESSION HIJACKING")
    logger.info("=" * 80)
    
    # Gerçek kullanıcı bağlantısı
    victim_uri = "ws://127.0.0.1:9000/CP_HASAN_VICTIM"
    # Saldırgan bağlantısı (farklı endpoint, farklı cihaz simülasyonu)
    attacker_uri = "ws://127.0.0.1:9000/CP_HASAN_ATTACKER"
    
    try:
        # Hem kurban hem saldırgan aynı anda bağlanacak
        async with websockets.connect(victim_uri, subprotocols=["ocpp1.6"]) as victim_ws, \
                   websockets.connect(attacker_uri, subprotocols=["ocpp1.6"]) as attacker_ws:
            
            victim_cp = SimulatedChargePoint("CP_HASAN_VICTIM", victim_ws)
            
            # Saldırgan için şimdilik placeholder (transaction ID elde edildikten sonra oluşturulacak)
            await asyncio.gather(
                victim_cp.start(),  # Kurban dinliyor
                attack_flow(victim_cp, attacker_ws),  # Saldırı akışı
            )
            
    except Exception as e:
        logger.error(f"❌ Saldırı senaryosu hatası: {e}")


# ============================================================================
# Ana Koşucu Fonksiyon (ScenarioRunner uyumlu)
# ============================================================================

async def attack_flow_with_adapter(victim_cp, attacker_ws, adapter):
    try:
        # ==================== PHASE 1: Normal Kullanıcı Başlatıyor ====================
        logger.info("\n📱 [KURBAN] Kullanıcı şarj oturumu başlatıyor...")
        await victim_cp.send_boot_notification()
        adapter.emit("BootNotification", {"model": "HASAN_VICTIM", "vendor": "SimuTech"})
        await asyncio.sleep(1)
        
        await victim_cp.start_charging()
        adapter.emit("StartTransaction", {"idTag": victim_cp.id_tag, "transactionId": victim_cp.transaction_id})
        await asyncio.sleep(2)
        
        # İlk birkaç MeterValues normal gönderiliyor
        logger.info("\n⚡ [KURBAN] Normal şarj devam ediyor...")
        for i in range(2):
            await victim_cp.simulate_meter_values(step_kwh=0.5)
            adapter.emit("MeterValues", {"transactionId": victim_cp.transaction_id, "meterValue": str(victim_cp.meter_value)})
            await asyncio.sleep(1)
        
        # ==================== PHASE 2: Saldırgan Dinliyor ====================
        logger.warning("\n🕵️ TransactionID ele geçirildi: " + str(victim_cp.transaction_id))
        
        # ==================== PHASE 3: Saldırgan Oturumu Devralıyor ====================
        logger.error("\n🚨 SALDIRGAN OTURUMU DEVRALıYOR...")
        
        attacker_cp = HijackerChargePoint(
            "CP_HASAN_ATTACKER",
            attacker_ws,
            stolen_transaction_id=victim_cp.transaction_id,
            stolen_id_tag=victim_cp.id_tag,
        )
        
        asyncio.create_task(attacker_cp.start())
        await asyncio.sleep(1)
        
        # 🛡️ Manuel Alarm Kaldırıldı - SessionHijackingDetector yakalayacak
        # adapter.emit_alarm(...)

        await attacker_cp.send_boot_notification()
        
        # Saldırgan çalınan transaction ID ile MeterValues gönderiyor (Düşük frekanslı sabotaj)
        logging.warning("\n🕸️ [ATTACK] Oturum 'Zombie' moduna alınıyor (Veri akışı yavaşlatıldı)...")
        for i in range(5):
            await attacker_cp.hijack_meter_values()
            adapter.emit("MeterValues", {"transactionId": victim_cp.transaction_id, "meterValue": "999"}, override_cp_id="CP_HASAN_ATTACKER")
            await asyncio.sleep(3) # Düşük frekans (Low frequency)
        
        # ==================== PHASE 4: StopTransaction YOK (Zombie Session) ====================
        logger.error("\n🕷️ SALDIRGAN OTURUMU KAPATMADI - ZOMBIE SESSION BIRAKILDI")
        logger.info("   (Gerçekçi Session Hijacking: Oturum açık bırakıldı, para/enerji kaybı sürüyor)")
        
    except Exception as e:
        logger.error(f"❌ Saldırı akışı hatası: {e}")

async def run_attack_with_adapter(adapter):
    victim_uri = "ws://127.0.0.1:9000/CP_HASAN_VICTIM"
    attacker_uri = "ws://127.0.0.1:9000/CP_HASAN_ATTACKER"
    
    try:
        async with websockets.connect(victim_uri, subprotocols=["ocpp1.6"]) as victim_ws, \
                   websockets.connect(attacker_uri, subprotocols=["ocpp1.6"]) as attacker_ws:
            
            victim_cp = SimulatedChargePoint("CP_HASAN_VICTIM", victim_ws)
            victim_cp_task = asyncio.create_task(victim_cp.start())
            
            await attack_flow_with_adapter(victim_cp, attacker_ws, adapter)
            
            await asyncio.sleep(1)
            victim_cp_task.cancel()
            
    except Exception as e:
        logger.error(f"❌ Senaryo hatası: {e}")

def run_scenario(mode: str = "attack", adapter: ScenarioAdapter = None):
    if mode == "normal":
        logger.info("Normal mod bu senaryo için şu an adapter ile optimize edilmedi.")
        # Basitlik için sadece attack modunu adapter ile çalıştırıyoruz
    else:
        asyncio.run(run_attack_with_adapter(adapter))

if __name__ == "__main__":
    import sys
    from src.core.scenario_adapter import ScenarioAdapter
    mode = sys.argv[1] if len(sys.argv) > 1 else "attack"
    adapter = ScenarioAdapter("CP_HASAN_VICTIM", "hasan_session_hijacking")
    run_scenario(mode, adapter)
