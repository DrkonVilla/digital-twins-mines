@echo off
title Lanzador de Langflow - Sistema M-11 Minero
echo ========================================================
echo   Iniciando Langflow para Modelos Predictivos M-11
echo ========================================================
echo.
echo Verificando instalacion de Langflow...
python -m langflow --help >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Langflow no esta instalado en este entorno de Python.
    echo Instalando langflow con pip...
    pip install langflow
)

echo.
echo Iniciando servidor Langflow en http://localhost:7860 ...
echo Puedes importar el flujo desde: langflow\mining_risk_prediction_flow.json
echo.
python -m langflow run --host 127.0.0.1 --port 7860
pause
