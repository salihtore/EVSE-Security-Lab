# 🔌 Bilgi Sistemleri Güvenliği Projesi: Akıllı Şarj İstasyonlarında Siber-Fiziksel Savunma Mimarisi

Bu depo, Elektrikli Araç Şarj Altyapılarında (EVCS) siber güvenlik tehditlerini incelemek ve özellikle **OCPP (Open Charge Point Protocol)** tabanlı anomalilere karşı **Yapay Zeka (AI)** ve **Blokzincir** teknolojileriyle güçlendirilmiş proaktif bir savunma mimarisi geliştirmek amacıyla hazırlanmıştır.

Proje, 12 farklı kritik güvenlik senaryosunu (anomali) kapsamakta olup, siber saldırıların fiziksel şarj süreçleri üzerindeki etkilerini simüle etmeye odaklanmıştır.

---

## 🎯 Projenin Temel Hedefleri (SMART)

Projemiz, belirlenen SMART hedefler doğrultusunda geliştirilmiştir:

* **Anomali Tespitinde Yüksek Doğruluk:** Şarj istasyonlarındaki anormal davranışların $\ge 95\%$ doğrulukla tespit edilmesi.
* **Enerji Hırsızlığı Tespiti:** Olağan dışı enerji tüketim desenlerini belirleyerek enerji hırsızlığını gerçek zamanlı olarak $\ge 90\%$ hassasiyetle tespit eden bir algoritma geliştirmek.
* **Hızlı Müdahale:** Şüpheli bir aktivite tespit edildiğinde ortalama 30 saniye içinde otomatik müdahale (şarj işlemini durdurma) sağlayacak olay yönetim altyapısı kurmak.
* **Standartlara Uyum:** Geliştirilen sistemin OCPP 2.0, ISO 27001 ve ISO 15118 gibi uluslararası standartlara $100\%$ uyumlu olması.

## 📂 Depo İçeriği

Bu depo, projenin tüm aşamalarını ve çıktılarını organize eden üç ana klasörden oluşmaktadır:

### 1. 📂 `Anomaliler`

Bu klasör, ekip üyeleri tarafından hazırlanan tüm güvenlik senaryolarını içerir:

* **Üye Adı Altında:** Her üyenin odaklandığı anomali senaryosunun (örn: CAN Enjeksiyonu, Enerji Maskelenmesi) detaylı açıklaması ve bu senaryoya özel **SWOT Analizi** dökümanları yer alır.

2. 📂 Dökümantasyon
Bu klasör, projenin yönetim, planlama ve akademik gerekliliklerini karşılayan tüm resmi ve teknik belgeleri içermektedir.

50 Maddelik Güvenlik Kontrol Listesi (Checklist): OCPP, Ağ, Veri Bütünlüğü ve Fiziksel katmanları kapsayan detaylı denetim listesi.

Projeye Genel Bakış: Proje özeti ve mimari planları.

Zaman Çizelgesi Belgesi: Proje yönetimi ve aşamalandırma (İP1, İP2, İP3, vb.) kayıtları.

Proje Değerlendirme Dokümanı: Değerlendirme kriterleri ve metrikler.

Takım Rehberi: Proje ekibinin organizasyon yapısını, üye listesini ve anomali senaryosu dağılımını gösteren kılavuzlar.

Proje Sunumu: Ders sunumunda kullanılan materyaller (örn. PowerPoint/PDF) ve bu sunumun içerik özetleri.

3. 📂 Simülasyon
Bu klasör, geliştirilen saldırı ve savunma prototiplerinin kanıtlarını içerir:

Üye Adı Altında: Her üyenin kendi anomalisine uygun olarak geliştirdiği simülasyon sisteminin kodları (Python/Raw WS/Node.js) ve saldırı ile tespitin başarılı olduğunu gösteren terminal çıktıları/logları yer alır.

---

## 💻 Kullanılan Teknolojiler ve Araçlar

| Alan | Teknolojiler/Standartlar | Uygulama |
| :--- | :--- | :--- |
| **Protokol** | OCPP 1.6 / OCPP 2.0.1 | Şarj istasyonu iletişimi. |
| **Geliştirme** | Python (asyncio, websockets), Node.js, CAN-utils, mitmproxy. | Simülasyon geliştirme ve siber saldırı benzetimi. |
| **Savunma** | Yapay Zeka (Autoencoder, SVM, Kümeleme), Blokzincir (Hyperledger Fabric/Ethereum). | Anomali tespiti ve veri bütünlüğü. |
| **Yönetim** | GitHub, Trello, SMART Hedefler, RAMS Tasarım Prensipleri. | Takım çalışması ve proje takibi. |
