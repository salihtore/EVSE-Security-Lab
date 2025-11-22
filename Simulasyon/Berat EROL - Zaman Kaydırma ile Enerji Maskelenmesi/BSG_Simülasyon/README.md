# 🕒 OCPP Zaman Kaydırma Saldırısı Simülasyonu (RAW WebSocket)

Bu proje, Elektrikli Araç Şarj İstasyonları (EVCS) ile Merkezi Yönetim Sistemi (CSMS) arasındaki OCPP (Open Charge Point Protocol) iletişiminde **Zaman Senkronizasyonu Manipülasyonu (Time Desync Attack)** anomalisini simüle eder.

Simülasyon, CP'nin MeterValues (Ölçüm Değerleri) mesajındaki zaman damgasını kasten manipüle ederek, **Yüksek Tarife** saatindeki tüketimi **Düşük Tarife** saatine kaydırılmasını sağlar. CSMS ise bu tutarsızlığı tespit ederek alarm verir.

## 🎯 Projenin Amacı

  * **Siber-Fiziksel Çatışmayı Göstermek:** Siber saldırıların (timestamp manipülasyonu) finansal sistemler üzerindeki etkisini göstermek.
  * **Anomali Tespiti:** CSMS tarafında, gelen verilerdeki mantıksal ve zamansal tutarsızlıkları (`actual_time` vs. `recorded_time`) analiz ederek anomali tespit algoritmasının temelini atmak.

-----

## ⚙️ Kurulum ve Gereksinimler

Bu proje, harici bir OCPP kütüphanesine ihtiyaç duymaz. Sadece Python'un standart kütüphaneleri ve `websockets` kütüphanesi gereklidir.

### 1\. Sistem Gereksinimleri

  * Python 3.8+ (Windows ortamında test edilmiştir.)
  * Windows PowerShell veya Komut İstemi (CMD).

### 2\. Kütüphane Kurulumu

Gerekli kütüphaneyi VS Code terminalinizde kurun:

```bash
# Sadece websockets ve JSON işlemeyi sağlar
py -m pip install websockets
```

-----

## 🚀 Çalıştırma Talimatları

Simülasyonu başlatmak için **iki ayrı terminal** penceresi gereklidir. Her terminalin proje dizininde (`BSG_Simülasyon`) olduğundan emin olun.

### Adım 1: Sunucuyu (CSMS) Başlatma (Terminal 1)

Sunucu, tüm bağlantıları ve gelen MeterValues verilerini dinleyerek anomalileri tespit edecektir.

```bash
py .\final_server_v3.py
```

*Beklenen Çıktı: Sunucunun 9000 portunda dinlemeye başladığını gösteren başlık.*

### Adım 2: Saldırgan İstemciyi (CP) Başlatma (Terminal 2)

İstemci, sunucuya bağlanacak ve BootNotification gönderdikten 5 saniye sonra **manipüle edilmiş zaman damgalı** MeterValues mesajlarını göndermeye başlayacaktır.

```bash
py .\raw_cp_client.py
```

### 🚨 Sonuçların Gözlemlenmesi

Terminal 2'yi başlattıktan hemen sonra:

| Terminal | Olay | Kritik Çıktı |
| :---: | :--- | :--- |
| **Terminal 1 (CSMS)** | Bağlantı & Anomali Tespiti | **`🚨 ALARM - ZAMAN KAYDIRMA ANOMALİSİ TESPİT EDİLDİ!`** |
| **Terminal 2 (CP)** | Saldırı Verisi Gönderimi | **`[SALDIRGAN CP] 💾 Kaydırılmış Zaman (Saldırı): ...`** |

Bu çıktı, CP'den gelen **kaydırılmış zaman** ile CSMS'in **gerçek zamanı** karşılaştırdığında mantık hatası bulduğunu gösterir (Yüksek Tarife Tüketimi, Düşük Tarifede görünüyor).

-----

## 🛠️ Kod Yapısı ve Kritik Fonksiyonlar

Bu simülasyon, `python-ocpp` kütüphanesinin zorluklarını aşmak için tamamen manuel JSON oluşturma üzerine kurulmuştur.

### `raw_cp_client.py` (Saldırgan Modül)

  * **`timestamp_olustur(offset_hours)`:** Saldırının kalbi. Gerçek UTC zamanını alır ve MeterValues mesajı için kasten `TIME_SHIFT_HOURS` kadar geriye kaydırır.
  * **`call_olustur(action, payload, mesaj_id)`:** OCPP Call mesajını manuel olarak `[2, mesaj_id, action, payload]` formatında JSON dizisi olarak hazırlar.

### `final_server_v3.py` (Tespit Modülü)

  * **`handle_connection(websocket, path)`:** Gelen RAW JSON mesajlarını çözer ve `BootNotification` ile `MeterValues` mesajlarını ayırır.
  * **`check_tariff_anomaly(...)`:** Bu fonksiyon, CSMS'in dahili saatini (`actual_time`) kullanarak CP'den gelen sahte zamanı (`recorded_time`) karşılaştırır. Eğer tüketim yüksek tarife saatinde gerçekleşmiş ancak düşük tarifeye kaydedilmişse **ALARM** tetiklenir.
