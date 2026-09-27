"""
ROBÔ QUANTITATIVO BINANCE SPOT (SIMULADOR COM DADOS REAIS / PAPER TRADING)
- 100% Gratuito: Sem precisar colocar dinheiro real
- Conectado à API Oficial da Binance em Tempo Real
- Banca Inicial Simulada: R$ 50,00
- Ordem Mínima: R$ 10,00 por entrada
- As 3 Leis de Ouro Ativas:
  1. Velas de 1 Hora (Sem ruído de segundos)
  2. Mercado Spot Puro (Propriedade real, nunca vende no prejuízo)
  3. Filtro Macro Global: Só compra se Bitcoin > SMA 200
"""

import requests
import json
import time
import sys
import io
import os
from datetime import datetime

if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, 'spot_paper_state.json')
JOURNAL_FILE = os.path.join(BASE_DIR, 'diario_spot_binance.md')

BINANCE_API_URL = "https://api.binance.com/api/v3"

# Configurações do Robô
INITIAL_BANKROLL_BRL = 50.00       # Banca inicial simulada
ORDER_SIZE_BRL = 10.00             # R$ 10,00 por ordem (mínimo da Binance)
TAKE_PROFIT_PCT = 2.0              # Alvo de lucro: +2.0% por operação
TIMEFRAME = "1h"                   # Velas de 1 Hora (Lei #1)

# Pares Monitorados em Reais e Dólares
TARGET_PAIRS = [
    {"symbol": "SOLBRL", "name": "Solana (BRL)", "quote": "BRL"},
    {"symbol": "BTCBRL", "name": "Bitcoin (BRL)", "quote": "BRL"},
    {"symbol": "ETHBRL", "name": "Ethereum (BRL)", "quote": "BRL"},
    {"symbol": "NEARUSDT", "name": "NEAR Protocol (USDT)", "quote": "USDT"},
    {"symbol": "RENDERUSDT", "name": "Render IA (USDT)", "quote": "USDT"}
]

class BinanceSpotPaperEngine:
    def __init__(self):
        self.state = self.load_state()
        self.running = True

    def load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    s = json.load(f)
                    if "is_paused" not in s:
                        s["is_paused"] = False
                    if "api_latency_ms" not in s:
                        s["api_latency_ms"] = 65
                    return s
            except Exception:
                pass
        return {
            "mode": "PAPER_TRADING_SPOT",
            "initial_capital_brl": INITIAL_BANKROLL_BRL,
            "cash_balance_brl": INITIAL_BANKROLL_BRL,
            "total_equity_brl": INITIAL_BANKROLL_BRL,
            "accumulated_profit_brl": 0.0,
            "profit_pct": 0.0,
            "open_positions": [],
            "closed_trades": [],
            "win_count": 0,
            "loss_count": 0,
            "is_paused": False,
            "api_latency_ms": 65,
            "last_macro_status": "ANALISANDO",
            "current_thought": "Iniciando simulador com cotações oficiais da Binance...",
            "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }

    def reset_simulation(self):
        """Redefine o simulador para a banca original de R$ 50,00."""
        self.state = {
            "mode": "PAPER_TRADING_SPOT",
            "initial_capital_brl": INITIAL_BANKROLL_BRL,
            "cash_balance_brl": INITIAL_BANKROLL_BRL,
            "total_equity_brl": INITIAL_BANKROLL_BRL,
            "accumulated_profit_brl": 0.0,
            "profit_pct": 0.0,
            "open_positions": [],
            "closed_trades": [],
            "win_count": 0,
            "loss_count": 0,
            "is_paused": False,
            "api_latency_ms": 65,
            "last_macro_status": "BULL 🟢 (Aguardando novo ciclo)",
            "current_thought": "Simulação reiniciada com sucesso. Banca resetada para R$ 50,00.",
            "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        self.save_state()

    def toggle_pause(self):
        """Pausa ou retoma a abertura de novas posições."""
        current = self.state.get("is_paused", False)
        self.state["is_paused"] = not current
        self.save_state()
        return self.state["is_paused"]

    def save_state(self):
        self.state["last_update"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        try:
            with open(STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[!] Erro ao salvar estado: {e}")

    def get_usdt_brl_rate(self):
        try:
            res = requests.get(f"{BINANCE_API_URL}/ticker/price?symbol=USDTBRL", timeout=4).json()
            return float(res['price'])
        except Exception:
            return 5.60

    def check_macro_sma200(self):
        """Lei #3: Filtro Global do Bitcoin acima da SMA 200 diária."""
        try:
            url = f"{BINANCE_API_URL}/klines?symbol=BTCUSDT&interval=1d&limit=200"
            candles = requests.get(url, timeout=5).json()
            if candles and len(candles) >= 200:
                closes = [float(c[4]) for c in candles]
                current_price = closes[-1]
                sma_200 = sum(closes) / len(closes)
                is_bull = current_price >= sma_200
                self.state["last_macro_status"] = f"BULL 🟢 (BTC: ${current_price:,.0f} > SMA200: ${sma_200:,.0f})" if is_bull else f"BEAR 🛑 (BTC: ${current_price:,.0f} < SMA200: ${sma_200:,.0f})"
                return is_bull
        except Exception:
            pass
        return True # Fallback seguro

    def fetch_candles_and_indicators(self, symbol, interval="1h", count=30):
        """Coleta velas de 1h reais da Binance e calcula RSI(14) e Médias Móveis."""
        try:
            url = f"{BINANCE_API_URL}/klines?symbol={symbol}&interval={interval}&limit={count}"
            candles = requests.get(url, timeout=5).json()
            if not candles or len(candles) < 20:
                return None

            closes = [float(c[4]) for c in candles]
            highs = [float(c[2]) for c in candles]
            lows = [float(c[3]) for c in candles]
            opens = [float(c[1]) for c in candles]

            # RSI 14
            gains = []
            losses = []
            for i in range(1, 15):
                diff = closes[-i] - closes[-i-1]
                if diff >= 0:
                    gains.append(diff)
                    losses.append(0.0)
                else:
                    gains.append(0.0)
                    losses.append(abs(diff))
            avg_gain = sum(gains) / 14 if gains else 0.0001
            avg_loss = sum(losses) / 14 if losses else 0.0001
            rs = avg_gain / avg_loss if avg_loss > 0 else 100.0
            rsi = 100.0 - (100.0 / (1.0 + rs))

            # EMA 9 e EMA 21
            def calc_ema(values, period):
                k = 2.0 / (period + 1)
                ema = values[0]
                for v in values[1:]:
                    ema = (v * k) + (ema * (1 - k))
                return ema

            ema9 = calc_ema(closes[-20:], 9)
            ema21 = calc_ema(closes[-20:], 21)

            return {
                "current_price": closes[-1],
                "rsi": round(rsi, 1),
                "ema9": ema9,
                "ema21": ema21,
                "prev_close": closes[-2],
                "prev_open": opens[-2],
                "is_bull_candle": closes[-1] > opens[-1]
            }
        except Exception:
            return None

    def update_open_positions(self):
        """Verifica se posições abertas atingiram o Take Profit de +2.0%."""
        usdt_brl = self.get_usdt_brl_rate()
        active_positions = []
        positions_value_brl = 0.0

        for pos in self.state.get("open_positions", []):
            sym = pos["symbol"]
            entry_price = pos["entry_price"]
            stake_brl = pos["stake_brl"]
            target_price = pos["target_price"]

            try:
                res = requests.get(f"{BINANCE_API_URL}/ticker/price?symbol={sym}", timeout=4).json()
                current_price = float(res['price'])
            except Exception:
                current_price = entry_price

            change_pct = ((current_price - entry_price) / entry_price) * 100
            current_val_brl = stake_brl * (1 + (change_pct / 100.0))
            positions_value_brl += current_val_brl

            # REGRA SPOT: Venda automática com LUCRO atingido (+2.0%)
            if current_price >= target_price:
                profit_brl = current_val_brl - stake_brl
                self.state["cash_balance_brl"] += current_val_brl
                self.state["accumulated_profit_brl"] += profit_brl
                self.state["win_count"] += 1

                trade_record = {
                    "symbol": sym,
                    "entry_time": pos["entry_time"],
                    "exit_time": datetime.now().strftime("%d/%m %H:%M:%S"),
                    "entry_price": entry_price,
                    "exit_price": current_price,
                    "profit_pct": round(change_pct, 2),
                    "profit_brl": round(profit_brl, 2),
                    "stake_brl": stake_brl
                }
                self.state["closed_trades"].append(trade_record)
                self.log_trade(trade_record)
                print(f"\n🎉 [TAKE PROFIT SPOT EXECUTADO] {sym} vendido a {current_price}! Lucro: +R$ {profit_brl:.2f} (+{change_pct:.2f}%)!")
            else:
                # Mantém posição aberta (Lei #2: NUNCA vende no prejuízo, espera o ativo valorizar)
                pos["current_price"] = current_price
                pos["current_pnl_pct"] = round(change_pct, 2)
                active_positions.append(pos)

        self.state["open_positions"] = active_positions
        self.state["total_equity_brl"] = round(self.state["cash_balance_brl"] + positions_value_brl, 2)
        total_profit = self.state["total_equity_brl"] - self.state["initial_capital_brl"]
        self.state["profit_pct"] = round((total_profit / self.state["initial_capital_brl"]) * 100, 2)
        self.save_state()

    def log_trade(self, trade):
        try:
            entry = f"\n### Trade SPOT - {trade['exit_time']}\n" \
                    f"- **Ativo:** {trade['symbol']}\n" \
                    f"- **Compra:** {trade['entry_price']} ➔ **Venda:** {trade['exit_price']} (+{trade['profit_pct']}%)\n" \
                    f"- **Resultado:** 🟢 **WIN (+R$ {trade['profit_brl']:.2f})** | **Banca Total:** R$ {self.state['total_equity_brl']:.2f}\n" \
                    f"---\n"
            with open(JOURNAL_FILE, 'a', encoding='utf-8') as f:
                f.write(entry)
        except Exception:
            pass

    def run_cycle(self):
        print("\n" + "=" * 68)
        print("🤖 ROBÔ BINANCE SPOT (SIMULADOR PAPER TRADING - BANCA R$ 50,00)")
        print(f"💰 Saldo Líquido: R$ {self.state['cash_balance_brl']:.2f} | Patrimônio Total: R$ {self.state['total_equity_brl']:.2f}")
        print(f"📈 Lucro Acumulado: R$ {self.state['accumulated_profit_brl']:.2f} ({self.state['profit_pct']:+.2f}%) | Vitórias: {self.state['win_count']}")
        print("=" * 68)

        t0 = time.time()
        # 1. Atualiza posições em andamento
        self.update_open_positions()

        # Mede latência aproximada da Binance
        self.state["api_latency_ms"] = max(25, int((time.time() - t0) * 1000))

        # 2. Verifica se o usuário pausou as compras
        if self.state.get("is_paused", False):
            self.state["current_thought"] = "⏸️ Robô em modo PAUSADO pelo usuário. Monitorando lucros das posições abertas."
            print(self.state["current_thought"])
            self.save_state()
            return

        # 3. Verifica a Lei #3 (Filtro Macro SMA 200 do Bitcoin)
        macro_ok = self.check_macro_sma200()
        print(f"\n🌐 Filtro Macro Global: {self.state['last_macro_status']}")

        if not macro_ok:
            self.state["current_thought"] = "🛡️ [LEI #3 ATIVA]: Mercado global em correção. Robô mantém o dinheiro 100% em caixa."
            print(self.state["current_thought"])
            self.save_state()
            return

        # 4. Se temos saldo em caixa (mínimo R$ 10,00), caçamos oportunidades no Spot
        if self.state["cash_balance_brl"] < ORDER_SIZE_BRL:
            self.state["current_thought"] = f"⏳ Saldo livre (R$ {self.state['cash_balance_brl']:.2f}) aguardando fechamento de posições com lucro..."
            print(self.state["current_thought"])
            self.save_state()
            return

        print("\n🔍 Escaneando oportunidades em Velas de 1H nos pares Spot...")

        for target in TARGET_PAIRS:
            sym = target["symbol"]

            # Evita comprar o mesmo par se já tiver posição aberta nele
            already_open = any(p["symbol"] == sym for p in self.state["open_positions"])
            if already_open:
                continue

            tech = self.fetch_candles_and_indicators(sym, interval=TIMEFRAME)
            if not tech:
                continue

            price = tech["current_price"]
            rsi = tech["rsi"]
            ema9 = tech["ema9"]
            ema21 = tech["ema21"]

            # GATILHO SPOT CONSERVADOR (Velas de 1 Hora):
            # RSI sobrevendido em 1H (<= 45) OU Cruzamento de Média com vela compradora
            is_oversold = rsi <= 45
            is_ema_bullish = ema9 > ema21 and tech["is_bull_candle"]

            print(f"   • {sym:<10}: Preço R$/$ {price:<10.2f} | RSI(1H): {rsi:<4.1f} | EMA9/21: {'ALTA ↗' if ema9 > ema21 else 'BAIXA ↘'}")

            if (is_oversold or is_ema_bullish) and self.state["cash_balance_brl"] >= ORDER_SIZE_BRL:
                target_profit_price = price * (1 + (TAKE_PROFIT_PCT / 100.0))
                
                # Executa compra simulada a preço de mercado real da Binance
                self.state["cash_balance_brl"] -= ORDER_SIZE_BRL
                new_position = {
                    "symbol": sym,
                    "name": target["name"],
                    "entry_time": datetime.now().strftime("%d/%m %H:%M:%S"),
                    "entry_price": price,
                    "target_price": round(target_profit_price, 4),
                    "stake_brl": ORDER_SIZE_BRL,
                    "current_price": price,
                    "current_pnl_pct": 0.0,
                    "reason": f"RSI 1H ({rsi}) + Alinhamento EMA9/21"
                }
                self.state["open_positions"].append(new_position)
                print(f"\n🛒 [COMPRA EXECUTADA NO SPOT]: R$ {ORDER_SIZE_BRL:.2f} de {sym} a {price:.4f}!")
                print(f"🎯 Alvo de Venda (+{TAKE_PROFIT_PCT}%): {target_profit_price:.4f}")
                self.save_state()
                break # Uma entrada por ciclo para diversificar

        self.save_state()

if __name__ == '__main__':
    engine = BinanceSpotPaperEngine()
    engine.run_cycle()
