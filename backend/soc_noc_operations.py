# Network Automation & Security Analysis Scripts
# Professional SOC/NOC Portfolio

import json
import time
import random
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any
import subprocess
import socket
import threading

@dataclass
class NetworkDevice:
    """Representa um dispositivo de rede"""
    ip: str
    hostname: str
    device_type: str  # router, switch, firewall, server
    status: str  # online, offline, warning
    cpu_usage: float
    memory_usage: float
    uptime: int  # seconds
    last_seen: datetime

@dataclass 
class SecurityEvent:
    """Representa um evento de segurança"""
    timestamp: datetime
    source_ip: str
    event_type: str  # intrusion_attempt, malware, anomaly, policy_violation
    severity: str  # critical, high, medium, low
    description: str
    affected_asset: str
    response_action: str

class NetworkDiscovery:
    """Descoberta automática de dispositivos na rede"""
    
    def __init__(self, subnet="192.168.1.0/24"):
        self.subnet = subnet
        self.devices = []
    
    def ping_host(self, ip: str) -> bool:
        """Verifica se um host está online via ping"""
        try:
            # Windows
            result = subprocess.run(['ping', '-n', '1', '-w', '1000', ip], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def scan_ports(self, ip: str, ports: List[int]) -> Dict[int, bool]:
        """Escaneia portas específicas em um host"""
        open_ports = {}
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                open_ports[port] = (result == 0)
                sock.close()
            except:
                open_ports[port] = False
        return open_ports
    
    def identify_device_type(self, ip: str, open_ports: Dict[int, bool]) -> str:
        """Identifica o tipo de dispositivo baseado nas portas abertas"""
        if open_ports.get(22) or open_ports.get(23):  # SSH/Telnet
            if open_ports.get(80) or open_ports.get(443):  # HTTP/HTTPS
                return "router"
            else:
                return "switch"
        elif open_ports.get(3389):  # RDP
            return "server"
        elif open_ports.get(443) and not open_ports.get(22):
            return "firewall"
        else:
            return "unknown"
    
    def discover_network(self) -> List[NetworkDevice]:
        """Descobre dispositivos na rede"""
        print("🔍 Iniciando descoberta de rede...")
        devices = []
        
        # Simula descoberta para demonstração
        sample_devices = [
            ("192.168.1.1", "gateway-fw", "firewall"),
            ("192.168.1.10", "core-sw-01", "switch"),
            ("192.168.1.11", "core-sw-02", "switch"),
            ("192.168.1.20", "srv-web-01", "server"),
            ("192.168.1.21", "srv-db-01", "server"),
            ("192.168.1.22", "srv-backup", "server"),
            ("192.168.1.100", "router-wan", "router"),
        ]
        
        for ip, hostname, device_type in sample_devices:
            device = NetworkDevice(
                ip=ip,
                hostname=hostname,
                device_type=device_type,
                status="online",
                cpu_usage=random.uniform(10, 80),
                memory_usage=random.uniform(20, 90),
                uptime=random.randint(86400, 2592000),  # 1 day to 30 days
                last_seen=datetime.now()
            )
            devices.append(device)
            print(f"✅ Descoberto: {device.hostname} ({device.ip}) - {device.device_type}")
            time.sleep(0.5)  # Simula tempo de descoberta
        
        self.devices = devices
        return devices

class ThreatDetection:
    """Sistema de detecção de ameaças usando ML"""
    
    def __init__(self):
        self.ml_models = {
            "isolation_forest": {"accuracy": 94.2, "status": "active"},
            "dbscan_clustering": {"accuracy": 89.7, "status": "active"},
            "random_forest": {"accuracy": 96.8, "status": "active"}
        }
        self.security_events = []
    
    def analyze_network_traffic(self, traffic_data: Dict) -> List[SecurityEvent]:
        """Analisa tráfego de rede em busca de anomalias"""
        events = []
        
        # Simula detecção de ameaças
        threat_scenarios = [
            {
                "type": "intrusion_attempt",
                "description": "Multiple failed SSH login attempts detected",
                "severity": "high",
                "source_ip": "203.0.113.15",
                "asset": "srv-web-01"
            },
            {
                "type": "malware",
                "description": "Suspicious executable downloaded from external source",
                "severity": "critical", 
                "source_ip": "192.168.1.50",
                "asset": "workstation-05"
            },
            {
                "type": "anomaly",
                "description": "Unusual bandwidth consumption pattern detected",
                "severity": "medium",
                "source_ip": "192.168.1.25",
                "asset": "srv-backup"
            },
            {
                "type": "policy_violation",
                "description": "Access to restricted website category",
                "severity": "low",
                "source_ip": "192.168.1.105",
                "asset": "workstation-12"
            }
        ]
        
        # Gera eventos aleatórios
        if random.random() > 0.7:  # 30% chance de gerar evento
            scenario = random.choice(threat_scenarios)
            event = SecurityEvent(
                timestamp=datetime.now(),
                source_ip=scenario["source_ip"],
                event_type=scenario["type"],
                severity=scenario["severity"],
                description=scenario["description"],
                affected_asset=scenario["asset"],
                response_action="automated_quarantine" if scenario["severity"] == "critical" else "monitoring"
            )
            events.append(event)
            self.security_events.append(event)
        
        return events
    
    def behavioral_analysis(self, user_activity: Dict) -> List[SecurityEvent]:
        """Análise comportamental de usuários"""
        events = []
        
        # Simula análise comportamental
        anomalies = [
            "Login outside business hours",
            "Access from unusual geographic location", 
            "Bulk file download activity",
            "Privilege escalation attempt",
            "Suspicious process execution"
        ]
        
        if random.random() > 0.8:  # 20% chance
            event = SecurityEvent(
                timestamp=datetime.now(),
                source_ip=f"192.168.1.{random.randint(100, 200)}",
                event_type="anomaly",
                severity=random.choice(["medium", "high"]),
                description=random.choice(anomalies),
                affected_asset=f"workstation-{random.randint(1, 50)}",
                response_action="alert_security_team"
            )
            events.append(event)
            self.security_events.append(event)
        
        return events

class IncidentResponse:
    """Sistema de resposta a incidentes"""
    
    def __init__(self):
        self.active_incidents = []
        self.playbooks = {
            "malware": self.malware_response,
            "intrusion_attempt": self.intrusion_response,
            "anomaly": self.anomaly_response,
            "policy_violation": self.policy_response
        }
    
    def create_incident(self, security_event: SecurityEvent) -> Dict:
        """Cria um incidente baseado em evento de segurança"""
        incident = {
            "id": f"INC-{datetime.now().strftime('%Y%m%d')}-{len(self.active_incidents) + 1:03d}",
            "event": security_event,
            "status": "open",
            "priority": self.calculate_priority(security_event),
            "assigned_to": "SOC-L1",
            "created_at": datetime.now(),
            "steps_completed": []
        }
        
        self.active_incidents.append(incident)
        return incident
    
    def calculate_priority(self, event: SecurityEvent) -> str:
        """Calcula prioridade do incidente"""
        severity_map = {
            "critical": "P1",
            "high": "P2", 
            "medium": "P3",
            "low": "P4"
        }
        return severity_map.get(event.severity, "P4")
    
    def malware_response(self, incident: Dict):
        """Playbook de resposta a malware"""
        steps = [
            "Isolar sistema infectado",
            "Capturar imagem forense",
            "Analisar sample de malware",
            "Verificar propagação lateral",
            "Atualizar assinaturas antivírus",
            "Restaurar sistema limpo"
        ]
        return steps
    
    def intrusion_response(self, incident: Dict):
        """Playbook de resposta a intrusão"""
        steps = [
            "Bloquear IP de origem",
            "Verificar logs de acesso",
            "Analisar contas comprometidas",
            "Forçar reset de senhas",
            "Revisar permissões de acesso",
            "Implementar controles adicionais"
        ]
        return steps
    
    def anomaly_response(self, incident: Dict):
        """Playbook de resposta a anomalia"""
        steps = [
            "Coletar dados adicionais",
            "Correlacionar com eventos históricos",
            "Verificar legitimidade da atividade",
            "Documentar baseline normal",
            "Ajustar regras de detecção"
        ]
        return steps
    
    def policy_response(self, incident: Dict):
        """Playbook de resposta a violação de política"""
        steps = [
            "Notificar usuário sobre violação",
            "Registrar incidente em RH",
            "Revisar políticas de acesso",
            "Implementar controles preventivos",
            "Agendar treinamento de segurança"
        ]
        return steps

class NetworkAutomation:
    """Automação de tarefas de rede"""
    
    def __init__(self):
        self.config_templates = {}
        self.backup_configs = {}
    
    def backup_device_config(self, device: NetworkDevice) -> bool:
        """Faz backup da configuração do dispositivo"""
        print(f"📋 Fazendo backup de {device.hostname}...")
        
        # Simula backup de configuração
        config_data = f"""
! Configuration backup for {device.hostname}
! Generated on {datetime.now().isoformat()}
!
hostname {device.hostname}
!
interface GigabitEthernet0/1
 ip address {device.ip} 255.255.255.0
 no shutdown
!
line vty 0 4
 password cisco
 login
!
end
        """
        
        self.backup_configs[device.hostname] = {
            "timestamp": datetime.now(),
            "config": config_data,
            "size": len(config_data)
        }
        
        time.sleep(1)  # Simula tempo de backup
        print(f"✅ Backup concluído: {device.hostname}")
        return True
    
    def deploy_security_policy(self, policy: Dict) -> List[str]:
        """Implanta política de segurança nos dispositivos"""
        results = []
        
        devices = ["gateway-fw", "core-sw-01", "core-sw-02"]
        
        for device in devices:
            print(f"🔒 Aplicando política em {device}...")
            
            # Simula aplicação de política
            time.sleep(0.5)
            
            if random.random() > 0.1:  # 90% success rate
                results.append(f"✅ {device}: Política aplicada com sucesso")
            else:
                results.append(f"❌ {device}: Falha na aplicação da política")
        
        return results
    
    def monitor_performance(self, devices: List[NetworkDevice]) -> Dict:
        """Monitora performance dos dispositivos"""
        performance_data = {}
        
        for device in devices:
            # Simula coleta de métricas
            performance_data[device.hostname] = {
                "cpu_usage": device.cpu_usage,
                "memory_usage": device.memory_usage,
                "interface_utilization": random.uniform(10, 95),
                "response_time": random.uniform(1, 50),
                "packet_loss": random.uniform(0, 5),
                "timestamp": datetime.now()
            }
        
        return performance_data

class DatabaseManager:
    """Gerenciador de banco de dados para logs e eventos"""
    
    def __init__(self, db_path="security_network.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de dispositivos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY,
                ip TEXT UNIQUE,
                hostname TEXT,
                device_type TEXT,
                status TEXT,
                cpu_usage REAL,
                memory_usage REAL,
                uptime INTEGER,
                last_seen TIMESTAMP
            )
        """)
        
        # Tabela de eventos de segurança
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP,
                source_ip TEXT,
                event_type TEXT,
                severity TEXT,
                description TEXT,
                affected_asset TEXT,
                response_action TEXT
            )
        """)
        
        # Tabela de incidentes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                event_id INTEGER,
                status TEXT,
                priority TEXT,
                assigned_to TEXT,
                created_at TIMESTAMP,
                resolved_at TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES security_events (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_device(self, device: NetworkDevice):
        """Salva informações do dispositivo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO devices 
            (ip, hostname, device_type, status, cpu_usage, memory_usage, uptime, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (device.ip, device.hostname, device.device_type, device.status,
              device.cpu_usage, device.memory_usage, device.uptime, device.last_seen))
        
        conn.commit()
        conn.close()
    
    def save_security_event(self, event: SecurityEvent) -> int:
        """Salva evento de segurança"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO security_events 
            (timestamp, source_ip, event_type, severity, description, affected_asset, response_action)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (event.timestamp, event.source_ip, event.event_type, event.severity,
              event.description, event.affected_asset, event.response_action))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id

def main():
    """Função principal - demonstração das capacidades"""
    print("🚀 Iniciando SOC/NOC Operations Center")
    print("=" * 50)
    
    # Inicializar componentes
    db = DatabaseManager()
    discovery = NetworkDiscovery()
    threat_detection = ThreatDetection()
    incident_response = IncidentResponse()
    automation = NetworkAutomation()
    
    # 1. Descoberta de rede
    print("\n📡 DESCOBERTA DE REDE")
    devices = discovery.discover_network()
    
    for device in devices:
        db.save_device(device)
    
    print(f"✅ {len(devices)} dispositivos descobertos e catalogados")
    
    # 2. Detecção de ameaças
    print("\n🛡️ DETECÇÃO DE AMEAÇAS")
    
    for i in range(5):  # Simula 5 ciclos de análise
        traffic_data = {"packets": random.randint(1000, 5000)}
        user_activity = {"sessions": random.randint(50, 200)}
        
        # Análise de tráfego
        traffic_events = threat_detection.analyze_network_traffic(traffic_data)
        behavior_events = threat_detection.behavioral_analysis(user_activity)
        
        all_events = traffic_events + behavior_events
        
        for event in all_events:
            event_id = db.save_security_event(event)
            print(f"🚨 EVENTO DETECTADO: {event.description} (Severidade: {event.severity})")
            
            # Criar incidente se necessário
            if event.severity in ["critical", "high"]:
                incident = incident_response.create_incident(event)
                print(f"📋 INCIDENTE CRIADO: {incident['id']} (Prioridade: {incident['priority']})")
        
        time.sleep(1)
    
    # 3. Automação de rede
    print("\n🤖 AUTOMAÇÃO DE REDE")
    
    # Backup de configurações
    for device in devices[:3]:  # Backup dos primeiros 3 dispositivos
        automation.backup_device_config(device)
    
    # Aplicar política de segurança
    security_policy = {
        "name": "Block_Malicious_IPs",
        "rules": ["deny ip host 203.0.113.15 any", "deny ip host 198.51.100.10 any"]
    }
    
    results = automation.deploy_security_policy(security_policy)
    for result in results:
        print(result)
    
    # 4. Monitoramento de performance
    print("\n📊 MONITORAMENTO DE PERFORMANCE")
    performance = automation.monitor_performance(devices)
    
    for hostname, metrics in performance.items():
        print(f"📈 {hostname}: CPU {metrics['cpu_usage']:.1f}% | "
              f"Mem {metrics['memory_usage']:.1f}% | "
              f"Latência {metrics['response_time']:.1f}ms")
    
    # 5. Resumo final
    print("\n📋 RESUMO OPERACIONAL")
    print(f"🌐 Dispositivos monitorados: {len(devices)}")
    print(f"🚨 Eventos de segurança: {len(threat_detection.security_events)}")
    print(f"📋 Incidentes ativos: {len(incident_response.active_incidents)}")
    print(f"💾 Backups realizados: {len(automation.backup_configs)}")
    
    print("\n✅ SOC/NOC Operations Center executando com sucesso!")
    print("🎯 Portfolio de Cybersecurity & Network Engineering demonstrado!")

if __name__ == "__main__":
    main()
