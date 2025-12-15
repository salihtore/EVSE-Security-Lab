"""
Loglama ve Raporlama Sistemi
Detaylı log kaydı ve rapor oluşturma
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from colorama import Fore, Style, init

# Colorama'yı başlat
init(autoreset=True)


class Logger:
    """Gelişmiş loglama sistemi"""
    
    def __init__(self, log_file: str = "simulation.log", console_output: bool = True):
        self.log_file = Path(log_file)
        self.console_output = console_output
        self.logs: List[Dict] = []
        
        # Log dosyasını hazırla
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _format_message(self, level: str, message: str, data: Dict = None) -> Dict:
        """Log mesajını formatlar"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        
        if data:
            log_entry["data"] = data
        
        return log_entry
    
    def _write_to_file(self, log_entry: Dict):
        """Log dosyasına yazar"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def _print_to_console(self, level: str, message: str, data: Dict = None):
        """Konsola renkli yazdırır"""
        if not self.console_output:
            return
        
        color = {
            "INFO": Fore.CYAN,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "CRITICAL": Fore.RED + Style.BRIGHT,
            "ALERT": Fore.MAGENTA + Style.BRIGHT,
            "ATTACK": Fore.RED + Style.BRIGHT
        }.get(level, Fore.WHITE)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] [{level}] {message}{Style.RESET_ALL}")
        
        if data:
            print(f"{Fore.WHITE}{json.dumps(data, indent=2, ensure_ascii=False)}{Style.RESET_ALL}")
    
    def info(self, message: str, data: Dict = None):
        """Bilgi logu"""
        log_entry = self._format_message("INFO", message, data)
        self.logs.append(log_entry)
        self._write_to_file(log_entry)
        self._print_to_console("INFO", message, data)
    
    def success(self, message: str, data: Dict = None):
        """Başarı logu"""
        log_entry = self._format_message("SUCCESS", message, data)
        self.logs.append(log_entry)
        self._write_to_file(log_entry)
        self._print_to_console("SUCCESS", message, data)
    
    def warning(self, message: str, data: Dict = None):
        """Uyarı logu"""
        log_entry = self._format_message("WARNING", message, data)
        self.logs.append(log_entry)
        self._write_to_file(log_entry)
        self._print_to_console("WARNING", message, data)
    
    def error(self, message: str, data: Dict = None):
        """Hata logu"""
        log_entry = self._format_message("ERROR", message, data)
        self.logs.append(log_entry)
        self._write_to_file(log_entry)
        self._print_to_console("ERROR", message, data)
    
    def critical(self, message: str, data: Dict = None):
        """Kritik hata logu"""
        log_entry = self._format_message("CRITICAL", message, data)
        self.logs.append(log_entry)
        self._write_to_file(log_entry)
        self._print_to_console("CRITICAL", message, data)
    
    def alert(self, message: str, data: Dict = None):
        """Alarm logu"""
        log_entry = self._format_message("ALERT", message, data)
        self.logs.append(log_entry)
        self._write_to_file(log_entry)
        self._print_to_console("ALERT", message, data)
    
    def attack(self, message: str, data: Dict = None):
        """Saldırı logu"""
        log_entry = self._format_message("ATTACK", message, data)
        self.logs.append(log_entry)
        self._write_to_file(log_entry)
        self._print_to_console("ATTACK", message, data)
    
    def get_logs(self, level: str = None, limit: int = None) -> List[Dict]:
        """Logları filtreler ve döndürür"""
        logs = self.logs
        
        if level:
            logs = [log for log in logs if log["level"] == level]
        
        if limit:
            logs = logs[-limit:]
        
        return logs


class ReportGenerator:
    """Simülasyon raporu oluşturur"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def generate_summary_report(self, session_manager, anomaly_detector, 
                                attack_orchestrator) -> Dict[str, Any]:
        """Özet rapor oluşturur"""
        
        active_sessions = session_manager.get_all_active_sessions()
        session_history = session_manager.get_session_history()
        alerts = anomaly_detector.get_alerts()
        attack_history = attack_orchestrator.get_attack_history()
        alert_stats = anomaly_detector.get_statistics()
        
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_sessions": len(session_history) + len(active_sessions),
                "active_sessions": len(active_sessions),
                "completed_sessions": len(session_history),
                "total_alerts": len(alerts),
                "critical_alerts": alert_stats["critical"],
                "total_attacks_executed": len(attack_history)
            },
            "sessions": {
                "active": active_sessions,
                "history": session_history
            },
            "alerts": {
                "all": alerts,
                "critical": anomaly_detector.get_critical_alerts(),
                "statistics": alert_stats
            },
            "attacks": {
                "executed": attack_history
            }
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Raporu dosyaya kaydeder"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.json"
        
        report_path = Path("reports") / filename
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.success(f"Report saved to {report_path}")
        return report_path
    
    def print_summary(self, report: Dict[str, Any]):
        """Özet raporu konsola yazdırır"""
        print("\n" + "="*80)
        print(f"{Fore.CYAN}{Style.BRIGHT}SIMULATION SUMMARY REPORT{Style.RESET_ALL}")
        print("="*80 + "\n")
        
        summary = report["summary"]
        print(f"{Fore.GREEN}Sessions:{Style.RESET_ALL}")
        print(f"  Total: {summary['total_sessions']}")
        print(f"  Active: {summary['active_sessions']}")
        print(f"  Completed: {summary['completed_sessions']}")
        print()
        
        print(f"{Fore.YELLOW}Alerts:{Style.RESET_ALL}")
        print(f"  Total: {summary['total_alerts']}")
        print(f"  Critical: {summary['critical_alerts']}")
        print()
        
        print(f"{Fore.RED}Attacks:{Style.RESET_ALL}")
        print(f"  Executed: {summary['total_attacks_executed']}")
        print()
        
        # Alert istatistikleri
        if report["alerts"]["statistics"]["by_type"]:
            print(f"{Fore.MAGENTA}Alert Types:{Style.RESET_ALL}")
            for alert_type, count in report["alerts"]["statistics"]["by_type"].items():
                if count > 0:
                    print(f"  {alert_type}: {count}")
            print()
        
        # Kritik alarmlar
        critical = report["alerts"]["critical"]
        if critical:
            print(f"{Fore.RED}{Style.BRIGHT}CRITICAL ALERTS:{Style.RESET_ALL}")
            for alert in critical[:5]:  # İlk 5 kritik alarm
                print(f"  [{alert['alert_id']}] {alert['alert_type']}: {alert['description']}")
            if len(critical) > 5:
                print(f"  ... and {len(critical) - 5} more")
            print()
        
        print("="*80 + "\n")
    
    def generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """Markdown formatında rapor oluşturur"""
        summary = report["summary"]
        
        md = f"""# Session Hijacking Simulation Report

**Generated:** {report["report_timestamp"]}

## Executive Summary

- **Total Sessions:** {summary['total_sessions']}
- **Active Sessions:** {summary['active_sessions']}
- **Completed Sessions:** {summary['completed_sessions']}
- **Total Alerts:** {summary['total_alerts']}
- **Critical Alerts:** {summary['critical_alerts']}
- **Attacks Executed:** {summary['total_attacks_executed']}

## Alert Statistics

"""
        
        alert_stats = report["alerts"]["statistics"]
        md += f"""
| Level | Count |
|-------|-------|
| Critical | {alert_stats['critical']} |
| Warning | {alert_stats['warning']} |
| Info | {alert_stats['info']} |

### Alert Types

"""
        
        for alert_type, count in alert_stats["by_type"].items():
            if count > 0:
                md += f"- **{alert_type}:** {count}\n"
        
        md += "\n## Critical Alerts\n\n"
        
        critical = report["alerts"]["critical"]
        if critical:
            for alert in critical[:10]:
                md += f"""
### {alert['alert_id']} - {alert['alert_type']}

- **Level:** {alert['level']}
- **Time:** {alert['timestamp']}
- **Transaction ID:** {alert.get('transaction_id', 'N/A')}
- **Description:** {alert['description']}

"""
        else:
            md += "*No critical alerts detected.*\n"
        
        md += "\n## Attack History\n\n"
        
        attacks = report["attacks"]["executed"]
        if attacks:
            for attack in attacks:
                md += f"""
### {attack['attack_type']}

- **Time:** {attack['timestamp']}
- **Success:** {attack['result'].get('success', False)}

"""
        else:
            md += "*No attacks executed.*\n"
        
        return md
    
    def save_markdown_report(self, report: Dict[str, Any], filename: str = None):
        """Markdown raporunu dosyaya kaydeder"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.md"
        
        report_path = Path("reports") / filename
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        md_content = self.generate_markdown_report(report)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        
        self.logger.success(f"Markdown report saved to {report_path}")
        return report_path
