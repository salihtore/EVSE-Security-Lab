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


async def attack_flow(victim_cp: SimulatedChargePoint, attacker_ws):
    """
    Saldırı Akışı:
    1. Kurban normal şarj başlatır
    2. Saldırgan transaction ID'yi ele geçirir (dinleme/replay)
    3. Saldırgan çalınan transaction ID ile MeterValues gönderir
    4. Saldırgan oturumu kapatır (idTag mismatch)
    """
    try:
        # ==================== PHASE 1: Normal Kullanıcı Başlatıyor ====================
        logger.info("\n📱 [KURBAN] Kullanıcı şarj oturumu başlatıyor...")
        await victim_cp.send_boot_notification()
        await asyncio.sleep(1)
        
        await victim_cp.start_charging()
        await asyncio.sleep(2)
        
        # İlk birkaç MeterValues normal gönderiliyor
        logger.info("\n⚡ [KURBAN] Normal şarj devam ediyor...")
        for i in range(3):
            await victim_cp.simulate_meter_values(step_kwh=0.5)
            await asyncio.sleep(2)
        
        # ==================== PHASE 2: Saldırgan Dinliyor / TransactionID Ele Geçiriyor ====================
        logger.warning("\n" + "=" * 80)
        logger.warning("🔴 SALDIRI BAŞLIYOR: Saldırgan ağ trafiğini dinledi!")
        logger.warning(f"🕵️ TransactionID ele geçirildi: {victim_cp.transaction_id}")
        logger.warning(f"🕵️ IdTag ele geçirildi: {victim_cp.id_tag}")
        logger.warning("=" * 80)
        
        await asyncio.sleep(2)
        
        # ==================== PHASE 3: Saldırgan Oturumu Devralıyor ====================
        logger.error("\n🚨 SALDIRGAN OTURUMU DEVRALıYOR...")
        
        # Saldırgan kendi cihazını (farklı CP) kullanarak bağlanıyor
        attacker_cp = HijackerChargePoint(
            "CP_HASAN_ATTACKER",
            attacker_ws,
            stolen_transaction_id=victim_cp.transaction_id,  # ÇALINMIŞ TRANSACTION ID
            stolen_id_tag=victim_cp.id_tag,
        )
        
        # Saldırganın connection'ı başlat (listener)
        asyncio.create_task(attacker_cp.start())
        await asyncio.sleep(1)
        
        await attacker_cp.send_boot_notification()
        await asyncio.sleep(1)
        
        # Saldırgan çalınan transaction ID ile MeterValues gönderiyor
        logger.error("\n🔴 PHASE 1: Saldırgan MeterValues gönderiyor (farklı connector/cihaz)...")
        for i in range(3):
            await attacker_cp.hijack_meter_values()
            await asyncio.sleep(2)
        
        # ==================== PHASE 4: Anomali Tespiti Beklenen Durumlar ====================
        logger.warning("\n⚠️ BEKLENEN ANOMALİLER:")
        logger.warning("  1. Aynı transactionId için farklı connector ID kullanıldı")
        logger.warning("  2. Aynı transactionId için farklı IP adresinden bağlantı")
        logger.warning("  3. Sayaç değerlerinde mantıksız artış/azalış")
        logger.warning("  4. Gerçek kullanıcı oturumu devam ederken saldırgan da mesaj gönderiyor")
        
        await asyncio.sleep(2)
        
        # ==================== PHASE 5: Saldırgan Oturumu Kapatıyor (idTag Mismatch) ====================
        logger.error("\n🔴 PHASE 2: Saldırgan oturumu kapatıyor (YANLIŞ ID TAG ile)...")
        await attacker_cp.hijack_stop_transaction(use_wrong_id_tag=True)
        
        logger.error("\n⚠️ BEKLENEN ANOMALİ:")
        logger.error(f"  - StopTransaction idTag mismatch: Beklenen={victim_cp.id_tag}, Gelen={attacker_cp.hijacker_id_tag}")
        
        await asyncio.sleep(2)
        
        # ==================== PHASE 6: Gerçek Kullanıcı Oturumun Çalındığını Fark Ediyor ====================
        logger.warning("\n📱 [KURBAN] Kullanıcı şarj devam ettirmeye çalışıyor ama oturum çalınmış!")
        try:
            await victim_cp.simulate_meter_values()
        except Exception as e:
            logger.error(f"❌ Kurban mesaj gönderemiyor - oturum geçersiz: {e}")
        
        # ==================== SALDIRI SONUÇ ====================
        logger.error("\n" + "=" * 80)
        logger.error("🚨 SALDIRI TAMAMLANDI: SESSION HIJACKING BAŞARILI")
        logger.error("=" * 80)
        logger.error("\n📊 SALDIRI SONUÇLARI:")
        logger.error("  ❌ Gerçek kullanıcı oturumu kaybetti")
        logger.error("  ❌ Faturalama verisi manipüle edildi")
        logger.error("  ❌ Saldırgan bedava şarj aldı")
        logger.error("  ❌ Loglarda tutarsızlıklar oluştu")
        logger.error("\n🔍 TESPİT EDİLMESİ GEREKEN İZLER (IoC):")
        logger.error("  1. Aynı transactionId, farklı connector/IP")
        logger.error("  2. IdTag mismatch (StopTransaction)")
        logger.error("  3. Sayaç değerlerinde anormal değişimler")
        logger.error("  4. Replay edilmiş mesajlar (aynı timestamp/payload)")
        logger.error("=" * 80 + "\n")
        
    except Exception as e:
        logger.error(f"❌ Saldırı akışı hatası: {e}")


# ============================================================================
# Ana Koşucu Fonksiyon
# ============================================================================

def run_scenario(mode: str = "normal"):
    """
    Senaryo koşucu
    
    Args:
        mode: "normal" veya "attack"
    """
    if mode == "attack":
        logger.warning("\n⚠️⚠️⚠️ SALDIRI MODU SEÇİLDİ ⚠️⚠️⚠️\n")
        asyncio.run(run_attack())
    else:
        logger.info("\n✅ NORMAL MOD SEÇİLDİ\n")
        asyncio.run(run_normal())


if __name__ == "__main__":
    # Test için doğrudan çalıştırılabilir
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "normal"
    run_scenario(mode)