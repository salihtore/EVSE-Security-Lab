"""
OCPP Session Hijacking Simulation
Ana simülasyon programı

Kullanım:
    python main.py --scenario <senaryo_adı>
    python main.py --interactive
"""

import asyncio
import argparse
import sys
from datetime import datetime
from typing import Optional

from charging_session import SessionManager, ChargingSession, SessionState
from anomaly_detector import AnomalyDetector, AlertLevel
from attack_scenarios import AttackOrchestrator, AttackType
from reporting import Logger, ReportGenerator
from ocpp_messages import StartTransaction, MeterValues, StopTransaction


class OCPPSimulator:
    """OCPP simülasyon yöneticisi"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.anomaly_detector = AnomalyDetector()
        self.attack_orchestrator = AttackOrchestrator()
        self.logger = Logger(log_file="logs/simulation.log")
        self.report_generator = ReportGenerator(self.logger)
        
        self.logger.info("="*80)
        self.logger.info("OCPP Session Hijacking Simulation Started")
        self.logger.info("="*80)
    
    async def simulate_normal_session(self, id_tag: str = "USER_001", 
                                     duration_seconds: int = 30) -> ChargingSession:
        """Normal şarj oturumu simülasyonu"""
        client_ip = "192.168.1.10"
        
        self.logger.info(f"Starting normal charging session for {id_tag}", {
            "id_tag": id_tag,
            "client_ip": client_ip
        })
        
        # 1. Oturum oluştur
        session = await self.session_manager.create_session(
            id_tag=id_tag,
            connector_id=1,
            client_ip=client_ip
        )
        
        # 2. Transaction başlat
        transaction_id = await self.session_manager.start_transaction(session)
        
        self.logger.success(f"Transaction started: {transaction_id}", {
            "transaction_id": transaction_id,
            "id_tag": id_tag,
            "meter_start": session.meter_start
        })
        
        # Anomali detektörüne kaydet
        start_msg = StartTransaction.create(
            connector_id=1,
            id_tag=id_tag,
            meter_start=session.meter_start
        )
        self.anomaly_detector.track_message(start_msg, client_ip)
        
        # 3. Şarj süresince meter values gönder
        intervals = duration_seconds // 10  # Her 10 saniyede bir
        
        for i in range(intervals):
            await asyncio.sleep(10)
            
            await self.session_manager.update_meter_value(transaction_id)
            current_meter = session.get_current_meter()
            
            meter_msg = MeterValues.create(
                connector_id=1,
                transaction_id=transaction_id,
                meter_value=current_meter
            )
            
            self.anomaly_detector.track_message(meter_msg, client_ip)
            
            # Anomali kontrolü
            alerts = self.anomaly_detector.analyze_session_hijack(
                transaction_id,
                session.to_dict(),
                meter_msg,
                client_ip
            )
            
            if alerts:
                for alert in alerts:
                    if alert.level == AlertLevel.CRITICAL:
                        self.logger.alert(f"CRITICAL ALERT: {alert.description}", alert.to_dict())
            
            self.logger.info(f"Meter value updated: {current_meter} Wh")
        
        return session
    
    async def simulate_session_hijack_scenario(self, id_tag: str = "USER_002"):
        """Session hijacking senaryosu"""
        self.logger.info("="*80)
        self.logger.info("SCENARIO: Session Hijacking Attack")
        self.logger.info("="*80)
        
        # 1. Normal oturum başlat
        self.logger.info("Phase 1: Legitimate user starts charging session")
        session = await self.simulate_normal_session(id_tag=id_tag, duration_seconds=20)
        
        await asyncio.sleep(2)
        
        # 2. Saldırgan IP değiştirerek oturumu ele geçirir
        self.logger.attack("Phase 2: Attacker hijacks session from different IP")
        
        attack_result = await self.attack_orchestrator.execute_attack(
            AttackType.SESSION_HIJACK_IP,
            session,
            attacker_ip="203.0.113.50"
        )
        
        if attack_result["success"]:
            self.logger.attack("Session hijacking attack executed successfully!", attack_result)
            
            # Anomali kontrolü
            for msg in attack_result.get("messages_sent", []):
                self.anomaly_detector.track_message(msg, "203.0.113.50")
                
                alerts = self.anomaly_detector.analyze_session_hijack(
                    session.transaction_id,
                    session.to_dict(),
                    msg,
                    "203.0.113.50"
                )
                
                for alert in alerts:
                    if alert.level == AlertLevel.CRITICAL:
                        self.logger.alert(f"🚨 CRITICAL ALERT: {alert.description}", alert.to_dict())
            
            # Oturumu ele geçirilmiş olarak işaretle
            await self.session_manager.mark_session_hijacked(session.transaction_id)
        
        # 3. Oturumu sonlandır
        await self.session_manager.stop_transaction(session.transaction_id)
        self.logger.info("Session terminated")
    
    async def simulate_id_spoofing_scenario(self, id_tag: str = "USER_003"):
        """ID spoofing senaryosu"""
        self.logger.info("="*80)
        self.logger.info("SCENARIO: ID Tag Spoofing Attack")
        self.logger.info("="*80)
        
        # 1. Normal oturum başlat
        self.logger.info("Phase 1: Legitimate user starts charging")
        session = await self.simulate_normal_session(id_tag=id_tag, duration_seconds=15)
        
        await asyncio.sleep(2)
        
        # 2. Saldırgan sahte ID ile müdahale eder
        self.logger.attack("Phase 2: Attacker uses spoofed ID tag")
        
        attack_result = await self.attack_orchestrator.execute_attack(
            AttackType.SESSION_HIJACK_ID_SPOOFING,
            session,
            fake_id_tag="HACKER_666"
        )
        
        if attack_result["success"]:
            self.logger.attack("ID spoofing attack executed!", attack_result)
            
            # Anomali kontrolü
            for msg in attack_result.get("messages_sent", []):
                self.anomaly_detector.track_message(msg, session.client_ip)
                
                alerts = self.anomaly_detector.analyze_session_hijack(
                    session.transaction_id,
                    session.to_dict(),
                    msg,
                    session.client_ip
                )
                
                for alert in alerts:
                    self.logger.alert(f"🚨 ALERT: {alert.description}", alert.to_dict())
        
        await self.session_manager.stop_transaction(session.transaction_id)
    
    async def simulate_meter_manipulation_scenario(self, id_tag: str = "USER_004"):
        """Sayaç manipülasyonu senaryosu"""
        self.logger.info("="*80)
        self.logger.info("SCENARIO: Meter Value Manipulation Attack")
        self.logger.info("="*80)
        
        # 1. Normal oturum başlat
        self.logger.info("Phase 1: Session starts normally")
        session = await self.simulate_normal_session(id_tag=id_tag, duration_seconds=20)
        
        await asyncio.sleep(2)
        
        # 2. Saldırgan sayaç değerini manipüle eder
        self.logger.attack("Phase 2: Attacker manipulates meter values")
        
        attack_result = await self.attack_orchestrator.execute_attack(
            AttackType.METER_MANIPULATION,
            session
        )
        
        if attack_result["success"]:
            self.logger.attack("Meter manipulation attack executed!", attack_result)
            
            # Anomali kontrolü
            for msg in attack_result.get("messages_sent", []):
                alerts = self.anomaly_detector.analyze_session_hijack(
                    session.transaction_id,
                    session.to_dict(),
                    msg,
                    session.client_ip
                )
                
                for alert in alerts:
                    self.logger.alert(f"🚨 ALERT: {alert.description}", alert.to_dict())
    
    async def simulate_all_scenarios(self):
        """Tüm senaryoları çalıştırır"""
        self.logger.info("Running all attack scenarios...")
        
        await self.simulate_session_hijack_scenario("USER_001")
        await asyncio.sleep(3)
        
        await self.simulate_id_spoofing_scenario("USER_002")
        await asyncio.sleep(3)
        
        await self.simulate_meter_manipulation_scenario("USER_003")
        
        self.logger.info("All scenarios completed!")
    
    def generate_final_report(self):
        """Final rapor oluşturur"""
        self.logger.info("Generating final report...")
        
        report = self.report_generator.generate_summary_report(
            self.session_manager,
            self.anomaly_detector,
            self.attack_orchestrator
        )
        
        # Konsola özet yazdır
        self.report_generator.print_summary(report)
        
        # JSON rapor kaydet
        json_path = self.report_generator.save_report(report)
        
        # Markdown rapor kaydet
        md_path = self.report_generator.save_markdown_report(report)
        
        return report


async def interactive_menu(simulator: OCPPSimulator):
    """Interaktif menü"""
    while True:
        print("\n" + "="*80)
        print("OCPP SESSION HIJACKING SIMULATION - Interactive Menu")
        print("="*80)
        print("1. Simulate Session Hijacking (IP Change)")
        print("2. Simulate ID Tag Spoofing Attack")
        print("3. Simulate Meter Manipulation Attack")
        print("4. Simulate Normal Session Only")
        print("5. Run All Attack Scenarios")
        print("6. View Critical Alerts")
        print("7. Generate Report")
        print("8. Exit")
        print("="*80)
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == "1":
            id_tag = input("Enter ID Tag (default: USER_001): ").strip() or "USER_001"
            await simulator.simulate_session_hijack_scenario(id_tag)
        
        elif choice == "2":
            id_tag = input("Enter ID Tag (default: USER_002): ").strip() or "USER_002"
            await simulator.simulate_id_spoofing_scenario(id_tag)
        
        elif choice == "3":
            id_tag = input("Enter ID Tag (default: USER_003): ").strip() or "USER_003"
            await simulator.simulate_meter_manipulation_scenario(id_tag)
        
        elif choice == "4":
            id_tag = input("Enter ID Tag (default: USER_000): ").strip() or "USER_000"
            duration = input("Enter duration in seconds (default: 30): ").strip()
            duration = int(duration) if duration.isdigit() else 30
            await simulator.simulate_normal_session(id_tag, duration)
        
        elif choice == "5":
            await simulator.simulate_all_scenarios()
        
        elif choice == "6":
            alerts = simulator.anomaly_detector.get_critical_alerts()
            if alerts:
                print(f"\n{len(alerts)} Critical Alerts Found:")
                for alert in alerts:
                    print(f"  [{alert['alert_id']}] {alert['alert_type']}: {alert['description']}")
            else:
                print("\nNo critical alerts found.")
        
        elif choice == "7":
            simulator.generate_final_report()
        
        elif choice == "8":
            print("\nGenerating final report before exit...")
            simulator.generate_final_report()
            print("\nExiting simulation. Goodbye!")
            break
        
        else:
            print("\nInvalid choice. Please try again.")


async def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(
        description="OCPP Session Hijacking Simulation"
    )
    parser.add_argument(
        "--scenario",
        choices=["hijack", "spoofing", "manipulation", "all", "normal"],
        help="Specific scenario to run"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--id-tag",
        default="USER_001",
        help="ID tag for the session"
    )
    
    args = parser.parse_args()
    
    simulator = OCPPSimulator()
    
    try:
        if args.interactive:
            await interactive_menu(simulator)
        elif args.scenario:
            if args.scenario == "hijack":
                await simulator.simulate_session_hijack_scenario(args.id_tag)
            elif args.scenario == "spoofing":
                await simulator.simulate_id_spoofing_scenario(args.id_tag)
            elif args.scenario == "manipulation":
                await simulator.simulate_meter_manipulation_scenario(args.id_tag)
            elif args.scenario == "all":
                await simulator.simulate_all_scenarios()
            elif args.scenario == "normal":
                await simulator.simulate_normal_session(args.id_tag)
            
            simulator.generate_final_report()
        else:
            # Varsayılan: tüm senaryoları çalıştır
            await simulator.simulate_all_scenarios()
            simulator.generate_final_report()
    
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
        simulator.generate_final_report()
    except Exception as e:
        simulator.logger.error(f"Simulation error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
