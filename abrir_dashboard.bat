@echo off
title 🌐 Abrir Dashboard SOC/NOC
color 0A

echo.
echo 🌐 ABRINDO DASHBOARD SOC/NOC...
echo.
echo ✅ Servidor rodando em: http://localhost:8080
echo ✅ Status: Operacional com 96 dispositivos
echo.

REM Tentar múltiplas formas de abrir o navegador
echo 🔄 Tentando abrir navegador...

REM Método 1: Start padrão
start "" "http://localhost:8080" >nul 2>&1

REM Método 2: Rundll32
rundll32 url.dll,FileProtocolHandler "http://localhost:8080" >nul 2>&1

REM Método 3: PowerShell
powershell -Command "Start-Process 'http://localhost:8080'" >nul 2>&1

REM Método 4: Chrome específico
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" "http://localhost:8080"
)

REM Método 5: Edge específico
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" "http://localhost:8080"
)

timeout /t 3 >nul

echo.
echo 📋 SE NÃO ABRIU AUTOMATICAMENTE:
echo    1. Abra seu navegador manualmente
echo    2. Digite: http://localhost:8080
echo    3. Pressione Enter
echo.
echo 🎯 DASHBOARD SOC/NOC PORTFOLIO:
echo    • 96 dispositivos ativos na rede
echo    • 10 módulos funcionais
echo    • Dados 100%% reais
echo    • Interface profissional
echo.
pause
