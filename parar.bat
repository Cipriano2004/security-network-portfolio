@echo off
title Parando Portfolio SOC/NOC
color 0C

echo.
echo 🛑 PARANDO PORTFOLIO SOC/NOC...
echo.

echo 🔄 Parando monitor de estabilidade...
taskkill /f /fi "WINDOWTITLE eq*MONITOR*" >nul 2>&1
taskkill /f /im cmd.exe /fi "WINDOWTITLE eq*monitor*" >nul 2>&1

echo ⚡ Finalizando processos Python...
taskkill /f /im python.exe /t >nul 2>&1

echo 🔌 Liberando porta 8080...
netstat -ano | findstr :8080 >nul
if %errorlevel% equ 0 (
    for /f "tokens=5" %%p in ('netstat -ano ^| findstr :8080') do (
        taskkill /f /pid %%p >nul 2>&1
    )
)

echo ✅ Portfolio parado com sucesso!
echo    • Servidor Python finalizado
echo    • Monitor de estabilidade parado
echo    • Porta 8080 liberada
echo.
echo 📊 Para reiniciar, execute: iniciar_portfolio.bat
echo.
timeout /t 3 /nobreak >nul
