"""
MÓDULO 1: INTRODUÇÃO PRÁTICA AO MERCADO SPOT DA BINANCE
- Conexão direta com a API Oficial da Binance (100% Gratuita e sem necessidade de chave agora)
- Monitoramento de Cotações em Reais (BRL) e Dólares (USDT)
- Cálculo da Volatilidade Diária para Lucro com Robô de Grid / Swing
"""

import requests
import json
import time
import sys
import io
from datetime import datetime

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

BINANCE_API_URL = "https://api.binance.com/api/v3"

def testar_conexao():
    print("\n" + "=" * 65)
    print("🚀 [AULA 1] CONECTANDO À API OFICIAL DA BINANCE (MERCADO SPOT)")
    print("=" * 65)
    
    try:
        t0 = time.time()
        res = requests.get(f"{BINANCE_API_URL}/ping", timeout=5)
        latencia_ms = int((time.time() - t0) * 1000)
        
        if res.status_code == 200:
            print(f"✅ Conexão Estabelecida com Sucesso! (Latência: {latencia_ms}ms)")
        else:
            print(f"[-] Erro na conexão: Status {res.status_code}")
            return False
    except Exception as e:
        print(f"[-] Falha ao conectar na Binance: {e}")
        return False

    return True

def escanear_melhores_pares_spot():
    print("\n🔍 Analisando os Pares mais Negociados para Operar com Pouco Dinheiro...")
    
    # Pares em Reais (BRL) e Dólares (USDT)
    pares_alvo = [
        {"simbolo": "BTCBRL", "nome": "Bitcoin em Reais (BRL)", "min_ordem": "R$ 10,00"},
        {"simbolo": "ETHBRL", "nome": "Ethereum em Reais (BRL)", "min_ordem": "R$ 10,00"},
        {"simbolo": "SOLBRL", "nome": "Solana em Reais (BRL)", "min_ordem": "R$ 10,00"},
        {"simbolo": "SOLUSDT", "nome": "Solana em Dólar (USDT)", "min_ordem": "$5.00"},
        {"simbolo": "NEARUSDT", "nome": "NEAR Protocol (Alta Volatilidade)", "min_ordem": "$5.00"},
        {"simbolo": "RENDERUSDT", "nome": "Render IA (Forte Oscilação)", "min_ordem": "$5.00"}
    ]
    
    resultados = []
    
    for p in pares_alvo:
        try:
            url = f"{BINANCE_API_URL}/ticker/24hr?symbol={p['simbolo']}"
            res = requests.get(url, timeout=5).json()
            
            preco_atual = float(res['lastPrice'])
            variacao_pct = float(res['priceChangePercent'])
            maxima_24h = float(res['highPrice'])
            minima_24h = float(res['lowPrice'])
            volume_milhoes = float(res['quoteVolume']) / 1_000_000
            
            # Margem de oscilação do dia (o "espaço" que o robô tem para lucrar)
            oscilacao_dia = ((maxima_24h - minima_24h) / minima_24h) * 100
            
            resultados.append({
                "simbolo": p['simbolo'],
                "nome": p['nome'],
                "min": p['min_ordem'],
                "preco": preco_atual,
                "variacao": variacao_pct,
                "max": maxima_24h,
                "min_dia": minima_24h,
                "oscilacao": oscilacao_dia,
                "vol": volume_milhoes
            })
        except Exception:
            continue
            
    print("\n" + "-" * 75)
    print(f"{'PAR':<12} | {'PREÇO ATUAL':<14} | {'VAR 24H':<8} | {'OSCILAÇÃO DO DIA':<18} | {'MÍNIMO'}")
    print("-" * 75)
    
    for r in resultados:
        moeda_sinal = "R$" if "BRL" in r['simbolo'] else "$"
        var_sinal = f"+{r['variacao']:.2f}%" if r['variacao'] >= 0 else f"{r['variacao']:.2f}%"
        print(f"{r['simbolo']:<12} | {moeda_sinal} {r['preco']:<11.2f} | {var_sinal:<8} | {r['oscilacao']:.2f}% de espaço     | {r['min']}")
        
    print("-" * 75)
    print("\n💡 O QUE ESSES NÚMEROS SIGNIFICAM PARA O SEU ROBÔ?")
    print("1. Veja a coluna 'OSCILAÇÃO DO DIA': ela mostra o quanto o preço subiu e desceu nas últimas 24h.")
    print("2. Se a Solana oscilou 6.5%, um robô de Grid no Spot teria comprado na baixa e vendido na alta várias vezes.")
    print("3. Você não precisava acertar vela de 30 segundos! O robô só executa a venda QUANDO O LUCRO ESTÁ GARANTIDO.")
    print("4. E com apenas R$ 10,00 ou $5 dólares por ordem, você já pode colocar ordens no mercado real.")

if __name__ == '__main__':
    if testar_conexao():
        escanear_melhores_pares_spot()
