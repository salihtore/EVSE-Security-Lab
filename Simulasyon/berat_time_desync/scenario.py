# Dosya: Simulasyon/berat_time_desync/scenario.py
import asyncio
import logging
# Modülleri içe aktar
from .payload_generator import get_manipulated_data 
from .cp_simulator import cp_event_flow      

from typing import Optional
import time
from src.core.scenario_adapter import ScenarioAdapter


logging.basicConfig(level=logging.INFO)

# --- SENARYO KOŞUCU FONKSİYONLARI ---

async def run_attack(adapter: Optional[ScenarioAdapter] = None):
    """Zaman Kaydırma ve Değer Düşürme saldırı modunu başlatır."""
    print("\n[SCENARIO] 💣 ZAMAN KAYDIRMA SALDIRISI BAŞLADI (Çift Anomali)")
    


    # ================================
    #  TIME DESYNC KANIT EVENT'İ
    # ================================
    if adapter:
        csms_time = time.time()
        cp_time = csms_time + 7200  # CP saatini +2 saat kaydırıyoruz

        adapter.emit(
            message_type="MeterValues",
            payload={
                "transactionId": 42,
                "cp_timestamp": cp_time,
                "csms_time": csms_time,
                "time_skew_seconds": cp_time - csms_time,
                "meterValue": [
                    {
                        "sampledValue": [
                            {"value": "35"}
                        ]
                    }
                ],
                "note": "TIME_DESYNC_ATTACK_MARKER"
            }
        )
    # ================================
    
    # cp_event_flow'u çağır ve manipülasyon verisini alacağı fonksiyonu ver
    await cp_event_flow(mode="ATTACK", adapter=adapter, get_manipulated_data=get_manipulated_data)
    
    print("[SCENARIO] Saldırı simülasyonu tamamlandı.")

async def run_normal(adapter: Optional[ScenarioAdapter] = None):
    """Anomalisiz normal akışı başlatır."""
    
    print("\n[SCENARIO] 🟢 NORMAL MOD BAŞLADI (Anomalisiz Akış)")
    
    # Normal modda, manipülasyon verisi fonksiyonunu göndermiyoruz

    await cp_event_flow(mode="NORMAL", adapter=adapter)
    
    print("[SCENARIO] Normal simülasyon tamamlandı.")


def run_scenario(scenario="attack", adapter: Optional[ScenarioAdapter] = None):
    """Ana motor (run_all.py) tarafından çağrılan giriş noktası."""
    if scenario == "normal":
        asyncio.run(run_normal(adapter))

    else:
        asyncio.run(run_attack(adapter))

if __name__ == "__main__":
    run_scenario("attack")

#python run_all.py --scenario berat_time_desync --mode attack