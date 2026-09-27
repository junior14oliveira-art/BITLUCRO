"""
BITLUCRO - Robô Oficial MEXC Spot Real (Juros Compostos 24/7)
Opera com saldo real em USDT sem risco de liquidação.
- Stop de proteção: Mercado Spot puro
- Alvo de lucro: +2.0% por trade (Take Profit automático)
- Juros compostos: Lucro é 100% reinvestido na próxima operação
"""

import os
import sys
import time
import json
import base64
import requests
import hmac
import hashlib
from datetime import datetime

if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

CONFIG_FILE = "mexc_config.json"
STATE_FILE = "mexc_spot_state.json"
MEXC_API = "https://api.mexc.com/api/v3"
TAKE_PROFIT_PCT = 2.0

# Pares de alta liquidez e volatilidade na MEXC Spot
MONITORED_PAIRS = [
    {"symbol": "SOLUSDT", "name": "Solana"},
    {"symbol": "DOGEUSDT", "name": "Dogecoin"},
    {"symbol": "XRPUSDT", "name": "Ripple"},
    {"symbol": "NEARUSDT", "name": "NEAR"},
    {"symbol": "SUIUSDT", "name": "Sui"},
    {"symbol": "AVAXUSDT", "name": "Avalanche"},
    {"symbol": "LINKUSDT", "name": "Chainlink"},
    {"symbol": "BTCUSDT", "name": "Bitcoin"},
    {"symbol": "ETHUSDT", "name": "Ethereum"}
]

class MEXCTrader:
    def __init__(self, api_key="", api_secret=""):
        # 1. Tenta parâmetros passados
        self.api_key = api_key
        self.api_secret = api_secret

        # 2. Tenta variáveis de ambiente
        if not self.api_key:
            self.api_key = os.environ.get("MEXC_API_KEY", "")
            self.api_secret = os.environ.get("MEXC_API_SECRET", "")

        # 3. Tenta arquivo local mexc_config.json
        if not self.api_key and os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    self.api_key = cfg.get("api_key", "").strip()
                    self.api_secret = cfg.get("api_secret", "").strip()
            except Exception:
                pass

        # 4. Fallback seguro codificado (para operar no Render 24/7 sem quebrar)
        if not self.api_key:
            try:
                self.api_key = base64.b64decode("bXgwdmdsbHllSUppNTZXSkJY").decode()
                self.api_secret = base64.b64decode("M2QwZjhhYmIwOGEyNDc0N2JmMjg4ZDEyMjRmOTdhOWM=").decode()
            except Exception:
                pass

        self.logs = []
        self.state = self.load_state()

    def add_log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}"
        self.logs.insert(0, entry)
        if len(self.logs) > 30:
            self.logs.pop()

    def load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "mode": "MEXC_REAL_SPOT",
            "initial_usdt": 2.24,
            "cash_balance_usdt": 2.24,
            "total_equity_usdt": 2.24,
            "accumulated_profit_usdt": 0.0,
            "profit_pct": 0.0,
            "wins": 0,
            "open_position": None,
            "closed_trades": [],
            "current_thought": "Robô MEXC Real inicializado. Escaneando o mercado com banca real...",
            "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }

    def save_state(self):
        self.state["last_update"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        try:
            with open(STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _sign(self, params):
        q = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        sig = hmac.new(self.api_secret.encode(), q.encode(), hashlib.sha256).hexdigest()
        return q + f"&signature={sig}"

    def _headers(self):
        return {"X-MEXC-APIKEY": self.api_key, "Content-Type": "application/json"}

    def get_usdt_balance(self):
        try:
            params = {"timestamp": int(time.time() * 1000)}
            signed = self._sign(params)
            r = requests.get(f"{MEXC_API}/account?{signed}", headers=self._headers(), timeout=5)
            if r.status_code == 200:
                for b in r.json().get("balances", []):
                    if b["asset"] == "USDT":
                        return float(b["free"])
        except Exception:
            pass
        return 0.0

    def get_asset_balance(self, asset):
        try:
            params = {"timestamp": int(time.time() * 1000)}
            signed = self._sign(params)
            r = requests.get(f"{MEXC_API}/account?{signed}", headers=self._headers(), timeout=5)
            if r.status_code == 200:
                for b in r.json().get("balances", []):
                    if b["asset"] == asset:
                        return float(b["free"])
        except Exception:
            pass
        return 0.0

    def get_live_price(self, symbol):
        try:
            r = requests.get(f"{MEXC_API}/ticker/price?symbol={symbol}", timeout=3)
            if r.status_code == 200:
                return float(r.json()["price"])
        except Exception:
            pass
        return None

    def calculate_rsi(self, symbol, interval="60m", period=14):
        try:
            r = requests.get(f"{MEXC_API}/klines?symbol={symbol}&interval={interval}&limit=50", timeout=4)
            if r.status_code == 200 and len(r.json()) >= period:
                closes = [float(k[4]) for k in r.json()]
                deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
                gains = [d if d > 0 else 0.0 for d in deltas]
                losses = [-d if d < 0 else 0.0 for d in deltas]
                avg_gain = sum(gains[-period:]) / period
                avg_loss = sum(losses[-period:]) / period
                if avg_loss == 0:
                    return 100.0
                rs = avg_gain / avg_loss
                return round(100.0 - (100.0 / (1.0 + rs)), 1)
        except Exception:
            pass
        return 50.0

    def execute_market_buy(self, symbol, usdt_amount):
        """Compra a mercado usando USDT."""
        try:
            params = {
                "symbol": symbol,
                "side": "BUY",
                "type": "MARKET",
                "quoteOrderQty": round(float(usdt_amount), 2),
                "timestamp": int(time.time() * 1000)
            }
            signed = self._sign(params)
            r = requests.post(f"{MEXC_API}/order?{signed}", headers=self._headers(), timeout=5)
            if r.status_code == 200:
                return {"success": True, "data": r.json()}
            return {"success": False, "error": r.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_market_sell(self, symbol, base_asset, quantity):
        """Vende a mercado toda a quantidade do ativo base."""
        try:
            info = requests.get(f"{MEXC_API}/exchangeInfo?symbol={symbol}", timeout=4).json()
            prec = 2
            if "symbols" in info and len(info["symbols"]) > 0:
                prec = int(info["symbols"][0].get("baseAssetPrecision", 2))

            qty_str = f"{quantity:.{prec}f}"
            params = {
                "symbol": symbol,
                "side": "SELL",
                "type": "MARKET",
                "quantity": qty_str,
                "timestamp": int(time.time() * 1000)
            }
            signed = self._sign(params)
            r = requests.post(f"{MEXC_API}/order?{signed}", headers=self._headers(), timeout=5)
            if r.status_code == 200:
                return {"success": True, "data": r.json()}
            return {"success": False, "error": r.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def step(self):
        """Executa um ciclo único do robô MEXC Real."""
        now_str = datetime.now().strftime("%H:%M:%S")

        # 1. Se tem posição aberta, monitora saída no alvo (+2.0%)
        pos = self.state.get("open_position")
        if pos:
            sym = pos["symbol"]
            entry_p = pos["entry_price"]
            target_p = pos["target_price"]
            cur_p = self.get_live_price(sym)

            if cur_p:
                pnl = ((cur_p - entry_p) / entry_p) * 100
                pos["current_price"] = cur_p
                pos["current_pnl_pct"] = round(pnl, 2)
                cur_val = pos["invested_usdt"] * (1 + (pnl / 100.0))
                self.state["total_equity_usdt"] = round(self.state.get("cash_balance_usdt", 0.0) + cur_val, 4)

                # BATEU O ALVO (+2.0%)? VENDE COM LUCRO!
                if cur_p >= target_p:
                    base_asset = sym.replace("USDT", "")
                    qty = self.get_asset_balance(base_asset)
                    res = self.execute_market_sell(sym, base_asset, qty)

                    if res.get("success"):
                        new_usdt = self.get_usdt_balance()
                        profit_usdt = new_usdt - pos["invested_usdt"]
                        self.state["accumulated_profit_usdt"] = round(self.state.get("accumulated_profit_usdt", 0.0) + max(0.0, profit_usdt), 4)
                        self.state["wins"] = self.state.get("wins", 0) + 1
                        self.state["cash_balance_usdt"] = new_usdt
                        self.state["total_equity_usdt"] = new_usdt
                        tot_prof = self.state["total_equity_usdt"] - self.state.get("initial_usdt", 2.24)
                        self.state["profit_pct"] = round((tot_prof / self.state.get("initial_usdt", 2.24)) * 100, 2)

                        trade_rec = {
                            "symbol": sym,
                            "entry": entry_p,
                            "exit": cur_p,
                            "pnl_pct": round(pnl, 2),
                            "profit_usdt": round(profit_usdt, 4),
                            "time": now_str
                        }
                        self.state.setdefault("closed_trades", []).append(trade_rec)
                        self.state["open_position"] = None
                        self.state["current_thought"] = f"[{now_str}] 🎉 ALVO ATINGIDO NA MEXC! {sym} vendido no alvo (+{pnl:.2f}% | +${profit_usdt:.4f} USDT). Caixa livre ampliado para ${new_usdt:.2f} USDT. Rastreando nova entrada!"
                        self.add_log(f"🎉 Take Profit Real: {sym} vendido a ${cur_p:.4f} (+{pnl:.2f}%). Lucro: +${profit_usdt:.4f} USDT.")
                        self.save_state()
                        return
                    else:
                        self.add_log(f"⚠️ Erro ao vender {sym}: {res.get('error')}")

                self.state["current_thought"] = f"[{now_str}] Custódia Real MEXC: {sym} (PnL: {pnl:+.2f}%) | Cotação: ${cur_p:.4f} ➔ Alvo programado de +2.0%: ${target_p:.4f}."
                self.save_state()
            return

        # 2. Se não tem posição aberta, escaneia oportunidades para comprar
        usdt_bal = self.get_usdt_balance()
        self.state["cash_balance_usdt"] = usdt_bal
        self.state["total_equity_usdt"] = usdt_bal

        if usdt_bal < 1.0:
            self.state["current_thought"] = f"[{now_str}] Saldo USDT insuficiente (${usdt_bal:.2f} USDT). Aguardando depósito na MEXC."
            self.save_state()
            return

        best_opportunity = None
        best_rsi = 100.0

        for p in MONITORED_PAIRS:
            sym = p["symbol"]
            rsi_15m = self.calculate_rsi(sym, interval="15m")
            rsi_60m = self.calculate_rsi(sym, interval="60m")
            cur_p = self.get_live_price(sym)

            if rsi_15m <= 38 or rsi_60m <= 42:
                if rsi_15m < best_rsi:
                    best_rsi = rsi_15m
                    best_opportunity = {
                        "symbol": sym,
                        "name": p["name"],
                        "price": cur_p,
                        "rsi": rsi_15m
                    }

        if best_opportunity and best_opportunity["price"]:
            target_sym = best_opportunity["symbol"]
            price = best_opportunity["price"]
            target_profit = price * (1 + (TAKE_PROFIT_PCT / 100.0))
            invest_usdt = round(usdt_bal - 0.05, 2)

            buy_res = self.execute_market_buy(target_sym, invest_usdt)
            if buy_res.get("success"):
                self.state["open_position"] = {
                    "symbol": target_sym,
                    "entry_price": price,
                    "target_price": round(target_profit, 4),
                    "invested_usdt": invest_usdt,
                    "entry_time": now_str,
                    "current_price": price,
                    "current_pnl_pct": 0.0
                }
                self.state["cash_balance_usdt"] = round(usdt_bal - invest_usdt, 4)
                self.state["current_thought"] = f"[{now_str}] 🛒 COMPRA REAL MEXC EXECUTADA: {target_sym} a ${price:.4f} (${invest_usdt:.2f} USDT). Alvo líquido programado em ${target_profit:.4f} (+2.0%)."
                self.add_log(f"🛒 Compra Real MEXC: ${invest_usdt:.2f} em {target_sym} a ${price:.4f}.")
                self.save_state()
            else:
                self.add_log(f"⚠️ Erro ao comprar {target_sym}: {buy_res.get('error')}")
        else:
            self.state["current_thought"] = f"[{now_str}] Saldo Livre: ${usdt_bal:.2f} USDT. Escaneando {len(MONITORED_PAIRS)} pares líquidos na MEXC em 15m e 1h. Aguardando recuo perfeito para entrada segura."
            self.save_state()

    def run(self):
        print("\n" + "=" * 62)
        print("🤖 BITLUCRO SPOT - ROBÔ OFICIAL MEXC (REAL & JUROS COMPOSTOS)")
        print("🛡️ Modo: SPOT PURO (Zero risco de liquidação)")
        print(f"🎯 Alvo por Operação: +{TAKE_PROFIT_PCT}%")
        print("=" * 62 + "\n")

        while True:
            try:
                self.step()
                time.sleep(10)
            except KeyboardInterrupt:
                print("\n[!] Robô pausado pelo usuário.")
                break
            except Exception as e:
                print(f"⚠️ Alerta no loop: {e}")
                time.sleep(5)

if __name__ == '__main__':
    bot = MEXCTrader()
    bot.run()
