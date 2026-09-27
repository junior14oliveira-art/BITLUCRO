"""
BITLUCRO - Scanner Dinâmico do Mercado Amplo da Binance
Analisa centenas de moedas negociadas na Binance em tempo real,
seleciona as mais líquidas e promissoras e fornece ao robô uma visão ampla do mercado.
"""

import requests
import json
import os
from datetime import datetime

BINANCE_API_URL = "https://api.binance.com/api/v3"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCANNER_CACHE_FILE = os.path.join(BASE_DIR, 'scanner_mercado_amplo.json')

class DynamicMarketScanner:
    def __init__(self):
        self.cached_pairs = []
        self.last_scan_time = None
        self.total_pairs_market = 0

    def scan_full_market(self, max_pairs=20):
        """
        Escaneia todos os tickers da Binance em 1 chamada rápida e filtra
        as melhores moedas por liquidez e volume financeiro.
        """
        try:
            res = requests.get(f"{BINANCE_API_URL}/ticker/24hr", timeout=6).json()
            if not isinstance(res, list):
                return self.get_fallback_pairs()

            self.total_pairs_market = len(res)

            # Filtra pares em BRL e USDT (exclui stablecoins puras como USDC, FDUSD, USD1, etc.)
            excluded_stablecoins = [
                "USDCUSDT", "FDUSDUSDT", "TUSDUSDT", "USDPUSDT", "EURIUSDT", 
                "EURUSDT", "USDCBRL", "BUSDUSDT", "USD1USDT", "USDTEUR", 
                "USDTDAI", "DAIUSDT", "AEURUSDT", "USDEUSDT", "WBTCBTC", "USTCUSDT"
            ]

            candidates = []
            for item in res:
                sym = item["symbol"]
                if sym in excluded_stablecoins:
                    continue

                is_brl = sym.endswith("BRL") and sym != "USDTBRL"
                is_usdt = sym.endswith("USDT")

                if is_brl or is_usdt:
                    quote_vol = float(item["quoteVolume"])
                    # Filtra apenas moedas com liquidez real comprovada
                    min_vol = 300000 if is_brl else 5000000 # R$ 300k em BRL ou $ 5M em USDT
                    if quote_vol >= min_vol:
                        candidates.append({
                            "symbol": sym,
                            "name": sym.replace("BRL", " (BRL)").replace("USDT", " (USDT)"),
                            "quote": "BRL" if is_brl else "USDT",
                            "price": float(item["lastPrice"]),
                            "change_24h_pct": float(item["priceChangePercent"]),
                            "volume_quote": quote_vol
                        })

            # Ordena por volume de negociação (as moedas mais vivas e líquidas do mercado)
            candidates.sort(key=lambda x: x["volume_quote"], reverse=True)

            # Seleciona o Top Moedas diversificado
            selected = candidates[:max_pairs]
            self.cached_pairs = selected
            self.last_scan_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            # Salva cache
            try:
                with open(SCANNER_CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump({
                        "total_pairs_market": self.total_pairs_market,
                        "selected_count": len(selected),
                        "last_scan_time": self.last_scan_time,
                        "pairs": selected
                    }, f, indent=2, ensure_ascii=False)
            except Exception:
                pass

            return selected

        except Exception as e:
            print(f"[!] Erro no scanner amplo: {e}")
            return self.get_fallback_pairs()

    def get_fallback_pairs(self):
        return [
            {"symbol": "SOLBRL", "name": "Solana (BRL)", "quote": "BRL"},
            {"symbol": "BTCBRL", "name": "Bitcoin (BRL)", "quote": "BRL"},
            {"symbol": "ETHBRL", "name": "Ethereum (BRL)", "quote": "BRL"},
            {"symbol": "NEARUSDT", "name": "NEAR Protocol (USDT)", "quote": "USDT"},
            {"symbol": "RENDERUSDT", "name": "Render IA (USDT)", "quote": "USDT"},
            {"symbol": "SUIUSDT", "name": "SUI Network (USDT)", "quote": "USDT"},
            {"symbol": "AVAXUSDT", "name": "Avalanche (USDT)", "quote": "USDT"},
            {"symbol": "LINKUSDT", "name": "Chainlink (USDT)", "quote": "USDT"}
        ]
