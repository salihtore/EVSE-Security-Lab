CHARGE-SHIELD AI 

Elektrikli Araç Şarj İstasyonları İçin Siber Güvenlik ve Anomali Tespit Sistemi 

 

Bu proje, elektrikli araç şarj altyapısında (EVCS) görülen siber tehditleri tespit etmeyi ve 

otomatik olarak engellemeyi amaçlayan yapay zeka destekli bir güvenlik platformudur. 

Çalışma ortamı, OCPP (Open Charge Point Protocol) ve CAN-Bus protokollerini simüle eden 

modüler bir laboratuvar altyapısı üzerine kuruludur. 

 

Amaç 

Elektrikli araç şarj istasyonlarında yaygın görülen saldırılar: 

- Kimlik doğrulama atlatma (Auth Bypass) 

- Replay Attack 

- Session Hijacking 

- CAN-Bus Manipülasyonu 

- Enerji Hırsızlığı 

- Termal Sahtekarlık 

- Zaman Senkronizasyon Saldırıları 

- Yetim Seans 

- Zero-Energy Flood 

- Phantom Current Draw 

 

Bu tehditlere karşı: 

Anomali Tespit sistemi + Otomatik Müdahale (IPS) geliştirilmiştir. 

 

Özellikler 

Red Team (Saldırı) 

- OCPP üzerinden sahte mesaj üretme   

- MITM proxy ile Replay Attack   

- CAN-Bus enjeksiyonu   

- StopCharging / Meter spoofing   

- Session Hijacking   

- Yetim Seans üretme   

- Enerji hırsızlığı manipülasyonları   

- Zero-Energy Flood saldırısı 

 

Blue Team (Savunma) 

- Gerçek zamanlı IDS   

- OCPP mesaj korelasyonu   

- CAN-Bus anomali analizi   

- Rule-based karar motoru   

- Otomatik RemoteStopTransaction   

- Güvenli moda geçiş mekanizması   

- Loglama + risk görselleştirme 

 

AI Anomaly Detection 

- Isolation Forest   

- Autoencoder   

- Zaman serisi çıkıntı tespiti   

- Risk skoru üretimi   

- Model tabanlı tehdit sınıflandırma 

 

Dashboard 

- Canlı trafik   

- Saldırı/savunma istatistikleri   

- Log görüntüleme   

- Risk skor grafikleri   

- UI tabanlı olay inceleme 

 

Mimari (Kısa Özet) 

CSMS (Server) ↔ OCPP ↔ Charge Point (CP) ↔ CAN-Bus ↔ Donanım Modülleri 

 

Kurulum ve Çalıştırma 

1) Repo klonla: 

git clone https://github.com/salihtore/EVSE-Security-Lab.git 

cd EVSE-Security-Lab 

 

2) Sanal ortam: 

python -m venv venv 

source venv/bin/activate  (Windows: venv\Scripts\activate) 

 

3) Gereksinimler: 

pip install -r requirements.txt 

 

Branch Stratejisi 

main                 → Stabil sürüm   

dev                  → Geliştirme alanı   

feature/*            → Ayrı modüller   

hotfix/*             → Acil düzeltme 

 

Feature Branch’ler: 

- feature/redteam-attacks 

- feature/blueteam-defense 

- feature/ai-anomaly 

- feature/canbus-module 

- feature/dashboard-ui 

- feature/docs 

 

İş/Branch Tablosu 

- OCPP Simülasyonu → feature/redteam-attacks 

- CAN Modülü → feature/canbus-module 

- Savunma Sistemi → feature/blueteam-defense 

- AI Modeli → feature/ai-anomaly 

- Dashboard → feature/dashboard-ui 

- Dokümantasyon → feature/docs 

 

Desteklenen Saldırı Senaryoları 

- Authentication Bypass   

- Replay Attack   

- Session Hijacking   

- Zero-Energy Flood   

- Phantom Current   

- Termal Anomali   

- Time Desync Attack   

- Yetim Seans   

- CAN Injection   

- Sensör Manipülasyonu   

 

Demo Akışı 

1) CSMS başlatılır   

2) CP bağlanır   

3) Normal şarj başlar   

4) Saldırı tetiklenir   

5) IDS anomali yakalar   

6) IPS durdurur   

7) Dashboard göstergeleri güncellenir   

8) Log kaydı oluşturulur 

 