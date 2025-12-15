# Hızlı Başlangıç Kılavuzu

## ⚡ 5 Dakikada Başlangıç

### 1. Kurulum (30 saniye)

```bash
# Bağımlılıkları yükle
uv sync
```

### 2. İlk Simülasyonu Çalıştır (1 dakika)

```bash
# Interaktif mod ile başla
python main.py --interactive
```

Menüden `5` seçerek tüm saldırı senaryolarını çalıştır.

### 3. Raporları İncele

Simülasyon bittikten sonra:
- `reports/` klasöründe JSON ve Markdown raporları
- `logs/` klasöründe detaylı loglar bulabilirsin

## 🎯 Yaygın Kullanım Senaryoları

### Senaryo 1: Session Hijacking Test

```bash
python main.py --scenario hijack --id-tag TEST_USER
```

**Beklenen Sonuç:**
- ✅ IP değişikliği algılanır
- ✅ Kritik alarm oluşturulur
- ✅ Oturum ele geçirilmiş olarak işaretlenir

### Senaryo 2: ID Tag Spoofing

```bash
python main.py --scenario spoofing --id-tag VICTIM
```

**Beklenen Sonuç:**
- ✅ ID tag uyumsuzluğu tespit edilir
- ✅ Sahte kimlik alarm oluşturur

### Senaryo 3: Meter Manipulation

```bash
python main.py --scenario manipulation --id-tag TARGET
```

**Beklenen Sonuç:**
- ✅ Anormal sayaç değeri tespit edilir
- ✅ Potansiyel bedava şarj girişimi algılanır

### Senaryo 4: Tüm Senaryolar

```bash
python main.py --scenario all
```

Tüm saldırı senaryolarını sırayla çalıştırır.

## 📊 Demo Programını Çalıştır

```bash
python examples.py
```

Interaktif demo menüsünden istediğin örneği seçebilirsin.

## 🔍 Log ve Rapor İnceleme

### JSON Raporu
```bash
cat reports/report_*.json
```

### Markdown Raporu
```bash
cat reports/report_*.md
```

### Log Dosyası
```bash
tail -f logs/simulation.log
```

## ⚙️ İleri Seviye Kullanım

### Python Kodu ile Kullanım

```python
import asyncio
from main import OCPPSimulator

async def custom_test():
    simulator = OCPPSimulator()
    
    # Normal oturum
    session = await simulator.simulate_normal_session("USER_001")
    
    # Saldırı simülasyonu
    await simulator.simulate_session_hijack_scenario("USER_002")
    
    # Rapor oluştur
    report = simulator.generate_final_report()
    
    return report

# Çalıştır
asyncio.run(custom_test())
```

### Özel Anomali Kuralı Ekleme

```python
from anomaly_detector import AnomalyDetector, Alert, AlertLevel, AlertType

detector = AnomalyDetector()

# Yeni kural ekle
def check_custom_rule(transaction_id, data):
    if data.get("suspicious_pattern"):
        return detector._create_alert(
            alert_type=AlertType.SUSPICIOUS_SEQUENCE,
            level=AlertLevel.WARNING,
            description="Custom rule triggered",
            transaction_id=transaction_id
        )
```

## 🐛 Sorun Giderme

### Problem: "Module not found" hatası

**Çözüm:**
```bash
uv sync
```

### Problem: Permission hatası (Windows)

**Çözüm:**
PowerShell'i yönetici olarak çalıştır veya:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: Port zaten kullanımda

Bu simülasyon gerçek WebSocket bağlantısı kullanmıyor, bu yüzden port sorunu olmamalı.

## 📚 Ek Kaynaklar

- [README.md](README.md) - Tam dokümantasyon
- [examples.py](examples.py) - Örnek kullanımlar
- Soru ve öneriler için: GitHub Issues

## 💡 İpuçları

1. **Konsol Çıktısı:** Renkli loglar için terminal renk desteğinin açık olduğundan emin ol
2. **Rapor Takibi:** Her simülasyon timestamp ile benzersiz rapor oluşturur
3. **Log Yönetimi:** `logs/` klasörünü periyodik temizle
4. **Test Ortamı:** Gerçek sistemlerde test yapmadan önce izole ortamda çalıştır

## ⚠️ Önemli Notlar

- Bu simülasyon **sadece eğitim amaçlıdır**
- Gerçek sistemlerde izinsiz test yapmayın
- Üretim ortamlarında kullanmadan önce yetkilendirme alın

## 🚀 Sonraki Adımlar

1. ✅ Tüm senaryoları çalıştır
2. ✅ Raporları incele
3. ✅ Kendi senaryolarını oluştur
4. ✅ Anomali tespit kurallarını optimize et
5. ✅ Gerçek OCPP sistemi ile entegre et (opsiyonel)

---

Mutlu simülasyonlar! 🎉
