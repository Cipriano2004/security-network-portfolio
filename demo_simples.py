#!/usr/bin/env python3
"""
Demo Simplificado - Portfolio SOC/NOC
Demonstração sem dependências externas
"""

import json
import time
import random
from datetime import datetime
import webbrowser
import os

def banner():
    """Exibe banner do sistema"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🔐 SOC/NOC OPERATIONS CENTER 🌐                          ║
║                                                                              ║
║              Portfolio Demonstração - Cybersecurity & Network               ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

def simular_descoberta_rede():
    """Simula descoberta de dispositivos na rede"""
    print("\n🔍 DESCOBERTA DE REDE")
    print("=" * 50)
    
    dispositivos = [
        {"ip": "192.168.1.254", "nome": "FW-CORE-01", "tipo": "Firewall", "status": "Online"},
        {"ip": "192.168.1.1", "nome": "RTR-WAN-01", "tipo": "Router", "status": "Online"},
        {"ip": "192.168.1.10", "nome": "SW-CORE-01", "tipo": "Switch", "status": "Online"},
        {"ip": "192.168.1.11", "nome": "SW-ACCESS-01", "tipo": "Switch", "status": "Warning"},
        {"ip": "192.168.1.20", "nome": "SRV-WEB-01", "tipo": "Server", "status": "Online"},
        {"ip": "192.168.1.21", "nome": "SRV-DB-01", "tipo": "Server", "status": "Online"},
        {"ip": "192.168.1.22", "nome": "SRV-BACKUP", "tipo": "Server", "status": "Warning"},
        {"ip": "192.168.1.100", "nome": "AP-FLOOR1-01", "tipo": "Access Point", "status": "Online"},
        {"ip": "192.168.1.101", "nome": "AP-FLOOR2-01", "tipo": "Access Point", "status": "Online"},
        {"ip": "192.168.1.53", "nome": "SRV-DNS-01", "tipo": "Server", "status": "Online"}
    ]
    
    for dispositivo in dispositivos:
        print(f"✅ {dispositivo['nome']} ({dispositivo['ip']}) - {dispositivo['tipo']} - {dispositivo['status']}")
        time.sleep(0.3)
    
    print(f"\n📊 Total de dispositivos descobertos: {len(dispositivos)}")
    return dispositivos

def simular_analise_seguranca():
    """Simula análise de segurança"""
    print("\n🔒 ANÁLISE DE SEGURANÇA")
    print("=" * 50)
    
    eventos = [
        {"tipo": "INFO", "evento": "Login bem-sucedido: admin@empresa.com"},
        {"tipo": "WARNING", "evento": "Tentativas de login falharam: 192.168.1.150"},
        {"tipo": "CRITICAL", "evento": "Malware detectado em anexo de email"},
        {"tipo": "INFO", "evento": "Firewall: 127 ameaças bloqueadas nas últimas 24h"},
        {"tipo": "WARNING", "evento": "Tráfego anômalo detectado na VLAN 100"}
    ]
    
    for evento in eventos:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {evento['tipo']}: {evento['evento']}")
        time.sleep(0.5)
    
    # Métricas de ML simuladas
    print(f"\n🤖 MODELOS DE MACHINE LEARNING:")
    print(f"   • Isolation Forest: 94.2% de precisão")
    print(f"   • Random Forest: 96.8% de precisão")
    print(f"   • DBSCAN Clustering: 89.7% de precisão")

def simular_automacao_rede():
    """Simula automação de rede"""
    print("\n🌐 AUTOMAÇÃO DE REDE")
    print("=" * 50)
    
    tarefas = [
        "Configurando VLAN 100 (USERS)",
        "Configurando VLAN 200 (SERVERS)", 
        "Configurando VLAN 300 (GUEST)",
        "Aplicando políticas de segurança no firewall",
        "Fazendo backup das configurações",
        "Verificando conectividade entre VLANs",
        "Atualizando tabelas de roteamento"
    ]
    
    for tarefa in tarefas:
        print(f"⚙️  {tarefa}...")
        time.sleep(0.8)
        print(f"   ✅ Concluído!")
    
    print(f"\n📋 Automação de rede executada com sucesso!")

def simular_monitoramento():
    """Simula monitoramento em tempo real"""
    print("\n📊 MONITORAMENTO EM TEMPO REAL")
    print("=" * 50)
    
    print("Coletando métricas dos dispositivos...")
    time.sleep(1)
    
    metricas = [
        {"dispositivo": "FW-CORE-01", "cpu": "23%", "memoria": "45%", "uptime": "45d 12h"},
        {"dispositivo": "RTR-WAN-01", "cpu": "34%", "memoria": "67%", "uptime": "23d 8h"},
        {"dispositivo": "SW-CORE-01", "cpu": "12%", "memoria": "34%", "uptime": "67d 4h"},
        {"dispositivo": "SRV-WEB-01", "cpu": "45%", "memoria": "72%", "uptime": "156d 2h"},
        {"dispositivo": "SRV-DB-01", "cpu": "67%", "memoria": "83%", "uptime": "89d 14h"}
    ]
    
    for metrica in metricas:
        print(f"📈 {metrica['dispositivo']}: CPU {metrica['cpu']} | RAM {metrica['memoria']} | Uptime {metrica['uptime']}")
        time.sleep(0.4)

def gerar_relatorio():
    """Gera relatório final"""
    print("\n📋 RELATÓRIO FINAL SOC/NOC")
    print("=" * 50)
    
    relatorio = {
        "timestamp": datetime.now().isoformat(),
        "dispositivos_monitorados": 10,
        "dispositivos_online": 8,
        "dispositivos_warning": 2,
        "dispositivos_offline": 0,
        "eventos_seguranca": 847,
        "ameacas_bloqueadas": 127,
        "vlans_configuradas": 3,
        "backups_realizados": 10,
        "eficiencia_automacao": "95.2%",
        "precisao_ml": "94.2%"
    }
    
    for chave, valor in relatorio.items():
        if chave != "timestamp":
            print(f"   {chave.replace('_', ' ').title()}: {valor}")
    
    # Salvar relatório
    with open('relatorio_soc_noc.json', 'w') as f:
        json.dump(relatorio, f, indent=2)
    
    print(f"\n💾 Relatório salvo em: relatorio_soc_noc.json")

def abrir_dashboard():
    """Abre o dashboard no navegador"""
    dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard', 'index.html')
    
    if os.path.exists(dashboard_path):
        print(f"\n🌐 Abrindo dashboard...")
        webbrowser.open(f'file://{os.path.abspath(dashboard_path)}')
        print(f"✅ Dashboard aberto em: {dashboard_path}")
    else:
        print(f"❌ Dashboard não encontrado")

def menu_principal():
    """Menu interativo principal"""
    while True:
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                             🎯 MENU PRINCIPAL                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

[1] 🔍 Descoberta de Rede
[2] 🔒 Análise de Segurança  
[3] 🌐 Automação de Rede
[4] 📊 Monitoramento em Tempo Real
[5] 🌐 Abrir Dashboard
[6] 🚀 Demo Completa (executa tudo)
[7] 📋 Gerar Relatório
[8] ❌ Sair
        """)
        
        escolha = input("Escolha uma opção (1-8): ").strip()
        
        if escolha == '1':
            simular_descoberta_rede()
        elif escolha == '2':
            simular_analise_seguranca()
        elif escolha == '3':
            simular_automacao_rede()
        elif escolha == '4':
            simular_monitoramento()
        elif escolha == '5':
            abrir_dashboard()
        elif escolha == '6':
            print("\n🚀 EXECUTANDO DEMO COMPLETA...")
            simular_descoberta_rede()
            simular_analise_seguranca()
            simular_automacao_rede()
            simular_monitoramento()
            gerar_relatorio()
            abrir_dashboard()
            print("\n✅ Demo completa executada!")
        elif escolha == '7':
            gerar_relatorio()
        elif escolha == '8':
            print("\n👋 Demonstração SOC/NOC concluída!")
            print("🎯 Portfolio apresentado com sucesso!")
            break
        else:
            print("❌ Opção inválida! Escolha entre 1-8.")
        
        input("\nPressione ENTER para continuar...")

def main():
    """Função principal"""
    banner()
    
    print("🎯 Bem-vindo ao Portfolio SOC/NOC Operations Center!")
    print("\nEste demo simplificado demonstra:")
    print("  • Descoberta automática de dispositivos")
    print("  • Análise de segurança e detecção de ameaças")
    print("  • Automação de configurações de rede")
    print("  • Monitoramento em tempo real")
    print("  • Dashboard profissional")
    
    print("\n✅ Sistema pronto para demonstração!")
    
    menu_principal()

if __name__ == "__main__":
    main()
