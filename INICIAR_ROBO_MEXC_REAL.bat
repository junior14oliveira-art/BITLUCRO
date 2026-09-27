@echo off
chcp 65001 > nul
title BITLUCRO SPOT - MEXC REAL 24/7
color 0A

echo ========================================================
echo        BITLUCRO SPOT - ROBO OFICIAL MEXC (REAL)
echo ========================================================
echo.
echo Conectando na conta MEXC com chave de API segura...
echo.

python rodar_mexc_real.py

pause
