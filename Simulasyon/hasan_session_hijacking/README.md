Session Hijacking (Oturum Çalma) Senaryosu
Hazırlayan: Hasan Sido (Takım 1)
Tarih: 03.11.2025

📋 Senaryo Özeti
Bu senaryo, aktif bir şarj oturumunun (transactionId / idTag) saldırgan tarafından ele geçirilmesi (session hijacking) durumunu simüle eder. Özellikle şifrelenmemiş veya zayıf TLS ile çalışan OCPP trafiğinde kolay uygulanabilir bir saldırıdır.

🎯 Amaç
Aktif şarj oturumunun saldırgan tarafından devralınması
Gerçek kullanıcının şarj hakkını kaybetmesi
Bedava şarj veya oturumu kapatma
Loglarda tutarsızlık (idTag mismatch) oluşturma
🚀 Kullanım
Normal Mod (Güvenli Akış)
python run_all.py --scenario hasan_session_hijacking --mode normal
Akış:

BootNotification gönderilir
StartTransaction ile oturum başlar
MeterValues periyodik olarak gönderilir
StopTransaction ile oturum düzgün şekilde kapanır
Attack Mod (Oturum Çalma)
python run_all.py --scenario hasan_session_hijacking --mode attack
Saldırı Akışı:

Kurban normal şarj başlatır
Saldırgan ağ trafiğini dinler ve transactionId/idTag ele geçirir
Saldırgan kendi cihazından (farklı connector/IP) çalınan transactionId ile MeterValues gönderir
Saldırgan yanlış idTag ile StopTransaction göndererek oturumu kapatır
Kurban oturumun çalındığını fark eder
🔍 Tespit Edilmesi Gereken Anomaliler (IoC)
1. Connector/IP Uyumsuzluğu
Aynı transactionId için farklı connector_id kullanımı
Aynı oturum için farklı IP adresinden bağlantı
2. IdTag Mismatch
StartTransaction ile StopTransaction arasında idTag uyumsuzluğu
Beklenmeyen idTag ile işlem yapılması
3. Sayaç Manipülasyonu
Mantıksız sayaç değeri artışları/azalışları
Aynı anda iki farklı kaynaktan farklı sayaç değerleri
4. Replay Saldırısı
Aynı timestamp/payload ile tekrar gönderilen mesajlar
Sequence number veya nonce kontrollerinin başarısız olması
📊 Beklenen Davranış
Normal Mod
✅ BootNotification: Accepted
✅ StartTransaction: transactionId=1734567890123, idTag=USER_HASAN_001
✅ MeterValues: 0.5 kWh, 1.0 kWh, 1.5 kWh, 2.0 kWh, 2.5 kWh
✅ StopTransaction: transactionId=1734567890123, idTag=USER_HASAN_001
✅ StatusNotification: Available
Attack Mod
📱 [KURBAN] StartTransaction: transactionId=1734567890123, idTag=USER_HASAN_001
📱 [KURBAN] MeterValues: 0.5 kWh, 1.0 kWh, 1.5 kWh

🚨 [SALDIRGAN] TransactionID ele geçirildi: 1734567890123
🔴 [SALDIRGAN] MeterValues gönderiliyor (connector_id=2, farklı IP)
⚠️  ANOMALI: Aynı transactionId, farklı connector!

🔴 [SALDIRGAN] StopTransaction: transactionId=1734567890123, idTag=ATTACKER_HASAN_999
⚠️  ANOMALI: IdTag mismatch! Beklenen=USER_HASAN_001, Gelen=ATTACKER_HASAN_999

❌ [KURBAN] Oturum çalınmış, mesaj gönderilemiyor!
🛡️ Önerilen Güvenlik Önlemleri
1. Şifreleme ve Kimlik Doğrulama
TLS 1.2+ kullanımı (wss:// protokolü)
Sertifika tabanlı kimlik doğrulama (mTLS)
HMAC veya dijital imza ile mesaj bütünlüğü
2. Oturum Doğrulama
Transaction başlatıldığında IP adresi kaydedilmeli
Aynı transaction için connector_id değişimi kontrol edilmeli
Nonce/sequence number ile replay önlenmeli
3. Anomali Tespiti Kuralları
Basit Kurallar (Rule-based)
# Kural 1: Farklı IP/connector kontrolü
if transaction[id].connector_id != current_connector_id:
    ALARM("Farklı connector ile transaction kullanımı!")

# Kural 2: IdTag eşleşme kontrolü
if stop_transaction.id_tag != start_transaction.id_tag:
    ALARM("IdTag mismatch - Session hijacking olasılığı!")

# Kural 3: Replay tespiti
if message.timestamp == previous_message.timestamp:
    ALARM("Replay attack tespit edildi!")
Gelişmiş Kurallar (ML-based)
Isolation Forest: Anormal mesaj kalıpları
Autoencoder: Sayaç değerlerinde anormal değişim
Behavioral Profiling: Kullanıcı davranış profili ile karşılaştırma
4. Fiziksel Sensör Entegrasyonu
Fiziksel fiş bağlantı sensörü ile oturum doğrulama
Gerçek akım ölçümü ile sayaç değerlerinin çapraz kontrolü
5. SIEM ve Otomatik Müdahale
Real-time log izleme ve korelasyon
Anomali tespit edildiğinde otomatik oturum sonlandırma
Şüpheli IP/cihazların otomatik olarak engellenmesi
🧪 Test Senaryoları
PoC Test 1: Pasif Dinleme + Replay
# 1. Normal kullanıcı şarj başlatır
# 2. Saldırgan Wireshark ile trafiği yakalar
# 3. Saldırgan transactionId/idTag değerlerini elde eder
# 4. Saldırgan aynı mesajları tekrar gönderir
PoC Test 2: ID Spoofing
# 1. Saldırgan kendi cihazından bağlanır
# 2. Çalınan transactionId ile MeterValues gönderir
# 3. Faturalama sistemi karışır, alarm tetiklenir
PoC Test 3: Yetersiz TLS Testi
# ws:// (şifrelenmemiş) ile bağlantı test edilir
# Açık metin mesajlar görünür
# Saldırı kolaylaşır
📈 Etki Analizi
Kategori	Etki	Şiddet
Finansal	Bedava şarj, hatalı faturalandırma	🔴 Yüksek
Operasyonel	Kullanıcı oturumu aniden kapanabilir	🟠 Orta
Güvenlik	Sisteme başka erişimler elde edilebilir	🔴 Yüksek
Hukuki	Veri bütünlüğü ve kullanıcı hakları ihlali	🟠 Orta
📞 İletişim
Geliştirici: Hasan Sido
Takım: Takım 1
E-posta: [İletişim bilgisi]

Not: Bu simülasyon eğitim amaçlıdır. Gerçek sistemlerde izinsiz test yapmayınız.