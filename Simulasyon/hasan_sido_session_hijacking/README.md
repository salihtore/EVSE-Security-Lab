# OCPP Session Hijacking Simulation

## 📋 Proje Hakkında

Bu proje, **Bilgi Sistemleri Güvenliği** dersi kapsamında hazırlanmış, elektrikli araç şarj istasyonlarında **Session Hijacking (Oturum Çalma)** saldırılarını simüle eden ve anomali tespit sistemlerini test eden bir uygulamadır.

**Ders:** Bilgi Sistemleri Güvenliği  
**Proje:** Şarj İstasyonlarının Güvenliği  
**Hazırlayan:** Hasan Sido (Takım 1)  
**Tarih:** 03.11.2025

## 🎯 Amaç

OCPP (Open Charge Point Protocol) kullanan şarj istasyonlarında oturum çalma saldırılarını simüle ederek:

- Güvenlik açıklarını tespit etmek
- Anomali tespit sistemlerini geliştirmek
- IoC (Indicators of Compromise) belirleyicilerini test etmek
- Güvenlik önlemlerinin etkinliğini değerlendirmek

## 🔥 Simüle Edilen Saldırı Senaryoları

### 1. Session Hijacking - IP Change
Saldırgan, farklı bir IP adresinden aktif bir şarj oturumunu ele geçirir.

**IoC'ler:**
- Aynı transaction ID için farklı IP adreslerinden gelen mesajlar
- Beklenmeyen MeterValues veya StopTransaction mesajları

### 2. ID Tag Spoofing
Saldırgan, sahte bir ID tag kullanarak oturuma müdahale eder.

**IoC'ler:**
- StopTransaction mesajında ID tag uyumsuzluğu
- Aynı transaction için farklı ID taglar

### 3. Meter Value Manipulation
Saldırgan, sayaç değerlerini manipüle ederek bedava şarj almaya çalışır.

**IoC'ler:**
- Geriye giden sayaç değerleri
- Anormal yüksek veya düşük enerji tüketimi

### 4. Connector Spoofing
Saldırgan, farklı bir connector ID ile mesaj gönderir.

**IoC'ler:**
- Aynı transaction için farklı connector ID'ler
- Fiziksel sensör verileri ile uyumsuzluk

### 5. Replay Attack
Saldırgan, yakaladığı OCPP mesajlarını tekrar oynatır.

**IoC'ler:**
- Kısa süre içinde tekrar eden aynı mesajlar
- Nonce/sequence kontrolü başarısızlığı

## 🚀 Kurulum

### Gereksinimler

- Python 3.11+
- uv (Python paket yöneticisi)

### Adımlar

1. **Repository'yi klonlayın:**
```bash
git clone <repository-url>
cd Simulasyon
```

2. **Bağımlılıkları yükleyin:**
```bash
uv sync
```

## 💻 Kullanım

### Interaktif Mod (Önerilen)

```bash
python main.py --interactive
```

Interaktif menüden istediğiniz senaryoyu seçebilirsiniz.

### Belirli Bir Senaryo Çalıştırma

```bash
# Session hijacking senaryosu
python main.py --scenario hijack --id-tag USER_001

# ID spoofing senaryosu
python main.py --scenario spoofing --id-tag USER_002

# Meter manipulation senaryosu
python main.py --scenario manipulation --id-tag USER_003

# Tüm senaryolar
python main.py --scenario all

# Normal oturum (saldırısız)
python main.py --scenario normal --id-tag USER_000
```

### Varsayılan Mod

Argüman olmadan çalıştırırsanız tüm senaryolar sırayla çalışır:

```bash
python main.py
```

## 📊 Çıktılar

### 1. Konsol Çıktısı

Simülasyon sırasında renkli ve detaylı loglar gösterilir:
- 🔵 INFO: Bilgi mesajları
- 🟢 SUCCESS: Başarılı işlemler
- 🟡 WARNING: Uyarılar
- 🔴 ERROR/CRITICAL: Hatalar
- 🟣 ALERT: Güvenlik alarmları
- 🔴 ATTACK: Saldırı eylemleri

### 2. Log Dosyası

Tüm aktiviteler `logs/simulation.log` dosyasına JSON formatında kaydedilir.

### 3. Raporlar

Simülasyon sonunda iki format rapor oluşturulur:

- **JSON Raporu:** `reports/report_YYYYMMDD_HHMMSS.json`
- **Markdown Raporu:** `reports/report_YYYYMMDD_HHMMSS.md`

## 🔍 Anomali Tespit Sistemi

### Tespit Edilen Anomaliler

1. **IP_CHANGE:** Transaction sırasında IP değişikliği
2. **ID_TAG_MISMATCH:** ID tag uyumsuzluğu
3. **CONNECTOR_MISMATCH:** Connector ID uyumsuzluğu
4. **REPLAY_ATTACK:** Tekrar eden mesajlar
5. **ABNORMAL_METER_VALUE:** Anormal sayaç değerleri
6. **SESSION_HIJACK:** Birden fazla IoC tespit edildiğinde

### Alarm Seviyeleri

- **INFO:** Bilgilendirme
- **WARNING:** Uyarı, dikkat gerektirir
- **CRITICAL:** Kritik güvenlik olayı, acil müdahale gerektirir

## 📁 Proje Yapısı

```
Simulasyon/
├── main.py                  # Ana simülasyon programı
├── ocpp_messages.py         # OCPP mesaj tanımları
├── charging_session.py      # Şarj oturumu yönetimi
├── anomaly_detector.py      # Anomali tespit sistemi
├── attack_scenarios.py      # Saldırı senaryoları
├── reporting.py             # Loglama ve raporlama
├── pyproject.toml           # Proje yapılandırması
├── README.md                # Bu dosya
├── logs/                    # Log dosyaları
│   └── simulation.log
└── reports/                 # Rapor dosyaları
    ├── report_*.json
    └── report_*.md
```

## 🛡️ Önerilen Güvenlik Önlemleri

Simülasyon sonuçlarına göre önerilen güvenlik önlemleri:

### 1. Transport Layer Security
- **TLS 1.2+** kullanımı (wss://)
- Sertifika doğrulama (mutual TLS)
- Güçlü cipher suite'ler

### 2. Mesaj Bütünlüğü
- HMAC ile mesaj imzalama
- Nonce/sequence numarası kullanımı
- Timestamp doğrulama

### 3. Oturum Yönetimi
- IP adresi doğrulama
- Fiziksel sensör kontrolü
- Session timeout mekanizması

### 4. Anomali Tespiti
- Gerçek zamanlı izleme
- Machine Learning tabanlı davranış analizi
- SIEM entegrasyonu

### 5. Erişim Kontrolü
- ID tag şifreleme
- Role-based access control (RBAC)
- Multi-factor authentication (MFA)

## 📈 Örnek Çıktı

```
================================================================================
OCPP SESSION HIJACKING SIMULATION - SUMMARY REPORT
================================================================================

Sessions:
  Total: 3
  Active: 0
  Completed: 3

Alerts:
  Total: 12
  Critical: 6

Attacks:
  Executed: 3

Alert Types:
  SESSION_HIJACK: 2
  IP_CHANGE: 3
  ID_TAG_MISMATCH: 1
  ABNORMAL_METER_VALUE: 1

CRITICAL ALERTS:
  [ALERT-000001] IP_CHANGE: IP address change detected for transaction 1000
  [ALERT-000003] SESSION_HIJACK: POSSIBLE SESSION HIJACKING DETECTED
  [ALERT-000005] ID_TAG_MISMATCH: ID tag mismatch in StopTransaction
  ...
```

## 🧪 Test Senaryoları

### PoC / Test Planı

1. **Pasif Dinleme + Replay:**
   - TransactionID ve idTag yakalanır
   - Mesajlar tekrar gönderilir
   - Beklenen: Replay alarm tetiklenir

2. **ID Spoofing:**
   - Saldırgan kendi cihazından MeterValues gönderir
   - Farklı idTag kullanılır
   - Beklenen: ID_TAG_MISMATCH alarm

3. **Yetersiz TLS Testi:**
   - ws:// kullanılır (şifrelenmemiş)
   - Açık metin mesajlar görünür
   - Beklenen: Saldırı kolaylaşır

## 🔧 Geliştirme

### Yeni Saldırı Senaryosu Ekleme

```python
from attack_scenarios import AttackScenario, AttackType

class YourAttackScenario(AttackScenario):
    def __init__(self):
        super().__init__(
            attack_type=AttackType.YOUR_ATTACK,
            description="Your attack description"
        )
    
    async def execute(self, session, **kwargs):
        # Saldırı kodunuz
        pass
```

### Yeni Anomali Kuralı Ekleme

```python
# anomaly_detector.py içinde
def check_your_anomaly(self, ...):
    if condition:
        return self._create_alert(
            alert_type=AlertType.YOUR_ANOMALY,
            level=AlertLevel.CRITICAL,
            description="Your description",
            ...
        )
```

## 📚 Referanslar

- [OCPP 1.6 Specification](https://www.openchargealliance.org/)
- [CWE-384: Session Fixation](https://cwe.mitre.org/data/definitions/384.html)
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

## 📝 Lisans

Bu proje eğitim amaçlıdır ve MIT lisansı altında paylaşılmaktadır.

## 👥 İletişim

**Hazırlayan:** Hasan Sido  
**Takım:** Takım 1  
**Ders:** Bilgi Sistemleri Güvenliği

---

⚠️ **UYARI:** Bu simülasyon yalnızca eğitim ve araştırma amaçlıdır. Gerçek sistemlerde izinsiz test yapmayınız.
