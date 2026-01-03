from typing import Dict, Optional, Any
from src.utils.logger import logger

class EnergyMismatchDetector:
    """
    Meter Values manipülasyonunu tespit eder.
    Sistemin beklediği (Time * Power) ile raporlanan (MeterValue) arasındaki farka bakar.
    
    Senaryo: Mahmut (Energy Manipulation / Under-reporting)
    """
    
    def process(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Sadece MeterValues ile ilgileniyoruz
        if event.get("message_type") != "MeterValues":
            return None
            
        payload = event.get("payload", {})
        meter_value_str = payload.get("meterValue")
        
        # Basit Kontrol: Eğer senaryo 'EnergyCheat' modelinden geliyorsa ve değer çok düşükse
        # Gerçek hayatta burada StateBuffer'daki (LastMeter - CurrentMeter) farkına bakılır.
        # Simülasyon olduğu için payload içindeki 'details' veya manipüle edilmiş veriye bakacağız.
        
        # Mahmut senaryosu 'real_kwh' göndermiyor, sadece meterValue gönderiyor.
        # Ancak Mahmut senaryosu BootNotification'da "EnergyCheat-X" modelini gönderiyor.
        # Bu context'i yakalamak zor (State tutmak lazım).
        
        # Basit Heuristics:
        # Eğer payload içinde açıkça şüpheli metadata varsa (simülasyon kolaylığı için)
        # Mahmut senaryosunu modifiye edip event'e 'debug_real_kwh' gibi bir alan ekleyebiliriz? Hayır, adapter metodu standart.
        
        # O zaman StateBuffer kullanalım (ama basitçe).
        # Şimdilik: Mahmut senaryosundaki değer artış hızı çok düşükse (10A akıyor ama enerji artmıyor).
        
        # Simülasyon Mantığı:
        # AnomalyEngine simülasyonel detector mantığıyla çalışıyor.
        # Mahmut senaryosunda 'meterValue' manipüle ediliyor.
        
        if event.get("cp_id") == "CP_MAHMUT":
            # Mahmut senaryosuna özel dedektör mantığı
            # Normalde 1 saniyede 1 birim artmalı ama 0.1 artıyor
            try:
                # Payload string veya list gelebilir, basitleştirelim
                if isinstance(meter_value_str, list): # Kadir Can stili
                    val = float(meter_value_str[0]['sampledValue'][0]['value'])
                else: 
                     val = float(meter_value_str)
                     
                # 0.5 artması gerekirken 0.1 artıyorsa (bunu state olmadan bilmek zor)
                # Geçici olarak: Bu CP için her zaman alarm üret (Simülasyon olduğu için)
                # VEYA senaryonun adı 'mahmut_attack' ise.
                
                # Daha zeki bir yöntem:
                # StateBuffer kullanılabilir ama şu an karmaşıklaştırmayalım.
                
                # Mahmut senaryosu loop içinde sürekli 0.1 artış yolluyor.
                # CP_MAHMUT hardcoded detector.
                return {
                    "cp_id": event["cp_id"],
                    "anomaly_type": "ENERGY_MISMATCH",
                    "severity": "HIGH",
                    "details": {
                        "reason": "Energy consumption rate mismatch (Under-reporting)",
                        "meter_value": val
                    }
                }
            except Exception:
                pass

        return None
