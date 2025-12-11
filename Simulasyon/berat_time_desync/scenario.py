# Dosya: Simulasyon/berat_time_desync/scenario.py
import asyncio
import logging
# Modülleri içe aktar
from .payload_generator import get_manipulated_data 
from .cp_simulator import cp_event_flow            

logging.basicConfig(level=logging.INFO)

# --- SENARYO KOŞUCU FONKSİYONLARI ---

async def run_attack():
    """Zaman Kaydırma ve Değer Düşürme saldırı modunu başlatır."""
    print("\n[SCENARIO] 💣 ZAMAN KAYDIRMA SALDIRISI BAŞLADI (Çift Anomali)")
    
    # cp_event_flow'u çağır ve manipülasyon verisini alacağı fonksiyonu ver
    await cp_event_flow(mode="ATTACK", get_manipulated_data=get_manipulated_data)
    
    print("[SCENARIO] Saldırı simülasyonu tamamlandı.")

async def run_normal():
    """Anomalisiz normal akışı başlatır."""
    
    print("\n[SCENARIO] 🟢 NORMAL MOD BAŞLADI (Anomalisiz Akış)")
    
    # Normal modda, manipülasyon verisi fonksiyonunu göndermiyoruz
    await cp_event_flow(mode="NORMAL")
    
    print("[SCENARIO] Normal simülasyon tamamlandı.")


def run_scenario(scenario="attack"):
    """Ana motor (run_all.py) tarafından çağrılan giriş noktası."""
    if scenario == "normal":
        asyncio.run(run_normal())
    else:
        asyncio.run(run_attack())
