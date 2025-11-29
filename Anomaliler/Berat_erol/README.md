# 🔌 EV Şarj İstasyonlarında Siber Güvenlik Mimarisi ve Anomali Tespiti

Bu proje, elektrikli araç şarj altyapılarında (EVCS) ortaya çıkan siber güvenlik tehditlerini incelemekte ve özellikle **OCPP protokolü** üzerinden gerçekleştirilen **Zaman Senkronizasyonu Manipülasyonu** saldırılarına karşı proaktif bir savunma mekanizması geliştirmeyi hedeflemektedir. Çalışma, yapay zekâ destekli anomali tespiti ve blokzincir tabanlı veri bütünlüğü çözümlerini merkezine almaktadır.

---

## 1. 🕒 Anomali Senaryosu: Zaman Kaydırma ile Enerji Maskelenmesi
Bu çalışmanın temelini oluşturan anomali, şarj istasyonlarının faturalandırma ve yük yönetimi süreçlerini hedef almaktadır.

  <img width="605" height="534" alt="image" src="https://github.com/user-attachments/assets/24859bb3-afdb-43fc-8e8d-2bc1ad258a59" />

### Saldırı Özeti

Saldırgan, şarj istasyonu (CP) ile merkezi yönetim sistemi (CSMS) arasındaki OCPP trafiğine **Man-in-the-Middle (MitM)** yöntemiyle müdahale eder. Saldırının amacı, yüksek tarifeli saatlerde tüketilen enerjiyi, düşük tarifeli saatlere aitmiş gibi göstermektir.

| Parametre | Fiziksel Gerçeklik | Saldırganın Kaydı | Sonuç |
| :--- | :--- | :--- | :--- |
| **Gerçek Zaman** | Yüksek Tarife (Örn: 14:00)  | Düşük Tarife (Örn: 02:00) | **Yanlış Faturalandırma** |
| **Gerçek Tüketim** | 50 kWh  | 35 kWh  | **Gelir Kaybı (Revenue Loss)** |

### Saldırının Vektörleri 

* **Zaman Damgası Manipülasyonu:** `MeterValues` veya `TransactionEvent` mesajlarının zaman damgası değiştirilir.
* **NTP Zehirlenmesi:** Şarj istasyonunun NTP sunucusuna müdahale edilerek sistem saati kaydırılır.
* **Zayıf Şifreleme:** MitM saldırısını mümkün kılan zayıf TLS/WS veya zayıf kimlik doğrulama kullanılır.

### Etkileri

* **Finansal Etki:** Faturalandırma hatası ve operatör için gelir kaybı.
* **Operasyonel Etki:** Şebeke yönetim sistemlerinde hatalı enerji verisi nedeniyle yük dengeleme algoritmalarının yanlış çalışması.
* **Yasal Etki:** MID ve ISO 15118 standartlarına göre kayıt bütünlüğünün bozulması.

---

## 2.  SWOT Analizi ve Tehdit Modelimiz

Projenin tehdit modelini derinlemesine anlamak ve stratejik savunma hedeflerini belirlemek amacıyla bir **SWOT Analizi** yapılmıştır. Analiz, EV şarj altyapılarındaki temel güvenlik zafiyetlerine odaklanmaktadır.

### A. Temel Problemler ve Zafiyetler 

Proje, dört ana güvenlik problemine karşı çözüm üretmeyi hedefler:

1.  **Zayıf Şifreleme:** `ws://` kullanımı veya zayıf sertifikasyon (self-signed/test) MitM saldırılarına kapı açar.
2.  **Yetkisiz Erişim:** Zayıf kimlik doğrulama mekanizmaları nedeniyle CP/CSMS'e izinsiz girişler.
3.  **Man-in-the-Middle (MitM) Saldırıları:** İletişim trafiğinin yakalanıp değiştirilmesi (Zaman Kaydırma senaryosunun ana vektörü).
4.  **Firmware ve Yazılım Açıkları:** CAN seviyesinde davranış değiştirebilecek zararlı firmware enjeksiyonları.

### B. SMART Hedefler (Proje Odak Noktaları) 

Geliştirilecek sistemin başarısını ölçmek için hedefler belirlenmiştir:

| Hedef ID | Tanım | Metrik (Minimum Başarı Oranı) |
| :--- | :--- | :--- |
| **Hedef 1** | Anomali Tespit Sisteminin Geliştirilmesi | Anormal davranışların $\ge 95\%$ doğrulukla tespiti. |
| **Hedef 3** | Enerji Hırsızlığı ve Sahte Veri Algoritması | Enerji hırsızlığının gerçek zamanlı olarak $\ge 90\%$ hassasiyetle tespiti. |
| **Hedef 4** | Gerçek Zamanlı İzleme ve Müdahale Modülü | Şüpheli aktivite tespit edildiğinde ortalama 30 saniye içinde otomatik müdahale (şarjı durdurma). |
| **Hedef 5** | Standartlara Uygunluk | Geliştirilen sistemin OCPP 1.6, ISO 27001 ve ISO 15118 gibi standartlara $100\%$ uyumlu olması. |

### C. Analiz Bileşenleri

| Kategori | Açıklama |
| :--- | :--- |
| **Güçlü Yönler (Strengths)** | Yapay zekâ (Zaman Serisi Kümeleme, Autoencoder) ve blokzincir teknolojisi kullanılarak veri bütünlüğünün ve izlenebilirliğin sağlanması. |
| **Zayıf Yönler (Weaknesses)** | Blokzincir katmanının mimariye eklenmesiyle oluşabilecek **Mesaj İşleme Süresi** ve **CPU/Bellek** kullanımı artışı. |
| **Fırsatlar (Opportunities)** | Geliştirilen sistemin uluslararası standartlara (OCPP, ISO 15118) uyumluluğu ile pilot uygulama ve yaygınlaştırma potansiyeli. |
| **Tehditler (Threats)** | MitM, Sahte Mesaj Enjeksiyonu ve Tekrar Saldırıları gibi aktif siber tehditlerin varlığı; standartlarda belirtilen minimum güvenlik gereksinimlerinin aşılamaması. |

---

## 💡 Savunma ve Yenilikçi Yaklaşım

Projemiz, CAN-Bus güvenliğini de kapsayan üç katmanlı bir savunma mimarisi üzerine inşa edilecektir:

1.  **Güvenlik Protokolü Katmanı:** OCPP iletişim kanalının **Mutual TLS** ile korunması ve `SignedMeterValues` gibi özelliklerin kullanılması.
2.  **Anomali Tespit Katmanı (AI/ML):** Enerji tüketim desenlerini, ID frekanslarını ve zaman serisi verilerini analiz ederek anormal davranışları (`Time Desync`) $\ge 95\%$ doğrulukla tespit etme.
3.  **Blokzincir Tabanlı Bütünlük Katmanı:** Kritik CAN mesajlarının veya OCPP verilerinin hashlenerek blokzincire kaydedilmesi, böylece mesaj kaynağı, zaman damgası ve bütünlüğünün değiştirilemez biçimde doğrulanması.
