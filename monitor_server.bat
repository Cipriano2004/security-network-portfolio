@echo off
echo ========================================
echo     MONITOR DE ESTABILIDADE DO SERVIDOR
echo ========================================
echo.

:LOOP
echo [%TIME%] Verificando servidor...

curl -s http://localhost:8080/api/system >nul 2>&1
if %errorlevel% == 0 (
    echo [%TIME%] ✅ Servidor funcionando normalmente
) else (
    echo [%TIME%] ❌ Servidor não responde - Reiniciando...
    
    REM Matar processos Python
    taskkill /f /im python.exe >nul 2>&1
    timeout /t 3 >nul
    
    REM Reiniciar servidor
    start /min python data_server.py
    timeout /t 10 >nul
    
    echo [%TIME%] 🔄 Servidor reiniciado
)

REM Aguardar 30 segundos antes da próxima verificação
timeout /t 30 >nul
goto LOOP
