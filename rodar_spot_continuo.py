"""
LOOP CONTÍNUO: SIMULADOR SPOT BINANCE (PAPER TRADING)
Roda a cada 60 segundos com cotações reais da Binance.
- Verifica posições abertas
- Vende no Take Profit (+2%)
- Compra novas oportunidades quando houver saldo
- Atualiza saldo e diário automaticamente
"""

import time
import sys
import io
from spot_paper_engine import BinanceSpotPaperEngine

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def main():
    engine = BinanceSpotPaperEngine()
    print("\n🟢 SIMULADOR SPOT BINANCE ATIVO EM TEMPO REAL!")
    print("Para pausar o robô a qualquer momento, pressione Ctrl + C.\n")

    while True:
        try:
            engine.run_cycle()
            time.sleep(60) # Verifica a cada 60 segundos
        except KeyboardInterrupt:
            print("\n[!] Simulador pausado pelo usuário.")
            break
        except Exception as e:
            print(f"[!] Erro no ciclo: {e}")
            time.sleep(10)

if __name__ == '__main__':
    main()
