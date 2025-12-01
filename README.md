EVSE Security Lab

Elektrikli Araç Şarj İstasyonları (EVSE) için saldırı–savunma odaklı bir siber güvenlik laboratuvarı.
Proje; OCPP → CAN-Bus köprüsü, anomali tespiti, saldırı simülasyonları, savunma modülü ve yapay zekâ tabanlı davranış analizi içerir.

Bu repo hem akademik çalışma hem de pratik saldırı/savunma laboratuvarı olarak tasarlanmıştır.

🚀 İçerik

Bu depo iki temel bileşenden oluşur:

1) Kod (main / dev branchleri)

Kod tamamen main ve dev branchlerinde tutulur.

Saldırı/savunma simülasyonları, çekirdek mekanizmalar ve protokol modelleri buradadır.


2) Dokümantasyon (docs branchi)

Tüm raporlar, senaryolar, gereksinim dokümanları ve proje dökümanları docs branchine taşınmıştır.

Bu sayede kod ve dokümanlar birbirine karışmaz. Kod incelemeleri temiz kalır.

🧭 Branch Stratejisi
Branch	İçerik	Kurallar
main	Stabil, test edilmiş, sunuma hazır kod	Protected, direkt push yasak
dev	Geliştirme ortamı, yeni özellikler	Commit serbest
docs	PDF, DOCX, raporlar, anomali dosyaları	Kod içermez
Akış:

Kod → dev

Test sonrası → Pull Request → main

Dokümanlar → docs

Kurumsal projelerdeki GitFlow yapısının sadeleştirilmiş hâlidir.

⚙️ Kurulum
1. Depoyu klonla
git clone https://github.com/salihtore/EVSE-Security-Lab.git
cd EVSE-Security-Lab

2. Sanal ortamı başlat
python -m venv venv
venv\Scripts\activate  # Windows
# veya
source venv/bin/activate  # Linux/Mac

3. Gereksinimleri yükle
pip install -r requirements.txt


🛡️ Savunma Modülü (IDS + AI)

src/defense/ dizini altında:

Paket bazlı kontrol

Zaman serisi anomalisi

Session-state kontrolü

Hızlı tepki (RemoteStopTransaction)

Yapay zekâ model entegrasyonu

Savunma modülü; OCPP ve CAN trafiğini eşzamanlı analiz ederek hem reaktif hem proaktif mekanizmalar içerir.

📄 Belgelere Erişim

Tüm raporlar burada:

docs branch:

https://github.com/salihtore/EVSE-Security-Lab/tree/docs/docs


PDF/DOCX’ler → bu branch içerisindedir.

👥 Takım & Yapı

Backend, CAN-Bus, saldırı/lab simülasyonu, IDS, AI ve dokümantasyon ekipleri

Her anomali bir öğrenci tarafından bağımsız modül olarak geliştirilir

Kod mimarisi modüler ve genişletilebilir

🧰 Katkıda Bulunma (Contribution)

Fork → dev branch aç

Yeni özellik → dev

PR → main

Kod incelemeden sonra merge

Dokümantasyon katkısı → docs branch.

🏁 Amaç

Bu lab:

EVSE güvenlik açıklarını anlamak

OCPP üzerinden saldırıları modellemek

CAN-Bus manipülasyonları simüle etmek

Gerçek zamanlı AI destekli savunma geliştirmek

Bir akademik/kurumsal EVSE güvenlik platformu için temel oluşturmak

için tasarlanmıştır.
