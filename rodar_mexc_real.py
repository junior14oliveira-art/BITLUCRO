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
import requests
import hmac
import hashlib
from datetime import datetime

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
    def __init__(self):
        if not os.path.exists(CONFIG_FILE):
            print("❌ Erro: Arquivo mexc_config.json não encontrado.")
            sys.exit(1)
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            self.api_key = cfg.get("api_key", "").strip()
            self.api_secret = cfg.get("api_secret", "").strip()
        
        self.state = self.load_state()

    def load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "initial_usdt": 2.24,
            "accumulated_profit_usdt": 0.0,
            "wins": 0,
            "open_position": None,
            "closed_trades": []
        }

    def save_state(self):
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
            # Obtém a precisão de lote da MEXC
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

    def run(self):
        print("\n" + "=" * 62)
        print("🤖 BITLUCRO SPOT - ROBÔ OFICIAL MEXC (REAL & JUROS COMPOSTOS)")
        print("🛡️ Modo: SPOT PURO (Zero risco de liquidação)")
        print(f"🎯 Alvo por Operação: +{TAKE_PROFIT_PCT}%")
        print("=" * 62 + "\n")

        usdt_bal = self.get_usdt_balance()
        print(f"💵 Saldo Livre na MEXC: {usdt_bal:.4f} USDT (≈ R$ {usdt_bal * 5.70:.2f})")

        while True:
            try:
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
                        print(f"[{now_str}] 📈 {sym} | Cotação: ${cur_p:.4f} | Entrada: ${entry_p:.4f} | PnL: {pnl:+.2f}% | Alvo: ${target_p:.4f} (+{TAKE_PROFIT_PCT}%)", end='\r')

                        # BATEU O ALVO (+2.0%)? VENDE COM LUCRO!
                        if cur_p >= target_p:
                            print(f"\n\n🎉 [{now_str}] ALVO ATINGIDO (+{pnl:.2f}%)! Vendendo {sym} a mercado...")
                            base_asset = sym.replace("USDT", "")
                            qty = self.get_asset_balance(base_asset)
                            res = self.execute_market_sell(sym, base_asset, qty)

                            if res.get("success"):
                                new_usdt = self.get_usdt_balance()
                                profit_usdt = new_usdt - pos["invested_usdt"]
                                self.state["accumulated_profit_usdt"] += max(0.0, profit_usdt)
                                self.state["wins"] += 1
                                self.state["closed_trades"].append({
                                    "symbol": sym,
                                    "entry": entry_p,
                                    "exit": cur_p,
                                    "pnl_pct": round(pnl, 2),
                                    "profit_usdt": round(profit_usdt, 4),
                                    "time": now_str
                                })
                                self.state["open_position"] = None
                                self.save_state()
                                print(f"✅ Venda executada com sucesso! Lucro no bolso: +{profit_usdt:.4f} USDT!")
                                print(f"💰 Novo Saldo Disponível para Reinvestir: {new_usdt:.4f} USDT\n")
                            else:
                                print(f"⚠️ Erro ao enviar ordem de venda: {res.get('error')}")

                    time.sleep(3)
                    continue

                # 2. Se não tem posição aberta, escaneia oportunidades para comprar
                usdt_bal = self.get_usdt_balance()
                if usdt_bal < 1.0:
                    print(f"[{now_str}] Saldo USDT insuficiente ({usdt_bal:.2f} USDT). Aguardando depósito...", end='\r')
                    time.sleep(10)
                    continue

                print(f"[{now_str}] 🔍 Escaneando {len(MONITORED_PAIRS)} pares na MEXC (Saldo: {usdt_bal:.2f} USDT)...")
                best_opportunity = None
                best_rsi = 100.0

                for p in MONITORED_PAIRS:
                    sym = p["symbol"]
                    rsi_15m = self.calculate_rsi(sym, interval="15m")
                    rsi_60m = self.calculate_rsi(sym, interval="60m")
                    cur_p = self.get_live_price(sym)

                    # Gatilho de Pullback Saudável (RSI em suporte de 15m/1h)
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
                    invest_usdt = round(usdt_bal - 0.05, 2) # Reserva pequena para taxas

                    print(f"\n⚡ OPORTUNIDADE DETECTADA: {target_sym} (RSI: {best_opportunity['rsi']}) a ${price:.4f}")
                    print(f"🛒 Executando compra de {invest_usdt:.2f} USDT no par {target_sym}...")

                    buy_res = self.execute_market_buy(target_sym, invest_usdt)
                    if buy_res.get("success"):
                        self.state["open_position"] = {
                            "symbol": target_sym,
                            "entry_price": price,
                            "target_price": round(target_profit, 4),
                            "invested_usdt": invest_usdt,
                            "entry_time": now_str
                        }
                        self.save_state()
                        print(f"✅ COMPRA EXECUTADA! Alvo de Venda (+{TAKE_PROFIT_PCT}%): ${target_profit:.4f}\n")
                    else:
                        print(f"⚠️ Erro na compra: {buy_res.get('error')}\n")

                time.sleep(25)

            except KeyboardInterrupt:
                print("\n[!] Robô pausado pelo usuário.")
                break
            except Exception as e:
                print(f"⚠️ Alerta no loop: {e}")
                time.sleep(5)

if __name__ == '__main__':
    bot = MEXCTrader()
    bot.run()
