@echo off
echo ===================================================
echo   INICIANDO AUTOMACAO ETL - MERCADO FINANCEIRO
echo ===================================================
echo.

:: 1. Entra na pasta do projeto (O uso de aspas garante que o Windows entenda os espaços no nome "Área de Trabalho")
cd /d "C:\Users\dudu1\OneDrive\Área de Trabalho\dudu\ETL_Mercado_Financeiro"

:: 2. Ativa o Ambiente Virtual
call venv\Scripts\activate.bat

:: 3. Executa o orquestrador
python src\main.py

echo.
echo ===================================================
echo   PROCESSO FINALIZADO
echo ===================================================

:: O pause mantem a tela preta aberta para voce ler os logs. 
:: Quando for agendar no Windows, voce pode apagar a palavra pause se quiser que feche sozinho.
pause