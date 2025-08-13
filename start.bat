@echo off
cls
title Portfolio SOC/NOC - Cybersecurity & Network Engineering
color 0B

echo.
echo ===============================================
echo   SOC/NOC OPERATIONS CENTER - PORTFOLIO
echo   🔥 95+ DISPOSITIVOS | 10 SEÇÕES FUNCIONAIS
echo ===============================================
echo.
echo 🚀 Iniciando sistema com dados REAIS...
echo.

cd /d "%~dp0"

echo ⚡ 1. Iniciando servidor de dados...
start /min python data_server.py

echo ⏳ 2. Aguardando servidor inicializar (scan completo 1-254)...
timeout /t 5 /nobreak >nul

echo 🌐 3. Abrindo dashboard profissional...
start http://localhost:8080

echo.
echo ✅ PORTFOLIO INICIADO COM SUCESSO!
echo.
echo 📊 RECURSOS DISPONÍVEIS:
echo    • Dashboard: http://localhost:8080
echo    • 95+ dispositivos de rede descobertos
echo    • 10 seções funcionais (SOC/NOC)
echo    • APIs REST em tempo real
echo    • Dados 100%% reais (não simulação)
echo.
echo 🎯 SEÇÕES DO DASHBOARD:
echo    • Threat Detection      • Performance Monitoring
echo    • Incident Response     • Security Automation  
echo    • Vulnerability Mgmt    • Compliance Management
echo    • Network Topology      • Machine Learning
echo    • Security Reports      • System Metrics
echo.
echo 🔥 PRONTO PARA APRESENTAÇÃO!
echo    Perfeito para impressionar recrutadores
echo.
echo ⚠️  Para parar: Feche esta janela
pause
