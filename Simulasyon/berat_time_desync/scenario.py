# Dosya: Simulasyon/berat_time_desync/scenario.py
import asyncio
import logging
import websockets
# Modülleri içe aktar
from .hacker import send_attack_data, REPORTED_CONSUMPTION_KWH 
from .istasyon import istasyon_logic

logging.basicConfig(level=logging.INFO)

# --- SENARYO PARAMETRELERİ ---
SENARYO_PATH = '/CP_BERAT'
SUNUCU_ADRESI = f'ws://localhost:9000{SENARYO_PATH}' 

async def run_attack():
    """Zaman Kaydırma ve Değer Düşürme saldırı modunu başlatır."""
    print("\n[SCENARIO] 💣 ZAMAN KAYDIRMA SALDIRISI BAŞLADI (Çift Anomali)")
    
    # 1. CP bağlantısını kur (istasyon.py)
    # 2. Saldırgan bağlantısını kur (hacker.py)
    
    try:
        # Aynı anda hem CP hem de Saldırgan CSMS'e bağlanmalı (Tek bir WebSocket üzerinden).
        # Ancak basitlik ve istikrar için, burada CP'nin kendisi saldırgan rolünü üstleniyor gibi gösterilir.
        # En temiz çözüm, CP'nin kendisinin saldırgan mantığını başlatmasıdır.
        async with websockets.connect(SUNUCU_ADRESI, subprotocols=['ocpp1.6']) as websocket:
            print(f"[SCENARIO] ✅ Bağlantı başarılı: {SUNUCU_ADRESI}")
            
            # Normal CP akışını başlat (Mesaj döngüsü)
            cp_task = asyncio.create_task(istasyon_logic(websocket, mode="ATTACK"))
            
            # Saldırı verilerini gönderme görevini başlat (Hacker/Anomali)
            attack_task = asyncio.create_task(send_attack_data(websocket))
            
            # Her iki görevin de bitmesini bekle
            await asyncio.gather(cp_task, attack_task)
            
    except ConnectionRefusedError:
        logging.error("[SCENARIO] ❌ Sunucuya bağlanılamadı. Core CSMS çalışmıyor olabilir.")
    except Exception as e:
        logging.error(f"[SCENARIO] Beklenmedik hata: {e}")

async def run_normal():
    """Anomalisiz normal akışı başlatır (Sadece güvenli CP davranışı)."""
    
    print("\n[SCENARIO] 🟢 NORMAL MOD BAŞLADI (Anomalisiz Akış)")
    
    try:
        async with websockets.connect(SUNUCU_ADRESI, subprotocols=['ocpp1.6']) as websocket:
            print(f"[SCENARIO] ✅ Bağlantı başarılı: {SUNUCU_ADRESI}")
            # Sadece güvenli CP mantığını çalıştır
            await istasyon_logic(websocket, mode="NORMAL")
            
    except ConnectionRefusedError:
        logging.error("[SCENARIO] ❌ Sunucuya bağlanılamadı. Core CSMS çalışmıyor olabilir.")
    except Exception as e:
        logging.error(f"[SCENARIO] Beklenmedik hata: {e}")


def run_scenario(scenario="attack"):
    """Ana motor (run_all.py) tarafından çağrılan giriş noktası."""
    if scenario == "normal":
        asyncio.run(run_normal())
    else:
        asyncio.run(run_attack())
