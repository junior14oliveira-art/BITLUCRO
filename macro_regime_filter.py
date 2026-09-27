"""
MÓDULO: FILTRO DE TENDÊNCIA GLOBAL MACRO (LEI #3)
Verifica a Média Móvel de 200 períodos do Bitcoin na Binance.
Se BTC > SMA200: 🟢 AUTORIZADO A COMPRAR NO SPOT
Se BTC < SMA200: 🛑 MERCADO EM RISCO - FICAR 100% EM DÓLAR (USDT)
"""

import requests
import json
import sys
import io

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

BINANCE_API_URL = "https://api.binance.com/api/v3"

def verificar_tendencia_macro_btc():
    print("\n" + "=" * 65)
    print("🛡️ [LEI #3] VERIFICANDO O FILTRO DE TENDÊNCIA GLOBAL DO BITCOIN")
    print("=" * 65)

    try:
        # Busca as últimas 200 velas diárias (1d) do Bitcoin na Binance
        url = f"{BINANCE_API_URL}/klines?symbol=BTCUSDT&interval=1d&limit=200"
        candles = requests.get(url, timeout=5).json()

        if not candles or len(candles) < 200:
            print("[-] Não foi possível carregar o histórico de 200 dias.")
            return False

        # Extrai os preços de fechamento
        fechamentos = [float(c[4]) for c in candles]
        btc_preco_atual = fechamentos[-1]
        
        # Média Móvel Simples de 200 dias (SMA 200)
        sma_200 = sum(fechamentos) / len(fechamentos)

        distancia_pct = ((btc_preco_atual - sma_200) / sma_200) * 100

        print(f"\n📊 Cotação Atual do Bitcoin:  $ {btc_preco_atual:,.2f}")
        print(f"📈 Média Móvel de 200 Dias:  $ {sma_200:,.2f}")
        print(f"📍 Distância da Média:       {distancia_pct:+.2f}%")

        print("-" * 65)
        if btc_preco_atual >= sma_200:
            print("🟢 [REGIME DE ALTA CONFIRMADO]: Bitcoin ACIMA da SMA 200!")
            print("✅ O Robô de IA tem PERMISSÃO TOTAL para caçar compras no Spot.")
            print("🚀 O vento está a favor do mercado; risco de colapso repentino é baixo.")
            return True
        else:
            print("🛑 [ALERTA DE RISCO]: Bitcoin ABAIXO da SMA 200!")
            print("🛡️ REGRA ATIVADA: Robô cruza os braços e protege o capital 100% em USDT.")
            print("⏸️ Nenhuma compra permitida até o mercado se recuperar acima da SMA 200.")
            return False

    except Exception as e:
        print(f"[-] Erro ao verificar regime: {e}")
        return False

if __name__ == '__main__':
    verificar_tendencia_macro_btc()
