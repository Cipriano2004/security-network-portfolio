#!/usr/bin/env python3
"""
Demo Script - Portfolio Cybersecurity e Network Engineering
Demonstração completa das capacidades do portfolio
"""

import sys
import os
import json
import time
import threading
from datetime import datetime

def banner():
    """Exibe banner do sistema"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🔐 SOC/NOC OPERATIONS CENTER 🌐                          ║
║                                                                              ║
║    Portfolio Profissional - Cybersecurity Analyst & Network Engineer       ║
║                              Junior Level                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

def check_dependencies():
    """Verifica dependências necessárias"""
    print("🔍 Verificando dependências...")
    
    required_packages = ['pandas', 'numpy', 'scikit-learn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Pacotes faltando: {', '.join(missing_packages)}")
        print("Execute: pip install pandas numpy scikit-learn")
        return False
    
    print("✅ Todas as dependências estão disponíveis!")
    return True

def run_security_analysis():
    """Executa análise de segurança com ML"""
    print("\n🔒 INICIANDO ANÁLISE DE SEGURANÇA COM ML")
    print("=" * 60)
    
    try:
        # Importa e executa análise de segurança
        sys.path.append(os.path.join(os.path.dirname(__file__), 'threat-detection'))
        from ml_security_analysis import SecurityAnalysisSystem
        
        security_system = SecurityAnalysisSystem()
        
        print("📊 Gerando dados de segurança...")
        security_system.data_generator.generate_dataset(1000)
        
        print("🧠 Treinando modelos de ML...")
        security_system.ml_detector.train_models()
        
        print("🔍 Detectando anomalias...")
        security_system.ml_detector.detect_anomalies()
        
        print("📈 Gerando relatórios...")
        security_system.generate_comprehensive_report()
        
        print("✅ Análise de segurança concluída!")
        
    except Exception as e:
        print(f"❌ Erro na análise de segurança: {e}")

def run_network_automation():
    """Executa automação de rede"""
    print("\n🌐 INICIANDO AUTOMAÇÃO DE REDE")
    print("=" * 60)
    
    try:
        # Importa e executa automação de rede
        sys.path.append(os.path.join(os.path.dirname(__file__), 'network-automation'))
        from network_automation import NetworkAutomation
        
        automation = NetworkAutomation()
        
        print("🔍 Descobrindo dispositivos na rede...")
        automation.discover_and_monitor("192.168.1.0/24")
        
        time.sleep(1)
        
        print("📋 Configurando VLANs automaticamente...")
        automation.setup_vlan_automation()
        
        print("🔒 Implementando políticas de segurança...")
        automation.security_policy_deployment()
        
        print("📊 Monitorando bandwidth...")
        automation.bandwidth_monitoring()
        
        print("💾 Realizando backup de configurações...")
        automation.automated_backup()
        
        print("🏥 Verificando saúde da rede...")
        automation.network_health_check()
        
        print("✅ Automação de rede concluída!")
        
    except Exception as e:
        print(f"❌ Erro na automação de rede: {e}")

def run_soc_operations():
    """Executa operações SOC/NOC"""
    print("\n🚨 INICIANDO OPERAÇÕES SOC/NOC")
    print("=" * 60)
    
    try:
        # Importa e executa operações SOC/NOC
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from soc_noc_operations import SOCNOCSystem
        
        soc_system = SOCNOCSystem()
        
        print("🔍 Executando descoberta de rede...")
        soc_system.network_discovery.discover_network("192.168.1.0/24")
        
        print("🛡️  Iniciando detecção de ameaças...")
        soc_system.threat_detector.analyze_network_traffic()
        
        print("🚨 Processando incidentes...")
        soc_system.incident_handler.process_alerts()
        
        print("⚙️  Executando automações...")
        soc_system.automation.execute_predefined_tasks()
        
        print("✅ Operações SOC/NOC concluídas!")
        
    except Exception as e:
        print(f"❌ Erro nas operações SOC/NOC: {e}")

def generate_dashboard_data():
    """Gera dados para o dashboard"""
    print("\n📊 GERANDO DADOS PARA DASHBOARD")
    print("=" * 60)
    
    dashboard_data = {
        "timestamp": datetime.now().isoformat(),
        "system_status": "operational",
        "security_metrics": {
            "threats_blocked": 127,
            "malware_detected": 5,
            "intrusion_attempts": 23,
            "vulnerabilities_found": 8,
            "security_score": 92.5
        },
        "network_metrics": {
            "devices_monitored": 15,
            "interfaces_active": 48,
            "bandwidth_utilization": 67.3,
            "network_uptime": 99.97,
            "response_time": 2.1
        },
        "automation_metrics": {
            "tasks_automated": 24,
            "configs_deployed": 12,
            "backups_completed": 48,
            "policies_enforced": 15,
            "automation_efficiency": 95.2
        },
        "ml_metrics": {
            "anomalies_detected": 3,
            "models_trained": 3,
            "accuracy_isolation_forest": 94.2,
            "accuracy_random_forest": 96.8,
            "false_positive_rate": 2.1
        }
    }
    
    # Salva dados no arquivo
    data_file = os.path.join(os.path.dirname(__file__), 'data', 'dashboard_data.json')
    
    try:
        with open(data_file, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        print(f"✅ Dados salvos em: {data_file}")
    except Exception as e:
        print(f"❌ Erro ao salvar dados: {e}")

def open_dashboard():
    """Abre o dashboard no navegador"""
    print("\n🌐 ABRINDO DASHBOARD")
    print("=" * 60)
    
    dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard', 'index.html')
    
    if os.path.exists(dashboard_path):
        import webbrowser
        try:
            webbrowser.open(f'file://{os.path.abspath(dashboard_path)}')
            print(f"✅ Dashboard aberto: {dashboard_path}")
        except Exception as e:
            print(f"❌ Erro ao abrir dashboard: {e}")
    else:
        print(f"❌ Dashboard não encontrado: {dashboard_path}")

def show_portfolio_summary():
    """Exibe resumo do portfolio"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           📋 RESUMO DO PORTFOLIO                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🔒 CYBERSECURITY CAPABILITIES:                                              ║
║     • Machine Learning Threat Detection (Isolation Forest, Random Forest)   ║
║     • Security Information and Event Management (SIEM)                      ║
║     • Incident Response and Automated Remediation                           ║
║     • Vulnerability Assessment and Penetration Testing                      ║
║     • Real-time Security Monitoring and Alerting                            ║
║                                                                              ║
║  🌐 NETWORK ENGINEERING CAPABILITIES:                                        ║
║     • Automated Network Discovery and Mapping                               ║
║     • SNMP Monitoring and Performance Analysis                              ║
║     • VLAN Configuration and Management                                     ║
║     • Firewall Policy Automation                                            ║
║     • Configuration Backup and Change Management                            ║
║                                                                              ║
║  ⚙️  AUTOMATION & TOOLS:                                                     ║
║     • Python-based Network Automation                                       ║
║     • RESTful API Development                                               ║
║     • Database Management (SQLite)                                          ║
║     • Configuration Template Management                                     ║
║     • Real-time Dashboard with HTML/CSS/JavaScript                         ║
║                                                                              ║
║  📊 TECHNICAL PROFICIENCIES:                                                 ║
║     • Programming: Python, JavaScript, SQL                                  ║
║     • Frameworks: scikit-learn, pandas, numpy                               ║
║     • Protocols: SNMP, TCP/IP, HTTP/HTTPS                                   ║
║     • Security: SIEM, IDS/IPS, Threat Intelligence                          ║
║     • Networking: Switching, Routing, VLANs, Firewalls                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

def interactive_menu():
    """Menu interativo para demonstração"""
    while True:
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                             🎯 MENU PRINCIPAL                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

[1] 🔒 Executar Análise de Segurança com ML
[2] 🌐 Executar Automação de Rede
[3] 🚨 Executar Operações SOC/NOC
[4] 📊 Gerar Dados para Dashboard
[5] 🌐 Abrir Dashboard no Navegador
[6] 📋 Visualizar Resumo do Portfolio
[7] 🚀 Executar Demo Completa
[8] ❌ Sair

        """)
        
        choice = input("Escolha uma opção (1-8): ").strip()
        
        if choice == '1':
            run_security_analysis()
        elif choice == '2':
            run_network_automation()
        elif choice == '3':
            run_soc_operations()
        elif choice == '4':
            generate_dashboard_data()
        elif choice == '5':
            open_dashboard()
        elif choice == '6':
            show_portfolio_summary()
        elif choice == '7':
            print("\n🚀 EXECUTANDO DEMO COMPLETA...")
            print("=" * 60)
            
            run_security_analysis()
            time.sleep(1)
            run_network_automation()
            time.sleep(1)
            run_soc_operations()
            time.sleep(1)
            generate_dashboard_data()
            time.sleep(1)
            open_dashboard()
            
            print("\n✅ DEMO COMPLETA CONCLUÍDA!")
            print("🎯 Portfolio demonstrado com sucesso!")
            
        elif choice == '8':
            print("\n👋 Obrigado por visualizar o portfolio!")
            print("🎯 Demonstração de competências SOC/NOC concluída!")
            break
        else:
            print("❌ Opção inválida! Escolha entre 1-8.")
        
        input("\nPressione ENTER para continuar...")

def main():
    """Função principal do demo"""
    banner()
    
    print("🎯 Bem-vindo à demonstração do Portfolio SOC/NOC!")
    print("Este portfolio demonstra competências em:")
    print("  • Cybersecurity Analysis (Junior Level)")
    print("  • Network Engineering (Junior Level)")
    print("  • Security Operations Center (SOC)")
    print("  • Network Operations Center (NOC)")
    
    if not check_dependencies():
        print("\n❌ Execute primeiro: pip install pandas numpy scikit-learn")
        return
    
    print("\n🚀 Sistema pronto para demonstração!")
    
    # Pergunta se quer executar demo automática ou menu interativo
    print("\nEscolha o modo de demonstração:")
    print("[1] 🚀 Demo Automática (executa tudo)")
    print("[2] 🎯 Menu Interativo (escolha individual)")
    
    mode = input("Modo (1 ou 2): ").strip()
    
    if mode == '1':
        print("\n🚀 INICIANDO DEMO AUTOMÁTICA...")
        
        run_security_analysis()
        time.sleep(2)
        run_network_automation()
        time.sleep(2)
        run_soc_operations()
        time.sleep(2)
        generate_dashboard_data()
        time.sleep(1)
        open_dashboard()
        
        show_portfolio_summary()
        
        print("\n✅ DEMO AUTOMÁTICA CONCLUÍDA!")
        print("🎯 Portfolio SOC/NOC demonstrado com sucesso!")
        
    elif mode == '2':
        interactive_menu()
    else:
        print("❌ Opção inválida!")

if __name__ == "__main__":
    main()
