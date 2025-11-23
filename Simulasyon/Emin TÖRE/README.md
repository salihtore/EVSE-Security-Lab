EVSE Security Lab – OCPP Kimlik Doğrulama Atlatma (Authentication Bypass) Simülasyonu
Bu proje, EV şarj istasyonlarının güvenliği kapsamında, saldırganların yetkilendirme (RFID/App) adımını atlayarak kaçak elektrik kullanmasını (Enerji Hırsızlığı) simüle eden bir Kavram Kanıtı (PoC) çalışmasıdır.

🎯 Amaç
Kimlik doğrulama olmadan gönderilen sahte başlatma komutlarını simüle etmek ve bunları Durum Bazlı (Stateful) Anomali Dedektörü ile gerçek zamanlı tespit edip engellemektir.

📂 1. Proje Yapısı
Klasördeki önemli dosyalar ve görevleri şunlardır:

istasyon.py (Kurban / Charge Point)
Savunmasız Şarj İstasyonu Simülatörü.

Sanal veri yolu (UDP Multicast) üzerinden gelen komutları dinler.

Şu mesajlara tepki verir:

StartTransaction (0x100): Sorgusuz sualsiz şarjı başlatır (Zafiyet noktası).

StopTransaction (0x200): Şarjı acil olarak durdurur.

Konsolda şarj durumunu (Röle açık/kapalı) görselleştirir.

hacker.py (Saldırgan / Attacker)
Man-in-the-Middle (MitM) Saldırı Scripti.

Ağa sızar ve yetkisi olmadığı halde, Authorize adımını atlayarak doğrudan sahte bir StartTransaction komutu gönderir.

Amaç: İstasyonu kandırarak ücretsiz enerji akışı sağlamaktır.

dedektor.py (IDS / Güvenlik Sistemi)
Anomali Tespit ve Engelleme Modülü.

Trafiği sürekli izler ve son Authorize (Yetkilendirme) zamanını hafızasında tutar.

StartTransaction mesajı geldiğinde şu mantığı kontrol eder:

"Bu başlatma komutundan hemen önce (son 5 saniye içinde) geçerli bir kart okutuldu mu?"

Eğer okutulmadıysa ANOMALİ alarmı üretir ve istasyona otomatik STOP komutu gönderir.

🛡️ 2. Uygulanan Güvenlik Kuralları (Anomali Tespiti)
Simülasyonda aşağıdaki temel güvenlik kuralı uygulanmaktadır:

Kural-1: Yetkisiz Başlatma (Unauthorized StartTransaction)

Koşul: StartTransaction (0x100) mesajı görüldü.

Kontrol: Last_Authorize_Time > 5 saniye (veya hiç yok).

Tespit: Bu bir "Authentication Bypass" veya "Replay Attack" girişimidir.

Eylem:

🚨 Alarm: "Kritik Anomali: Yetkisiz Erişim" üretilir.

🛑 Müdahale: İstasyona StopTransaction (0x200) gönderilerek enerji kesilir.

Dedektör ekranında bu alarm şu şekilde görünür:

🚨🚨 KRİTİK ANOMALİ TESPİT EDİLDİ! (YETKİSİZ ERİŞİM) 🚨🚨 -> Sebep: Geçerli 'Authorize' kaydı bulunamadı.

⚙️ 3. Kurulum
Not: Bu proje Linux çekirdek modülü gerektirmez, Python UDP Multicast üzerinde çalışır.

Proje klasörüne girin:

Bash

cd OCPP_Auth_Bypass_PoC
Gerekli Python paketlerini yükleyin:

Bash

pip install python-can msgpack colorama tabulate
Veya requirements.txt varsa:

Bash

pip install -r requirements.txt
🚀 4. Çalıştırma
Simülasyonu görmek için 3 ayrı terminal açmanız gerekmektedir.

4.1. İstasyonu Başlat (Terminal 1)
Bash

python3 istasyon.py
Konsolda: ⛽ [İSTASYON] Sistem Hazır. Bekleniyor... yazısını görmelisiniz.

4.2. Güvenlik Dedektörünü Başlat (Terminal 2)
Bash

python3 dedektor.py
Konsolda: Siber Güvenlik Paneli açılacak ve trafik izlenmeye başlanacaktır.

4.3. Saldırıyı Yap (Terminal 3)
Bash

python3 hacker.py
Bu script çalıştırıldığında ağa sahte paket enjekte edilir.

📊 5. Beklenen Çıktılar
hacker.py Tarafında:
Plaintext

😈 HACKER: Merkezi Sistem (CSMS) taklit ediliyor...
🚀 SALDIRI: Sahte 'Yetki Verildi + Başlat' paketi yollandı!
istasyon.py Tarafında:
Plaintext

🔌 [İSTASYON] Başlat komutu geldi! Röleler açılıyor...
   ⚡ Şarj Ediliyor... %10
🛑 [İSTASYON] ACİL DURDURMA EMRİ ALINDI! (Güvenlik Sistemi)
dedektor.py Tarafında:
Plaintext

[UYARI] ⚠️  'ŞARJI BAŞLAT' KOMUTU GÖRÜLDÜ...

🚨  KRİTİK ANOMALİ TESPİT EDİLDİ! (YETKİSİZ ERİŞİM)  🚨
   -> Sebep: Geçerli 'Authorize' kaydı bulunamadı.
   -> Eylem: Otomatik Engelleme Başlatılıyor...
✅  MÜDAHALE BAŞARILI: İstasyon Durduruldu.
📝 6. Notlar
Bu simülasyon, gerçek şarj istasyonuna bağlanmadan Python Virtual Bus teknolojisi ile protokol güvenliğini test etmek için tasarlanmıştır.

Testler yerel ağda (Localhost/UDP) koşturulmaktadır, internet bağlantısı gerektirmez.

Proje, Bilgi Sistemleri Güvenliği dersi kapsamındaki EVSE Security Lab – Kimlik Doğrulama Güvenliği çalışması için hazırlanmıştır.
