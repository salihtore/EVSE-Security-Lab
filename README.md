# ⚡ EVSE Security Lab  
**Akıllı Şarj İstasyonlarında (EVSE) Siber-Fiziksel Güvenlik Test ve Simülasyon Platformu**

Bu proje, elektrikli araç şarj altyapılarında kullanılan **OCPP (Open Charge Point Protocol)** protokolünün güvenlik açıklarını analiz etmek, gerçekçi saldırı senaryoları üretmek ve şarj istasyonu – CSMS arasındaki iletişimi test etmek amacıyla geliştirilmiş bütünleşik bir **siber-fiziksel güvenlik laboratuvarıdır**.

Platform hem **saldırı simülasyonu**, hem **anomali tespiti**, hem de **savunma geliştirme** senaryolarını destekler.  
Modüler yapısı ile her ekip üyesi kendi OCPP anomalisini bağımsız şekilde geliştirebilir.

---

## 🎯 Projenin SMART Hedefleri

Bu proje, bilgi güvenliği alanında profesyonel siber test ortamı sağlamak için aşağıdaki SMART hedeflere göre tasarlanmıştır:

- **≥ %95 doğruluk** ile OCPP anomali tespiti  
- **Gerçek zamanlı enerji hırsızlığı tespiti** (≥ %90 hassasiyet)  
- Kritik saldırılara karşı **≤ 30 saniye tepki süresi**  
- OCPP 1.6 → OCPP 2.0.1 geçişinde **tam uyumluluk**  
- Sistem bileşenlerinde **ISO 27001 / ISO 15118** prensiplerine bağlılık  

---

## 💻 Kullanılan Teknolojiler

| Katman | Teknolojiler | Amaç |
|-------|--------------|------|
| **Protokol** | OCPP 1.6-J, JSON RPC | EVSE ↔ CSMS iletişimi |
| **Backend** | Python (asyncio, websockets), Node.js | Senaryo geliştirme |
| **Güvenlik** | Autoencoder, Isolation Forest, SVM | Anomali tespiti |
| **Blockchain** | Hyperledger Fabric / Ethereum | Log sahteciliğini engelleme |
| **Araçlar** | GitHub, Trello, VSCode | Takım işbirliği |

---

## 🛠 Kurulum

```bash
git clone https://github.com/salihtore/EVSE-Security-Lab.git
cd EVSE-Security-Lab
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
 ``` 

---

▶️ Simülasyon Çalıştırma

Tek senaryo: 
python Simulasyon/<senaryo_adı>/scenario.py

Tüm senaryolar:
python run_all.py

---

🧱 Yeni Senaryo Geliştirme Standartları

Yeni klasör eklenir:
Simulasyon/<senaryo_adı>/

Dosya yapısı:

scenario.py  
charge_point.py  
csms.py           (opsiyonel)
anomaly_detector.py (opsiyonel)


Türkçe karakter kullanılmaz

Kod stili PEP8’e uygundur

PR açmadan önce:

git pull
