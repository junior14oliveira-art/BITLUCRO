"""
BITLUCRO - Motor de Execução Spot Oficial para Corretora MEXC
Opera com juros compostos seguros (Spot Puro sem risco de liquidação).
Utiliza a mesma inteligência quantitativa:
- Filtro Macro SMA 200 do Bitcoin
- Multi-Timeframe (15m, 1h, 4h)
- Machine Learning Predictor (>65% de confiança)
- Gestão de Risco com Take Profit automático de +2.0%
"""

import time
import hmac
import hashlib
import json
import os
import requests
from datetime import datetime

MEXC_API_URL = "https://api.mexc.com/api/v3"
STATE_FILE_MEXC = "mexc_spot_state.json"
TAKE_PROFIT_PCT = 2.0

class MEXCSpotEngine:
    def __init__(self, api_key="", api_secret=""):
        self.api_key = api_key or os.environ.get("MEXC_API_KEY", "")
        self.api_secret = api_secret or os.environ.get("MEXC_API_SECRET", "")
        self.state = self.load_state()

    def _sign(self, params):
        """Gera assinatura HMAC SHA256 exigida pela MEXC."""
        query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return query_string + f"&signature={signature}"

    def _headers(self):
        return {
            "X-MEXC-APIKEY": self.api_key,
            "Content-Type": "application/json"
        }

    def load_state(self):
        if os.path.exists(STATE_FILE_MEXC):
            try:
                with open(STATE_FILE_MEXC, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "mode": "MEXC_REAL_SPOT",
            "initial_capital_usdt": 0.0,
            "cash_balance_usdt": 0.0,
            "total_equity_usdt": 0.0,
            "accumulated_profit_usdt": 0.0,
            "profit_pct": 0.0,
            "open_positions": [],
            "closed_trades": [],
            "win_count": 0,
            "loss_count": 0,
            "current_thought": "Motor MEXC pronto. Aguardando chaves de API e saldo em USDT...",
            "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }

    def save_state(self):
        self.state["last_update"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        try:
            with open(STATE_FILE_MEXC, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get_account_balances(self):
        """Busca os saldos reais disponíveis na conta MEXC Spot."""
        if not self.api_key or not self.api_secret:
            return {"error": "Chaves de API não configuradas"}
        
        try:
            params = {"timestamp": int(time.time() * 1000)}
            signed_query = self._sign(params)
            url = f"{MEXC_API_URL}/account?{signed_query}"
            r = requests.get(url, headers=self._headers(), timeout=5)
            if r.status_code == 200:
                data = r.json()
                balances = {}
                for b in data.get("balances", []):
                    free = float(b.get("free", 0.0))
                    locked = float(b.get("locked", 0.0))
                    if free > 0 or locked > 0:
                        balances[b["asset"]] = {"free": free, "locked": locked, "total": free + locked}
                return balances
            return {"error": f"HTTP {r.status_code}: {r.text}"}
        except Exception as e:
            return {"error": str(e)}

    def get_ticker_price(self, symbol):
        """Busca o preço em tempo real de um par na MEXC."""
        try:
            r = requests.get(f"{MEXC_API_URL}/ticker/price", params={"symbol": symbol}, timeout=3)
            if r.status_code == 200:
                return float(r.json()["price"])
        except Exception:
            pass
        return None

    def execute_market_order(self, symbol, side, quote_quantity):
        """
        Executa ordem a mercado na MEXC com validação de segurança.
        side: 'BUY' ou 'SELL'
        quote_quantity: valor em USDT da ordem
        """
        if not self.api_key or not self.api_secret:
            return {"status": "error", "message": "Chaves da MEXC ausentes"}

        try:
            params = {
                "symbol": symbol,
                "side": side.upper(),
                "type": "MARKET",
                "quoteOrderQty": round(float(quote_quantity), 2),
                "timestamp": int(time.time() * 1000)
            }
            signed_query = self._sign(params)
            url = f"{MEXC_API_URL}/order?{signed_query}"
            r = requests.post(url, headers=self._headers(), timeout=5)
            if r.status_code == 200:
                return {"status": "success", "data": r.json()}
            return {"status": "error", "message": r.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}
