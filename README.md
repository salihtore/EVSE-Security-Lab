# ⚡ EVSE Security Lab

**Akıllı Şarj İstasyonlarında (EVSE) Siber-Fiziksel Güvenlik Test ve Simülasyon Platformu**

Bu proje, elektrikli araç şarj altyapılarında (EVSE) kullanılan **OCPP (Open Charge Point Protocol)** protokolü ve ilgili donanım bileşenleri üzerindeki güvenlik açıklarını analiz etmek, siber saldırı senaryolarını simüle etmek ve blockchain tabanlı loglama ile güvenliği artırmak amacıyla geliştirilmiş kapsamlı bir **siber-fiziksel güvenlik laboratuvarıdır**.

Platform, araştırmacıların ve geliştiricilerin kendi saldırı senaryolarını oluşturmasına, bu saldırıları simüle etmesine ve yapay zeka/blockchain tabanlı savunma mekanizmalarını test etmesine olanak tanır.

---

## 🚀 Özellikler

- **Gelişmiş Saldırı Simülasyonları:** Isıl manipülasyon, zaman desenkronizasyonu, oturum çalma ve daha fazlasını içeren hazır senaryolar.
- **OCPP 1.6-J Desteği:** Şarj istasyonu (CP) ve Merkezi Yönetim Sistemi (CSMS) arasındaki iletişimi tam uyumlu şekilde simüle eder.
- **Blockchain Entegrasyonu (Sui):** Kritik olay loglarının değiştirilemezliği için **Sui Blockchain** ve **Walrus** (Blob Storage) entegrasyonu.
- **Canlı İzleme Paneli:** Saldırıları ve sistem durumunu gerçek zamanlı izlemek için modern bir **React + Vite** dashboard.
- **Modüler Yapı:** Kolayca yeni senaryo ve savunma modülü eklenebilir mimari.
- **Yapay Zeka Destekli Savunma:** Anomali tespiti için entegre edilmiş makine öğrenmesi modelleri.

---

## 📂 Proje Yapısı

```
EVSE-Security-Lab/
├── Simulasyon/              # Saldırı senaryolarının bulunduğu klasör
├── dashboard/               # React tabanlı web arayüzü
├── sui_admin/               # Sui Blockchain smart contractları (Move)
├── src/                     # Python tabanlı çekirdek simülasyon motoru
│   ├── api/                 # Backend API
│   ├── core/                # OCPP ve simülasyon mantığı
│   ├── attacks/             # Ortak saldırı kütüphaneleri
│   └── defense/             # Savunma ve anomali tespit modülleri
├── run_all.py               # Simülasyonları çalıştırmak için ana script
└── ...
```

---

## 💻 Teknoloji Yığını

| Katman | Teknolojiler | Amaç |
|-------|--------------|------|
| **Frontend** | React, Vite, Tailwind CSS, Recharts | Kullanıcı arayüzü ve görselleştirme |
| **Backend** | Python (asyncio, websockets) | Simülasyon motoru ve API |
| **Blockchain** | Sui (Move), Walrus | Veri bütünlüğü ve log saklama |
| **Protokol** | OCPP 1.6-J | EVSE haberleşme standardı |
| **Simülasyon** | Python, CAN Bus Kütüphaneleri | Donanım ve ağ simülasyonu |

---

## 🛠 Kurulum

Proje hem Python (backend) hem de Node.js (frontend) ortamlarına ihtiyaç duyar.

### Ön Gereksinimler
- Python 3.8+
- Node.js 18+
- [Sui CLI](https://docs.sui.io/guides/developer/getting-started/sui-install) (Blockchain özellikleri için)

### 1. Backend Kurulumu

```bash
# Projeyi klonlayın
git clone https://github.com/salihtore/EVSE-Security-Lab.git
cd EVSE-Security-Lab

# Sanal ortam oluşturun
python -m venv .venv
source .venv/bin/activate  # Windows için: .venv\Scripts\activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

### 2. Frontend (Dashboard) Kurulumu

```bash
cd dashboard
npm install
```

### 3. Blockchain Kurulumu (Opsiyonel)
Sui ağında işlem yapabilmek için `sui_admin` klasöründeki kontratların yayınlanması gerekebilir. Gerekli konfigürasyonlar `.env` dosyası üzerinden yapılır.

---

## ▶️ Kullanım

### Simülasyonları Çalıştırma

Tüm simülasyonları listelemek ve çalıştırmak için kök dizindeki `run_all.py` scriptini kullanabilirsiniz:

```bash
# Sanal ortam aktifken
python run_all.py --help

# Belirli bir senaryoyu çalıştırma (Örn: thermal_manipulation)
python run_all.py --scenario ahmet_thermal_manipulation --mode attack
```

Tekil bir senaryoyu doğrudan çalıştırmak için:
```bash
python Simulasyon/ahmet_thermal_manipulation/scenario.py
```

### Dashboard'u Başlatma

Siber güvenlik paneline erişmek için:

```bash
cd dashboard
npm run dev
```
Uygulama genellikle `http://localhost:5173` adresinde çalışacaktır.

---

## 🧪 Mevcut Senaryolar

`Simulasyon` klasörü altında aşağıdaki ve daha fazla senaryo bulunmaktadır:

1.  **Thermal Manipulation:** Sensör verilerini değiştirerek aşırı ısınma/soğuma simülasyonu.
2.  **Time Desync:** Zaman damgalarını manipüle ederek log tutarlılığını bozma.
3.  **Auth Bypass:** Yetkilendirme mekanizmalarını atlatma denemeleri.
4.  **Session Hijacking:** Aktif şarj oturumlarını ele geçirme.
5.  **Phantom Current:** Gerçekte olmayan akım verisi enjekte etme.
6.  **Zero Energy Flood:** Sıfır enerji tüketimi verisiyle sistemi boğma.
7.  **Replay Attack:** Geçmiş mesajları tekrar göndererek işlem yapma.

---

## 🤝 Katkıda Bulunma

1.  Yeni bir senaryo için `Simulasyon/` altında yeni klasör oluşturun (Türkçe karakter kullanmadan).
2.  `scenario.py` dosyanızı standartlara uygun şekilde oluşturun.
3.  Kodunuzu PEP8 standartlarına göre biçimlendirin.
4.  Pull Request (PR) açmadan önce en son değişiklikleri `git pull` ile alın.

---

