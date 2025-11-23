# ANOMALİ SENARYO RAPORU  
“Sıfır Enerjili” Oturum Seli (Zero-Energy Flood)  
CAN-Bus StopCharging (Şarjı Durdur) Komutu Replay Attack  
Ders: Bilgi Sistemleri Güvenliği  
Proje: Şarj İstasyonlarının Güvenliği   
Hazırlayan: Ömer Gülnaroğlu  

------------------------------------------------------------

1) ÖZET
------------------------------------------------------------
Bu senaryo, CAN-Bus Replay Attack yöntemine dayalı bir güvenlik açığını ele almaktadır.  
Saldırgan, aracın CAN-Bus hattını dinleyerek BMS’den gelen “Batarya doldu, şarjı durdur (StopCharging)” mesajını kaydeder.  
Daha sonra kötü amaçlı yazılımla ele geçirilmiş araç, bir şarj istasyonuna bağlandığı anda bu komutu tekrar gönderir.

Bu işlem aracı “batarya dolu” olduğuna inandırır ve araç enerji çekmez.  
CSMS tarafında ise yüzlerce / binlerce “0 kWh – 0 saniye” oturum logu oluşur.

------------------------------------------------------------

2) SENARYONUN AMACI
------------------------------------------------------------
- Araçların şarj hizmeti almasını engellemek  
- CSMS üzerinde çok sayıda gereksiz (junk) oturum yaratarak analitik sistemlerini doldurmak  
- Operasyonel DoS etkisi oluşturmak  
- Veri bütünlüğünü (Data Integrity) zayıflatmak  

Süreç:  
1. Araç bağlanır → StartTransaction başlatılır  
2. Replay saldırısı tetiklenir  
3. Araç enerji çekmez (Energy = 0 kWh)  
4. StopTransaction hemen gönderilir  
5. Veritabanı “çöp oturumlarla” dolar  

------------------------------------------------------------

3) SALDIRI ADIMLARI
------------------------------------------------------------
1. Dinleme / Sniffing  
   - CAN-Bus trafiği izlenir  
   - Örn: 0x3F1 ID’li StopCharging mesajı kaydedilir  

2. Sızma  
   - Mesajı içeren malware araca yüklenir  

3. Replay  
   - Araç şarj istasyonuna bağlanınca saldırı tetiklenir  

4. Manipülasyon  
   - Kayıtlı StopCharging mesajı CAN-Bus’a tekrar gönderilir  

5. Etki  
   - EVCC “batarya dolu” sanır → enerji talep edilmez  

6. Log Etkisi  
   - StartTransaction + hemen StopTransaction → “0 kWh” oturumu  

7. Botnet Etkisi  
   - Bu malware araç filosuna yayıldığında CSMS her gün binlerce sahte oturum üretir  

------------------------------------------------------------

4) GÖZLEMLENECEK BELİRTİLER (IoC)
------------------------------------------------------------
Kritik Belirtiler:
- Energy_Consumed_kWh = 0 olan oturumlarda ani artış  
- Aynı idTag veya araç modeli üzerinden tekrar eden 0 kWh oturumları  

İkincil Belirtiler:
- <1 dakika süren oturumlarda ani artış  
- Başarısız oturum oranının aniden yükselmesi  

------------------------------------------------------------

5) TESPİT KURALLARI
------------------------------------------------------------
BASİT KURALLAR (SIEM / SQL):

KURAL 1:
Eğer son 1 saat içinde kWh_tuketim = 0 olan oturum sayısı > 100 ise → ALARM

KURAL 2:
Eğer aynı idTag için kWh_tuketim = 0 olan oturum sayısı > 3 ise → ALARM

GELİŞMİŞ KURALLAR:
- Her idTag / araç modeli için “başarılı vs başarısız” oturum profili hesaplanır  
- Başarısızlık oranındaki ani değişim Replay Attack göstergesidir  

------------------------------------------------------------

6) ETKİ ANALİZİ
------------------------------------------------------------
OPERASYONEL:
- CSMS veritabanı çöp loglarla dolar → DoS on Analytics  

FİNANSAL:
- Sıfır kWh oturumlar şarj istasyonunu meşgul ederek dolaylı gelir kaybı yaratır  

GÜVENLİK:
- Araç güvenlik mekanizmalarının atlatılabildiği görülür  
- İleride overcharging gibi daha kritik saldırılara yol açabilir  

------------------------------------------------------------

7) ÖNERİLEN ÖNLEMLER
------------------------------------------------------------
CSMS TARAFI:
- Kullanıcı bazlı 0 kWh sayaçlarının izlenmesi  
- Şüpheli idTag’lerin geçici askıya alınması  
- Şarj başlamadan önce mobil uygulama onayı gibi ek doğrulamalar  

ARAÇ ÜRETİCİSİ:
- Kritik mesajlar için MAC / SecOC uygulanması  
- Replay saldırılarının kriptografik olarak engellenmesi  

ARAÇ İÇİ GÜVENLİK:
- Eğlence sistemi → kritik CAN-Bus arasında firewall  
- Yetkisiz mesaj yönlendirmelerinin engellenmesi  

------------------------------------------------------------
