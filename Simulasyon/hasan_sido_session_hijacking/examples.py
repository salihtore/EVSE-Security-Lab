"""
Örnek Kullanım Senaryoları
Bu dosya simülasyonun nasıl kullanılacağını gösterir
"""

import asyncio
from main import OCPPSimulator


async def demo_basic_usage():
    """Temel kullanım örneği"""
    print("\n" + "="*80)
    print("DEMO 1: Temel Kullanım - Normal Şarj Oturumu")
    print("="*80 + "\n")
    
    simulator = OCPPSimulator()
    
    # Normal bir şarj oturumu simüle et
    session = await simulator.simulate_normal_session(
        id_tag="DEMO_USER_001",
        duration_seconds=15
    )
    
    print(f"\nOturum tamamlandı:")
    print(f"  Transaction ID: {session.transaction_id}")
    print(f"  Başlangıç: {session.meter_start} Wh")
    print(f"  Bitiş: {session.meter_stop} Wh")
    print(f"  Tüketim: {session.meter_stop - session.meter_start} Wh")


async def demo_session_hijacking():
    """Session hijacking senaryosu"""
    print("\n" + "="*80)
    print("DEMO 2: Session Hijacking - IP Değişikliği ile Saldırı")
    print("="*80 + "\n")
    
    simulator = OCPPSimulator()
    
    # Session hijacking senaryosu
    await simulator.simulate_session_hijack_scenario("VICTIM_USER")
    
    # Kritik alarmları göster
    critical_alerts = simulator.anomaly_detector.get_critical_alerts()
    print(f"\n🚨 {len(critical_alerts)} kritik alarm tespit edildi!")
    
    for alert in critical_alerts:
        print(f"  - {alert['alert_type']}: {alert['description']}")


async def demo_multiple_attacks():
    """Birden fazla saldırı senaryosu"""
    print("\n" + "="*80)
    print("DEMO 3: Çoklu Saldırı Senaryoları")
    print("="*80 + "\n")
    
    simulator = OCPPSimulator()
    
    # Tüm saldırı senaryolarını çalıştır
    await simulator.simulate_all_scenarios()
    
    # İstatistikleri göster
    stats = simulator.anomaly_detector.get_statistics()
    
    print("\n📊 Anomali Tespit İstatistikleri:")
    print(f"  Toplam Alarm: {stats['total_alerts']}")
    print(f"  Kritik: {stats['critical']}")
    print(f"  Uyarı: {stats['warning']}")
    print(f"  Bilgi: {stats['info']}")
    
    print("\n🎯 Alarm Türleri:")
    for alert_type, count in stats['by_type'].items():
        if count > 0:
            print(f"  {alert_type}: {count}")
    
    # Rapor oluştur
    report = simulator.generate_final_report()


async def demo_custom_scenario():
    """Özel senaryo örneği"""
    print("\n" + "="*80)
    print("DEMO 4: Özel Senaryo - Manuel Anomali Tespiti")
    print("="*80 + "\n")
    
    simulator = OCPPSimulator()
    
    # Normal oturum başlat
    session = await simulator.simulate_normal_session(
        id_tag="CUSTOM_USER",
        duration_seconds=10
    )
    
    await asyncio.sleep(1)
    
    # Manuel olarak anomali kontrolü yap
    from ocpp_messages import MeterValues
    
    # Sahte bir mesaj oluştur (farklı IP'den)
    fake_message = MeterValues.create(
        connector_id=1,
        transaction_id=session.transaction_id,
        meter_value=session.get_current_meter()
    )
    
    # Anomali analizi
    alerts = simulator.anomaly_detector.analyze_session_hijack(
        session.transaction_id,
        session.to_dict(),
        fake_message,
        "10.0.0.99"  # Farklı IP
    )
    
    if alerts:
        print(f"\n⚠️ {len(alerts)} anomali tespit edildi:")
        for alert in alerts:
            print(f"  [{alert.level}] {alert.alert_type}: {alert.description}")
    else:
        print("\n✅ Anomali tespit edilmedi")
    
    # Oturumu kapat
    await simulator.session_manager.stop_transaction(session.transaction_id)


async def demo_real_time_monitoring():
    """Gerçek zamanlı izleme simülasyonu"""
    print("\n" + "="*80)
    print("DEMO 5: Gerçek Zamanlı İzleme")
    print("="*80 + "\n")
    
    simulator = OCPPSimulator()
    
    print("Normal oturum başlatılıyor...")
    session = await simulator.simulate_normal_session(
        id_tag="MONITORED_USER",
        duration_seconds=20
    )
    
    # Oturum sırasında alarm oluştu mu kontrol et
    alerts = simulator.anomaly_detector.get_alerts()
    
    if alerts:
        print(f"\n📈 Oturum süresince {len(alerts)} olay tespit edildi")
        
        # Son 5 olayı göster
        recent_alerts = alerts[-5:]
        for alert in recent_alerts:
            print(f"  [{alert['timestamp']}] {alert['alert_type']}")
    else:
        print("\n✅ Oturum temiz tamamlandı, anomali yok")
    
    print(f"\nOturum Özeti:")
    print(f"  Süre: {(session.end_time - session.start_time).total_seconds():.1f} saniye")
    print(f"  Mesaj Sayısı: {session.message_count}")
    print(f"  Enerji: {session.meter_stop - session.meter_start} Wh")


async def main():
    """Tüm demo senaryolarını çalıştır"""
    demos = [
        ("Temel Kullanım", demo_basic_usage),
        ("Session Hijacking", demo_session_hijacking),
        ("Çoklu Saldırılar", demo_multiple_attacks),
        ("Özel Senaryo", demo_custom_scenario),
        ("Gerçek Zamanlı İzleme", demo_real_time_monitoring),
    ]
    
    print("\n" + "="*80)
    print("OCPP SESSION HIJACKING SIMULATION - DEMO SENARYOLARI")
    print("="*80)
    print("\nHangi demoyu çalıştırmak istersiniz?")
    print()
    
    for i, (name, _) in enumerate(demos, 1):
        print(f"{i}. {name}")
    
    print(f"{len(demos) + 1}. Tümünü Çalıştır")
    print(f"{len(demos) + 2}. Çıkış")
    print()
    
    try:
        choice = int(input("Seçiminiz (1-{}): ".format(len(demos) + 2)))
        
        if 1 <= choice <= len(demos):
            await demos[choice - 1][1]()
        elif choice == len(demos) + 1:
            for name, demo_func in demos:
                print(f"\n{'='*80}")
                print(f"Çalıştırılıyor: {name}")
                print(f"{'='*80}")
                await demo_func()
                await asyncio.sleep(2)
        elif choice == len(demos) + 2:
            print("\nÇıkılıyor...")
        else:
            print("\nGeçersiz seçim!")
    
    except ValueError:
        print("\nLütfen geçerli bir numara girin!")
    except KeyboardInterrupt:
        print("\n\nDemo kullanıcı tarafından sonlandırıldı.")


if __name__ == "__main__":
    asyncio.run(main())
