# Zero-Energy Flood (Sıfır Enerjili Oturum Seli)

**Senaryo Sahibi:** Ömer Gülnaroğlu  
**Saldırı Tipi:** CAN-Bus Replay / DoS

## 1. Senaryo Özeti
Bu modül, **"CAN-Bus Replay Attack"** yöntemini simüle eder. Saldırgan araç, bataryası boş olsa bile BMS üzerinden kaydedilmiş **"Şarjı Durdur"** sinyalini istasyona tekrar tekrar gönderir. Bu durum, istasyonun enerji verememesine ve CSMS loglarında binlerce **"0 kWh"** değerinde çöp kayıt (log flood) oluşmasına neden olur.

## 2. Saldırı Mantığı
Kod (`scenario.py`), saldırı modunda şu döngüyü işletir:
1.  **Bağlantı:** Araç istasyona bağlanır (`StartTransaction`).
2.  **Saldırı:** Araç anında şarjı reddeder ve enerji tüketimi **0.0 Wh** olarak kalır.
3.  **Kapanış:** Oturum saniyeler içinde sonlanır (`StopTransaction`).
4.  **Flood:** Bu işlem arka arkaya tekrarlanarak sistemde "Log Seli" yaratılır.

## 3. Anomali Göstergeleri (IoC)
Dashboard üzerinde şu belirtiler gözlemlenir:
* **Enerji:** Tüketilen enerji her zaman **0 kWh**.
* **Süre:** Oturum süreleri çok kısadır (< 10 saniye).
* **Tekrar:** Aynı istasyonda kısa sürede çok sayıda Başlat/Durdur işlemi.

## 4. Kurulum ve Çalıştırma
Proje ana dizininde `run_all.py` scripti ile çalıştırılır.

**Normal Mod (Sağlıklı Şarj):**
`python run_all.py --scenario omer_sifir_enerji_sel --mode normal`

**Saldırı Modu (Zero-Energy Flood):**
`python run_all.py --scenario omer_sifir_enerji_sel --mode attack`

## 5. Dosya Yapısı
* `charge_point.py`: Sıfır enerji tüketimini simüle edebilen sanal istasyon sınıfı.
* `scenario.py`: Saldırı döngüsünü (Flood) yöneten senaryo motoru.
