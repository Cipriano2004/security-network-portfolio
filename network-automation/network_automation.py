# Network Automation Scripts
# Professional Network Engineering Portfolio

import json
import time
import socket
import subprocess
import threading
from datetime import datetime
import random
import ipaddress
from dataclasses import dataclass
from typing import List, Dict, Optional
import re

@dataclass
class SNMPDevice:
    """Dispositivo SNMP para monitoramento"""
    ip: str
    community: str
    device_type: str
    hostname: str
    uptime: int
    interfaces: List[Dict]
    cpu_usage: float
    memory_usage: float
    temperature: Optional[float] = None

class NetworkScanner:
    """Scanner de rede para descoberta automática"""
    
    def __init__(self, subnet="192.168.1.0/24"):
        self.subnet = subnet
        self.active_hosts = []
        self.scan_results = {}
    
    def ping_sweep(self) -> List[str]:
        """Realiza ping sweep na rede"""
        print(f"🌐 Executando ping sweep em {self.subnet}")
        network = ipaddress.IPv4Network(self.subnet, strict=False)
        active_hosts = []
        
        def ping_host(ip):
            try:
                # Windows ping command
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', '1000', str(ip)],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    active_hosts.append(str(ip))
                    print(f"✅ Host ativo: {ip}")
            except:
                pass
        
        threads = []
        for ip in list(network.hosts())[:20]:  # Limita para demonstração
            thread = threading.Thread(target=ping_host, args=(ip,))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        self.active_hosts = active_hosts
        return active_hosts
    
    def port_scan(self, host: str, ports: List[int]) -> Dict[int, bool]:
        """Escaneia portas específicas"""
        open_ports = {}
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                open_ports[port] = (result == 0)
                sock.close()
            except:
                open_ports[port] = False
        
        return open_ports
    
    def identify_services(self, host: str) -> Dict:
        """Identifica serviços rodando no host"""
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5900, 8080]
        open_ports = self.port_scan(host, common_ports)
        
        services = {}
        service_map = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
            443: "HTTPS", 993: "IMAPS", 995: "POP3S",
            3389: "RDP", 5900: "VNC", 8080: "HTTP-Alt"
        }
        
        for port, is_open in open_ports.items():
            if is_open:
                services[port] = service_map.get(port, "Unknown")
        
        return services
    
    def device_fingerprinting(self, host: str) -> str:
        """Tenta identificar o tipo de dispositivo"""
        services = self.identify_services(host)
        
        # Lógica de identificação baseada em serviços
        if 22 in services and 80 in services:
            return "Router/Switch"
        elif 3389 in services:
            return "Windows Server"
        elif 22 in services and 443 in services:
            return "Linux Server"
        elif 443 in services and not 22 in services:
            return "Firewall/Appliance"
        elif 80 in services:
            return "Web Server"
        else:
            return "Unknown Device"

class SNMPMonitor:
    """Monitor SNMP para coleta de métricas"""
    
    def __init__(self):
        self.devices = []
        self.monitoring_active = False
    
    def add_device(self, ip: str, community: str = "public"):
        """Adiciona dispositivo para monitoramento"""
        # Simula coleta SNMP para demonstração
        device = SNMPDevice(
            ip=ip,
            community=community,
            device_type=self._get_device_type(ip),
            hostname=f"device-{ip.split('.')[-1]}",
            uptime=random.randint(86400, 2592000),
            interfaces=self._generate_interfaces(),
            cpu_usage=random.uniform(10, 80),
            memory_usage=random.uniform(20, 90),
            temperature=random.uniform(35, 65)
        )
        
        self.devices.append(device)
        print(f"📊 Dispositivo SNMP adicionado: {device.hostname} ({device.ip})")
        return device
    
    def _get_device_type(self, ip: str) -> str:
        """Simula identificação de tipo via SNMP"""
        device_types = ["Router", "Switch", "Server", "Firewall", "Access Point"]
        return random.choice(device_types)
    
    def _generate_interfaces(self) -> List[Dict]:
        """Gera interfaces simuladas"""
        interfaces = []
        interface_count = random.randint(4, 24)
        
        for i in range(interface_count):
            interface = {
                "name": f"GigabitEthernet0/{i+1}",
                "status": random.choice(["up", "down", "testing"]),
                "speed": random.choice([100, 1000, 10000]),  # Mbps
                "mtu": 1500,
                "in_octets": random.randint(1000000, 100000000),
                "out_octets": random.randint(1000000, 100000000),
                "in_errors": random.randint(0, 100),
                "out_errors": random.randint(0, 50),
                "utilization": random.uniform(0, 95)
            }
            interfaces.append(interface)
        
        return interfaces
    
    def collect_metrics(self, device: SNMPDevice) -> Dict:
        """Coleta métricas atualizadas de um dispositivo"""
        # Simula coleta SNMP real
        metrics = {
            "timestamp": datetime.now(),
            "cpu_usage": device.cpu_usage + random.uniform(-5, 5),
            "memory_usage": device.memory_usage + random.uniform(-10, 10),
            "temperature": device.temperature + random.uniform(-2, 2) if device.temperature else None,
            "uptime": device.uptime + 300,  # +5 minutos
            "interface_stats": []
        }
        
        # Atualiza estatísticas das interfaces
        for interface in device.interfaces:
            updated_interface = interface.copy()
            updated_interface.update({
                "in_octets": interface["in_octets"] + random.randint(1000, 10000),
                "out_octets": interface["out_octets"] + random.randint(1000, 10000),
                "utilization": max(0, min(100, interface["utilization"] + random.uniform(-5, 5)))
            })
            metrics["interface_stats"].append(updated_interface)
        
        return metrics
    
    def start_monitoring(self, interval: int = 300):
        """Inicia monitoramento contínuo"""
        self.monitoring_active = True
        
        def monitor_loop():
            while self.monitoring_active:
                for device in self.devices:
                    metrics = self.collect_metrics(device)
                    print(f"📈 {device.hostname}: CPU {metrics['cpu_usage']:.1f}% | "
                          f"Mem {metrics['memory_usage']:.1f}% | "
                          f"Temp {metrics['temperature']:.1f}°C")
                
                time.sleep(interval)
        
        monitor_thread = threading.Thread(target=monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print(f"🔄 Monitoramento SNMP iniciado (intervalo: {interval}s)")

class ConfigurationManager:
    """Gerenciador de configurações de dispositivos"""
    
    def __init__(self):
        self.config_templates = {}
        self.device_configs = {}
        self.backup_history = {}
    
    def create_template(self, template_name: str, template_content: str):
        """Cria template de configuração"""
        self.config_templates[template_name] = {
            "content": template_content,
            "created": datetime.now(),
            "variables": self._extract_variables(template_content)
        }
        print(f"📋 Template criado: {template_name}")
    
    def _extract_variables(self, content: str) -> List[str]:
        """Extrai variáveis do template"""
        variables = re.findall(r'\{\{(\w+)\}\}', content)
        return list(set(variables))
    
    def generate_config(self, template_name: str, variables: Dict) -> str:
        """Gera configuração a partir do template"""
        if template_name not in self.config_templates:
            raise ValueError(f"Template {template_name} não encontrado")
        
        template = self.config_templates[template_name]["content"]
        
        # Substitui variáveis
        for var, value in variables.items():
            template = template.replace(f"{{{{{var}}}}}", str(value))
        
        return template
    
    def backup_config(self, device_ip: str, config_content: str):
        """Faz backup da configuração"""
        timestamp = datetime.now()
        
        if device_ip not in self.backup_history:
            self.backup_history[device_ip] = []
        
        backup_entry = {
            "timestamp": timestamp,
            "config": config_content,
            "size": len(config_content),
            "hash": hash(config_content)
        }
        
        self.backup_history[device_ip].append(backup_entry)
        
        # Mantém apenas últimos 10 backups
        if len(self.backup_history[device_ip]) > 10:
            self.backup_history[device_ip] = self.backup_history[device_ip][-10:]
        
        print(f"💾 Backup realizado: {device_ip} ({len(config_content)} bytes)")
    
    def deploy_config(self, device_ip: str, config_content: str) -> bool:
        """Simula deploy de configuração"""
        print(f"🚀 Fazendo deploy em {device_ip}...")
        
        # Simula processo de deploy
        steps = [
            "Conectando ao dispositivo",
            "Validando configuração",
            "Fazendo backup da config atual",
            "Aplicando nova configuração",
            "Verificando conectividade",
            "Confirmando mudanças"
        ]
        
        for step in steps:
            print(f"   {step}...")
            time.sleep(0.5)
        
        # Simula sucesso (90% chance)
        success = random.random() > 0.1
        
        if success:
            self.device_configs[device_ip] = config_content
            print(f"✅ Deploy concluído com sucesso em {device_ip}")
        else:
            print(f"❌ Falha no deploy em {device_ip}")
        
        return success

class NetworkAutomation:
    """Sistema principal de automação de rede"""
    
    def __init__(self):
        self.scanner = NetworkScanner()
        self.snmp_monitor = SNMPMonitor()
        self.config_manager = ConfigurationManager()
        self.automation_tasks = []
    
    def discover_and_monitor(self, subnet: str = "192.168.1.0/24"):
        """Descobre dispositivos e inicia monitoramento"""
        print("🔍 Iniciando descoberta e monitoramento de rede")
        
        # Descoberta
        active_hosts = self.scanner.ping_sweep()
        
        # Identificação de dispositivos
        for host in active_hosts[:5]:  # Limita para demonstração
            device_type = self.scanner.device_fingerprinting(host)
            print(f"🔍 {host}: {device_type}")
            
            # Adiciona ao monitoramento SNMP
            if device_type in ["Router/Switch", "Linux Server", "Windows Server"]:
                self.snmp_monitor.add_device(host)
        
        # Inicia monitoramento
        self.snmp_monitor.start_monitoring(60)  # A cada 1 minuto
    
    def setup_vlan_automation(self):
        """Configura automação de VLAN"""
        vlan_template = """
! VLAN Configuration Template
vlan {{vlan_id}}
 name {{vlan_name}}
 state active
!
interface {{interface}}
 switchport mode access
 switchport access vlan {{vlan_id}}
 spanning-tree portfast
 no shutdown
!
        """
        
        self.config_manager.create_template("vlan_config", vlan_template)
        
        # Exemplo de deployment
        vlans = [
            {"vlan_id": 100, "vlan_name": "USERS", "interface": "GigabitEthernet0/10"},
            {"vlan_id": 200, "vlan_name": "SERVERS", "interface": "GigabitEthernet0/20"},
            {"vlan_id": 300, "vlan_name": "GUEST", "interface": "GigabitEthernet0/30"}
        ]
        
        for vlan in vlans:
            config = self.config_manager.generate_config("vlan_config", vlan)
            print(f"📋 Configuração VLAN {vlan['vlan_id']} gerada")
            
            # Simula deploy em switches
            for device in self.snmp_monitor.devices:
                if device.device_type == "Switch":
                    self.config_manager.deploy_config(device.ip, config)
    
    def security_policy_deployment(self):
        """Deploy de políticas de segurança"""
        firewall_template = """
! Security Policy Template
access-list {{acl_number}} extended deny ip {{source_network}} {{destination_network}}
access-list {{acl_number}} extended permit ip {{trusted_network}} any
access-list {{acl_number}} extended deny ip any any log
!
interface {{outside_interface}}
 access-group {{acl_number}} in
!
        """
        
        self.config_manager.create_template("security_policy", firewall_template)
        
        # Políticas de segurança
        policies = [
            {
                "acl_number": 101,
                "source_network": "203.0.113.0 255.255.255.0",
                "destination_network": "192.168.1.0 255.255.255.0",
                "trusted_network": "192.168.1.0 255.255.255.0",
                "outside_interface": "GigabitEthernet0/1"
            }
        ]
        
        for policy in policies:
            config = self.config_manager.generate_config("security_policy", policy)
            print("🔒 Política de segurança gerada")
            
            # Deploy em firewalls
            for device in self.snmp_monitor.devices:
                if device.device_type == "Firewall":
                    self.config_manager.deploy_config(device.ip, config)
    
    def bandwidth_monitoring(self):
        """Monitoramento e alertas de bandwidth"""
        print("📊 Iniciando monitoramento de bandwidth")
        
        for device in self.snmp_monitor.devices:
            metrics = self.snmp_monitor.collect_metrics(device)
            
            for interface in metrics["interface_stats"]:
                if interface["utilization"] > 80:
                    print(f"⚠️  ALERTA: {device.hostname} {interface['name']} - "
                          f"Utilização: {interface['utilization']:.1f}%")
                elif interface["utilization"] > 90:
                    print(f"🚨 CRÍTICO: {device.hostname} {interface['name']} - "
                          f"Utilização: {interface['utilization']:.1f}%")
    
    def automated_backup(self):
        """Backup automático de configurações"""
        print("💾 Executando backup automático de configurações")
        
        for device in self.snmp_monitor.devices:
            # Simula coleta de configuração
            config_content = f"""
! Configuration for {device.hostname}
! Backup generated on {datetime.now()}
!
hostname {device.hostname}
!
enable secret 5 $1$mERr$hx5rVt7rPNoS4wqbXKX7m0
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
            
            self.config_manager.backup_config(device.ip, config_content)
    
    def network_health_check(self):
        """Verifica saúde geral da rede"""
        print("🏥 Executando verificação de saúde da rede")
        
        health_report = {
            "total_devices": len(self.snmp_monitor.devices),
            "devices_up": 0,
            "devices_warning": 0,
            "devices_critical": 0,
            "total_interfaces": 0,
            "interfaces_up": 0,
            "high_utilization_interfaces": 0,
            "timestamp": datetime.now()
        }
        
        for device in self.snmp_monitor.devices:
            metrics = self.snmp_monitor.collect_metrics(device)
            
            # Status do dispositivo
            if metrics["cpu_usage"] < 70 and metrics["memory_usage"] < 80:
                health_report["devices_up"] += 1
            elif metrics["cpu_usage"] < 85 and metrics["memory_usage"] < 90:
                health_report["devices_warning"] += 1
            else:
                health_report["devices_critical"] += 1
            
            # Status das interfaces
            for interface in metrics["interface_stats"]:
                health_report["total_interfaces"] += 1
                
                if interface["status"] == "up":
                    health_report["interfaces_up"] += 1
                
                if interface["utilization"] > 80:
                    health_report["high_utilization_interfaces"] += 1
        
        # Exibir relatório
        print(f"📋 RELATÓRIO DE SAÚDE DA REDE:")
        print(f"   Dispositivos: {health_report['devices_up']} OK, "
              f"{health_report['devices_warning']} Warning, "
              f"{health_report['devices_critical']} Critical")
        print(f"   Interfaces: {health_report['interfaces_up']}/{health_report['total_interfaces']} UP")
        print(f"   Alta utilização: {health_report['high_utilization_interfaces']} interfaces")
        
        return health_report

def main():
    """Demonstração completa do sistema de automação"""
    
    print("🤖 SISTEMA DE AUTOMAÇÃO DE REDE")
    print("=" * 50)
    
    # Inicializar sistema
    automation = NetworkAutomation()
    
    # 1. Descoberta e monitoramento
    print("\n1️⃣ DESCOBERTA E MONITORAMENTO")
    automation.discover_and_monitor("192.168.1.0/24")
    
    time.sleep(2)
    
    # 2. Automação de VLAN
    print("\n2️⃣ AUTOMAÇÃO DE VLAN")
    automation.setup_vlan_automation()
    
    # 3. Deploy de políticas de segurança
    print("\n3️⃣ POLÍTICAS DE SEGURANÇA")
    automation.security_policy_deployment()
    
    # 4. Monitoramento de bandwidth
    print("\n4️⃣ MONITORAMENTO DE BANDWIDTH")
    automation.bandwidth_monitoring()
    
    # 5. Backup automático
    print("\n5️⃣ BACKUP AUTOMÁTICO")
    automation.automated_backup()
    
    # 6. Verificação de saúde
    print("\n6️⃣ VERIFICAÇÃO DE SAÚDE")
    health_report = automation.network_health_check()
    
    # 7. Salvar dados para dashboard
    dashboard_data = {
        "devices": [
            {
                "hostname": device.hostname,
                "ip": device.ip,
                "type": device.device_type,
                "cpu_usage": device.cpu_usage,
                "memory_usage": device.memory_usage,
                "uptime": device.uptime,
                "interface_count": len(device.interfaces)
            }
            for device in automation.snmp_monitor.devices
        ],
        "health_report": health_report,
        "templates": list(automation.config_manager.config_templates.keys()),
        "backup_count": sum(len(backups) for backups in automation.config_manager.backup_history.values()),
        "timestamp": datetime.now().isoformat()
    }
    
    # Salvar dados
    with open('C:/security-network-portfolio/data/network_automation_data.json', 'w') as f:
        json.dump(dashboard_data, f, indent=2, default=str)
    
    print("\n✅ AUTOMAÇÃO DE REDE CONCLUÍDA!")
    print(f"📊 Dispositivos monitorados: {len(automation.snmp_monitor.devices)}")
    print(f"📋 Templates criados: {len(automation.config_manager.config_templates)}")
    print(f"💾 Backups realizados: {sum(len(backups) for backups in automation.config_manager.backup_history.values())}")
    print("🎯 Portfolio de Network Engineering demonstrado!")

if __name__ == "__main__":
    main()
