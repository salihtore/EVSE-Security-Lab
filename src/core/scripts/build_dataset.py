#build_dataset.py
"""
EVSE Security Lab - Dataset Builder (Sentetik Veri Uretici)
Bu script, 9 farkli anomali senaryosu ve normal sarj akisi icin stabil ve tekrar uretilebilir bir ML egitim datasi olusturur. 

🔍 9 ANOMALI TESHIS MANTIGI:
----------------------------
1. KADIR (Thermal Spoofing): Akim (TX_KADIR_AMP) degisirken, sicakligin (meter_value) 40.0 derecede sabit kalmasiyla anlasilir.
2. BERAT (Time Desync): Timestamp'in aniden firlamasi ve meter_value degerinin 35.0'da cakilmasiyla anlasilir.
3. AHMET (Thermal Manipulation): meter_value degerinin fiziksel sinirlari asarak 96.0'a firlamasiyla anlasilir.
4. EMIN (Auth Bypass): Authorize onayi gelmeden (Bypass) direkt yuksek enerji tuketiminin (meter_value) baslamasiyla anlasilir.
5. HASAN (Session Hijacking): Ayni transaction_id degerinin kurban CP'den saldirgan CP'ye gecmesiyle anlasilir.
6. MAHMUT (Energy Manipulation): Gercek tuketim (TX_REAL) yuksekken resmi meter_value raporunun dusuk kalmasiyla anlasilir.
7. MERVE (Phantom Current): plugged: 0 (arac yok) iken meter_value degerinin artmaya devam etmesiyle anlasilir.
8. OMER (Zero-Energy Flood): Cok kisa zaman araliklarinda (timestamp) surekli 0.0 degerli mesaj akisiyla anlasilir.
9. SEMIH (Orphan Session): plugged: 0 oldugu halde islemin sonlanmamasi ve sayacin 5.0 degerinde asili kalmasiyla anlasilir.

⚠️ KRITIK ML EGITIM NOTU:
-------------------------
Modelin "message_type" sutunundaki "ANOMALY" etiketine bakarak ezber yapmamasi icin; egitim asamasinda bu etiketler "label" olarak kullanilmali, ancak 
test/tahmin asamasinda bu kolon modelden gizlenerek sadece sayisal verilerle (meter_value, timestamp, plugged) karar verilmesi saglanmalidir.

PDF Kriter Uyumlulugu:
- Kolonlar: timestamp, cp_id, message_type, transaction_id, meter_value, plugged 
- Cikti: data/dataset.csv 
- Klasor: data/ klasoru yoksa otomatik olusturulur
"""
import csv
import time
import random
from pathlib import Path

def build_dataset():
    out_file = "data/dataset.csv"
    output_path = Path(out_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = ['timestamp', 'cp_id', 'message_type', 'transaction_id', 'meter_value', 'plugged']
    rows_written = 0
    base_ts = time.time()
    
    N_NORMAL = 10
    N_ATTACK = 10

    print(f"🚀 EVSE Security Lab: Geçişli Veri Seti (Her biri {N_NORMAL} Normal + {N_ATTACK} Anomali)")

    try:
        with open(out_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            # --- 1. KADİR: Thermal Spoofing ---
            # Normal: Isınan kablo | Anomali: Donmuş sensör (40C)
            for i in range(N_NORMAL):
                writer.writerow({'timestamp': base_ts + rows_written, 'cp_id': 'CP_KADIR_CAN', 'message_type': 'NORMAL_DATA', 'transaction_id': 'TX_KADIR_STABLE', 'meter_value': round(25.0 + (i * 0.5), 2), 'plugged': 1})
                rows_written += 1
            for i in range(N_ATTACK):
                writer.writerow({'timestamp': base_ts + rows_written, 'cp_id': 'CP_KADIR_CAN', 'message_type': 'ANOMALY_THERMAL_SPOOFING', 'transaction_id': f'TX_KADIR_AMP_{round(random.uniform(20,30),2)}', 'meter_value': 40.0, 'plugged': 1})
                rows_written += 1

            # --- 2. BERAT: Time Desync ---
            # Normal: 10sn aralık | Anomali: Zaman sıçraması ve 35kW düşüşü
            for i in range(N_NORMAL):
                writer.writerow({'timestamp': base_ts + rows_written * 10, 'cp_id': 'CP_BERAT', 'message_type': 'MeterValues', 'transaction_id': 'TX_BERAT_INIT', 'meter_value': round(i * 2.0, 2), 'plugged': 1})
                rows_written += 1
            for i in range(N_ATTACK):
                writer.writerow({'timestamp': base_ts + 10000 + i, 'cp_id': 'CP_BERAT', 'message_type': 'ANOMALY_TIME_DESYNC', 'transaction_id': 'TX_BERAT_ATTACK', 'meter_value': 35.0, 'plugged': 1})
                rows_written += 1

            # --- 3. AHMET: Thermal Manipulation ---
            # Normal: Düşük Wh artışı | Anomali: 96 Derece patlaması
            for i in range(N_NORMAL):
                writer.writerow({'timestamp': base_ts + rows_written, 'cp_id': 'CP_OTONOM_01', 'message_type': 'MeterValues', 'transaction_id': 'TX_AHMET_P', 'meter_value': round(i * 0.1, 3), 'plugged': 1})
                rows_written += 1
            for i in range(N_ATTACK):
                writer.writerow({'timestamp': base_ts + rows_written, 'cp_id': 'CP_OTONOM_01', 'message_type': 'ANOMALY_THERMAL_MANIPULATION', 'transaction_id': 'TX_AHMET_P', 'meter_value': 96.0, 'plugged': 1})
                rows_written += 1

            # --- 4. EMİN: Auth Bypass ---
            # Normal: Authorize sonrası şarj | Anomali: Authorize olmadan şarj
            for i in range(N_NORMAL):
                writer.writerow({'timestamp': base_ts + rows_written, 'cp_id': 'CP_EMIN', 'message_type': 'Authorize_Accepted', 'transaction_id': 'TX_EMIN_OK', 'meter_value': 0.0, 'plugged': 1})
                rows_written += 1
            for i in range(N_ATTACK):
                writer.writerow({'timestamp': base_ts + rows_written, 'cp_id': 'CP_EMIN', 'message_type': 'ANOMALY_AUTH_BYPASS', 'transaction_id': 'TX_EMIN_BYPASS', 'meter_value': round(0.5 + i, 2), 'plugged': 1})
                rows_written += 1

            # --- 5. HASAN: Session Hijacking ---
            # Normal: Victim CP | Anomali: Attacker CP (Aynı TX ID)
            for i in range(N_NORMAL):
                writer.writerow({'timestamp': base_ts + rows_written, 'cp_id': 'CP_HASAN_VICTIM', 'message_type': 'MeterValues', 'transaction_id': 'TX_HIJACK_ME', 'meter_value': round(i * 0.5, 2), 'plugged': 1})
                rows_written += 1
            for i in range(N_ATTACK):
                writer.writerow({'timestamp': base_ts + rows_written, 'cp_id': 'CP_HASAN_ATTACKER', 'message_type': 'ANOMALY_SESSION_HIJACKING', 'transaction_id': 'TX_HIJACK_ME', 'meter_value': round(5.0 + i, 2), 'plugged': 1})
                rows_written += 1

            # --- 6. MAHMUT: Energy Manipulation ---
            # Normal: Dürüst Rapor | Anomali: Eksik Rapor (Hırsızlık)
            for i in range(N_NORMAL):
                writer.writerow({'timestamp': base_ts + rows_written, 'cp_id': 'CP_MAHMUT', 'message_type': 'MeterValues', 'transaction_id': f'TX_REAL_{round(i*0.5,1)}', 'meter_value': round(i * 0.5, 2), 'plugged': 1})
                rows_written += 1
            for i in range(N_ATTACK):
                writer.writerow({'timestamp': base_ts + rows_written, 'cp_id': 'CP_MAHMUT', 'message_type': 'ANOMALY_ENERGY_MANIPULATION', 'transaction_id': f'TX_REAL_{round((i+10)*1.5,1)}', 'meter_value': round(i * 0.1, 2), 'plugged': 1})
                rows_written += 1

            # --- 7. MERVE: Phantom Current ---
            # Normal: Plugged 1, Artan Meter | Anomali: Plugged 0, Artan Meter
            for i in range(N_NORMAL):
                writer.writerow({'timestamp': base_ts + rows_written, 'cp_id': 'CP_MERVE_HAYALET', 'message_type': 'MeterValues', 'transaction_id': 'TX_PHANTOM', 'meter_value': round(i * 0.5, 2), 'plugged': 1})
                rows_written += 1
            for i in range(N_ATTACK):
                writer.writerow({'timestamp': base_ts + rows_written, 'cp_id': 'CP_MERVE_HAYALET', 'message_type': 'ANOMALY_PHANTOM_CURRENT', 'transaction_id': 'TX_PHANTOM', 'meter_value': round(5.0 + (i*0.5), 2), 'plugged': 0})
                rows_written += 1

            # --- 8. ÖMER: Zero-Energy Flood ---
            # Normal: Yavaş artış | Anomali: Çok hızlı 0.0 değerleri
            for i in range(N_NORMAL):
                writer.writerow({'timestamp': base_ts + rows_written * 2, 'cp_id': 'CP_OMER_FLOOD', 'message_type': 'MeterValues', 'transaction_id': 'TX_OMER_N', 'meter_value': round(i * 0.5, 2), 'plugged': 1})
                rows_written += 1
            for i in range(N_ATTACK):
                writer.writerow({'timestamp': base_ts + rows_written + (i * 0.1), 'cp_id': 'CP_OMER_FLOOD', 'message_type': 'ANOMALY_ZERO_ENERGY_FLOOD', 'transaction_id': 'TX_FLOOD', 'meter_value': 0.0, 'plugged': 1})
                rows_written += 1

            # --- 9. SEMİH: Orphan Session ---
            # Normal: Start -> Stop | Anomali: Connection Lost -> No Stop
            for i in range(N_NORMAL):
                writer.writerow({'timestamp': base_ts + rows_written, 'cp_id': 'CP_SEMIH_ORPHAN', 'message_type': 'MeterValues', 'transaction_id': 'TX_SEMIH_OK', 'meter_value': round(i * 0.3, 2), 'plugged': 1})
                rows_written += 1
            for i in range(N_ATTACK):
                writer.writerow({'timestamp': base_ts + rows_written, 'cp_id': 'CP_SEMIH_ORPHAN', 'message_type': 'ANOMALY_ORPHAN_SESSION', 'transaction_id': 'TX_ORPHAN', 'meter_value': 5.0, 'plugged': 0})
                rows_written += 1

    except Exception as e:
        print(f"❌ Hata: {e}")

    print(f"✅ Başarıyla Tamamlandı: {rows_written} satır veri oluşturuldu. (Her blokta 10 Normal + 10 Anomali)")

if __name__ == "__main__":
    build_dataset()