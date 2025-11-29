# 🛡️ OCPP & EV Şarj İstasyonu Güvenlik Kontrol Listesi (50 Madde)

Bu kontrol listesi, elektrikli araç şarj istasyonlarının (EVCS) merkezi yönetim sistemi (CSMS) ve şarj ünitesi (CP) arasındaki iletişim ve donanım katmanlarında karşılaşılabilecek olası güvenlik zafiyetleri ve anomali türlerini kapsamaktadır. Özellikle, projemizin odak noktası olan **Zaman Kaydırma** ve **Enerji Hırsızlığı** gibi siber-fiziksel anomalilerin tespiti hedeflenmiştir.

## 🎯 Projenin Amacı ve Kapsamı

Kontrol listesi, **Yapay Zeka Destekli Anomali Tespit Sisteminin** (SMART Hedef 1) geliştirilmesi için bir **veri etiketleme ve kural tabanlı tespit altyapısı** oluşturmayı amaçlar.

Liste, sekiz ana kategoride toplanmış olup, her bir madde bir güvenlik açığı, hatalı konfigürasyon veya anomaliye işaret eder. 

---

## 📋 Güvenlik Kontrol Listesi Kategorileri

Kontrol listesi, istasyon güvenliğini uçtan uca değerlendirmek üzere tasarlanmıştır:

### 1. Kimlik Doğrulama & Erişim Kontrolü (A)
* CP ve CSMS arasındaki bağlantının **Mutual TLS (mTLS)** ile kurulup kurulmadığı.
* Cihazlarda **varsayılan (default) kimlik bilgilerinin** kullanılıp kullanılmadığı.

### 2. Giriş Doğrulama (V)
* Gelen **OCPP JSON yüklerinin şema ve format doğrulamasından** geçip geçmediği.
* CAN-Bus'a iletilen komut ID'lerinin **izin verilen listeler (whitelisting)** ile filtrelediği.

### 3. Kriptografi (C)
* Kritik bileşenlerin sadece imzalı yazılım çalıştırmasını sağlayan **Güvenli Önyükleme (Secure Boot)** mekanizmasının varlığı.
* OTA (Over-the-Air) firmware güncellemelerinde **imza doğrulaması**nın zorunlu tutulması.

### 4. Bütünlük (Integrity) (I)
* MeterValues gibi faturalandırma verilerinin **dijital olarak imzalanması** (OCPP 2.0.1'de `SignedMeterValues` özelliği).
* Ağ trafiğindeki mesajların **sıra takibinin** yapılması (Replay saldırılarına karşı).

### 5. Zaman ve Enerji (T) **(Proje Odak Noktası)**
* CP ile CSMS arasındaki zaman damgası farkının (**Timestamp Delta**) belirli bir eşiğin (`< 5 saniye`) altında olup olmadığının sürekli izlenmesi.
* NTP sunucusunun durumunun takip edilmesi (NTP Spoofing/Zehrine karşı).
* Raporlanan şarj değerlerinin, geçen **zamana göre fiziksel limitleri** aşıp aşmadığı.

### 6. Ağ Güvenliği (N)
* CP üzerinde harici erişime açık **gereksiz portların** olup olmadığı.
* CSMS'ye gelen bağlantı oranlarında **anormal bir yükselişin** (Brute Force/DoS riski) olup olmadığı.

### 7. Davranışsal Anomali (B)
* Şarj işlemleri sırasında `RemoteStart` ve `RemoteStop` komutlarının **anormal hızda tekrarı**.
* Kullanıcı şarj sürelerinin veya tüketim profillerinin **genel ortalamadan** ciddi şekilde sapması.

### 8. Fiziksel ve Olay Yanıtlama (P & D)
* Kritik anahtarların **TPM/HSM** gibi güvenli bir elementte saklanıp saklanmadığı.
* Bir anomali tespit edildiğinde, sistemin **otomatik müdahale** (şarjı durdurma, erişimi kısıtlama) yeteneğinin olup olmadığı (SMART Hedef 4).

---

## 📝 Uygulama ve Kullanım

Bu kontrol listesi, projenizin iki ana bileşenini destekler:

1.  **Kural Tabanlı IDS:** Özellikle T1, T2 ve V3 gibi maddeler, temel seviyede anomali tespiti için (`IF [Şart] THEN ALARM`) basit **Güvenlik Geçidi (Gateway)** filtreleri oluşturmak için kullanılır.
2.  **Yapay Zeka Veri Etiketlemesi:** Kontrol listesindeki maddeler, toplanan gerçek veya sentetik saldırı verilerini (örneğin MeterValues veya CAN trafiği) etiketlemek için kullanılır. Etiketli bu veri setleri, **Zaman Serisi Kümeleme** veya **Autoencoder** gibi yapay zeka modellerini eğitmek için temel oluşturur.

---
