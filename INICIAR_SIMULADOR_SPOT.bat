@echo off
chcp 65001 > nul
title ROBÔ BINANCE SPOT - SIMULADOR PAPER TRADING (BANCA R$ 50)
color 0A
cls
echo ====================================================================
echo   🚀 INICIANDO SIMULADOR BINANCE SPOT (DADOS REAIS EM TEMPO REAL)
echo   💰 Banca Inicial Simulada: R$ 50,00 ^| Ordem: R$ 10,00
echo   🏛️ 3 Leis de Ouro: Velas de 1H ^| Mercado Spot ^| Filtro SMA 200
echo ====================================================================
echo.
python rodar_spot_continuo.py
pause
