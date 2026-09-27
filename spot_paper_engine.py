"""
ROBÔ QUANTITATIVO BINANCE SPOT (SIMULADOR PAPER TRADING ULTRA-REALISTA)
- 100% Gratuito: Cotações oficiais da Binance em tempo real
- Simulação Fiel com Taxas Oficiais da Binance (0.10% Maker/Taker + 0.05% Slippage)
- Motor Multi-Timeframe Ativo: 15M (Scalp Dips), 1H (Swing) e 4H (Macro Estrutura)
- Contingência Ampla de IA: Google Gemini -> Groq AI -> Motor Quantitativo Local (24/7)
- Banca Inicial Simulada: R$ 50,00 | Ordem Mínima: R$ 10,00
"""

import requests
import json
import time
import sys
import os
from datetime import datetime

# Configuração de encoding para UTF-8 seguro
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

from super_skill_brain import SuperSkillBrain
from risk_manager import RiskManager
from historical_market_analyzer import HistoricalMarketAnalyzer
from ai_market_study_contingency import AIMarketStudyContingency
from dynamic_market_scanner import DynamicMarketScanner
from ml_quant_predictor import MLQuantPredictor

BINANCE_API_URL = "https://api.binance.com/api/v3"

# Configurações do Simulador e Taxas Reais da Binance
INITIAL_BANKROLL_BRL = 50.00       # Banca inicial simulada
ORDER_SIZE_BRL = 10.00             # R$ 10,00 por ordem (mínimo da Binance)
TAKE_PROFIT_PCT = 2.0              # Alvo de lucro: +2.0% por operação

# Custos Reais da Corretora (Binance Spot)
BINANCE_FEE_PCT = 0.10             # Taxa padrão Spot Maker/Taker Binance (0.10%)
SIMULATED_SLIPPAGE_PCT = 0.05      # Deslizamento médio de execução de book (0.05%)
TOTAL_ORDER_COST_PCT = BINANCE_FEE_PCT + SIMULATED_SLIPPAGE_PCT # 0.15% por ponta

# Pares Base Monitorados
TARGET_PAIRS = [
    {"symbol": "SOLBRL", "name": "Solana (BRL)", "quote": "BRL"},
    {"symbol": "BTCBRL", "name": "Bitcoin (BRL)", "quote": "BRL"},
    {"symbol": "ETHBRL", "name": "Ethereum (BRL)", "quote": "BRL"},
    {"symbol": "NEARUSDT", "name": "NEAR Protocol (USDT)", "quote": "USDT"},
    {"symbol": "RENDERUSDT", "name": "Render IA (USDT)", "quote": "USDT"}
]

class BinanceSpotPaperEngine:
    def __init__(self):
        self.brain = SuperSkillBrain()
        self.risk_manager = RiskManager(initial_capital=INITIAL_BANKROLL_BRL)
        self.historical_analyzer = HistoricalMarketAnalyzer(TARGET_PAIRS)
        self.ai_contingency = AIMarketStudyContingency()
        self.market_scanner = DynamicMarketScanner()
        self.ml_predictor = MLQuantPredictor(target_profit_pct=TAKE_PROFIT_PCT, min_confidence_threshold=0.65)
        self.state = self.load_state()
        self.state["super_skill"] = self.brain.state
        self.running = True

    def load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    s = json.load(f)
                    if "total_fees_paid_brl" not in s:
                        s["total_fees_paid_brl"] = 0.0
                    if "gross_profit_brl" not in s:
                        s["gross_profit_brl"] = 0.0
                    if "active_ai_provider" not in s:
                        s["active_ai_provider"] = "Motor Quantitativo Local (Zero Downtime)"
                    if "detailed_logs" not in s:
                        s["detailed_logs"] = []
                    return s
            except Exception:
                pass
        return {
            "mode": "PAPER_TRADING_SPOT",
            "initial_capital_brl": INITIAL_BANKROLL_BRL,
            "cash_balance_brl": INITIAL_BANKROLL_BRL,
            "total_equity_brl": INITIAL_BANKROLL_BRL,
            "accumulated_profit_brl": 0.0,
            "gross_profit_brl": 0.0,
            "total_fees_paid_brl": 0.0,
            "profit_pct": 0.0,
            "open_positions": [],
            "closed_trades": [],
            "win_count": 0,
            "loss_count": 0,
            "is_paused": False,
            "api_latency_ms": 65,
            "last_macro_status": "ANALISANDO",
            "active_ai_provider": "Motor Quantitativo Local (Zero Downtime)",
            "current_thought": "Iniciando simulador com cotações oficiais e taxas reais da Binance...",
            "detailed_logs": [],
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
            "gross_profit_brl": 0.0,
            "total_fees_paid_brl": 0.0,
            "profit_pct": 0.0,
            "open_positions": [],
            "closed_trades": [],
            "win_count": 0,
            "loss_count": 0,
            "is_paused": False,
            "api_latency_ms": 65,
            "last_macro_status": "BULL 🟢 (Aguardando novo ciclo)",
            "active_ai_provider": "Motor Quantitativo Local (Zero Downtime)",
            "current_thought": "Simulação reiniciada com sucesso. Banca restaurada para R$ 50,00.",
            "detailed_logs": [],
            "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        self.save_state()

    def toggle_pause(self):
        current = self.state.get("is_paused", False)
        self.state["is_paused"] = not current
        self.save_state()
        return self.state["is_paused"]

    def add_detailed_log(self, log_type, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = {"time": ts, "type": log_type, "msg": msg}
        logs = self.state.get("detailed_logs", [])
        logs.insert(0, entry)
        if len(logs) > 50:
            logs.pop()
        self.state["detailed_logs"] = logs

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
        return True

    def fetch_candles_and_indicators(self, symbol, interval="1h", count=30):
        """Coleta velas reais da Binance e calcula RSI(14) e Médias Móveis."""
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
            gains, losses = [], []
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
                "is_bull_candle": closes[-1] > opens[-1]
            }
        except Exception:
            return None

    def update_open_positions(self):
        """
        Verifica se posições abertas atingiram o Take Profit de +2.0%.
        Desconta as taxas oficiais da Binance (0.10%) e slippage (0.05%) para fidelidade total!
        """
        active_positions = []
        positions_value_brl = 0.0

        for pos in self.state.get("open_positions", []):
            sym = pos["symbol"]
            entry_price = pos["entry_price"]
            stake_brl = pos["stake_brl"]
            target_price = pos["target_price"]
            buy_fee_brl = pos.get("buy_fee_brl", stake_brl * (TOTAL_ORDER_COST_PCT / 100.0))

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
                gross_profit_brl = current_val_brl - stake_brl
                sell_fee_brl = current_val_brl * (TOTAL_ORDER_COST_PCT / 100.0)
                total_trade_fees = buy_fee_brl + sell_fee_brl
                
                net_exit_val_brl = current_val_brl - sell_fee_brl
                net_profit_brl = net_exit_val_brl - stake_brl

                self.state["cash_balance_brl"] += net_exit_val_brl
                self.state["accumulated_profit_brl"] += net_profit_brl
                self.state["gross_profit_brl"] = round(self.state.get("gross_profit_brl", 0.0) + gross_profit_brl, 4)
                self.state["total_fees_paid_brl"] = round(self.state.get("total_fees_paid_brl", 0.0) + total_trade_fees, 4)
                self.state["win_count"] += 1

                trade_record = {
                    "symbol": sym,
                    "timeframe": pos.get("timeframe", "1H"),
                    "entry_time": pos["entry_time"],
                    "exit_time": datetime.now().strftime("%d/%m %H:%M:%S"),
                    "entry_price": entry_price,
                    "exit_price": current_price,
                    "gross_profit_brl": round(gross_profit_brl, 2),
                    "net_profit_brl": round(net_profit_brl, 2),
                    "profit_pct": round(change_pct, 2),
                    "fees_paid_brl": round(total_trade_fees, 4),
                    "stake_brl": stake_brl
                }
                self.state["closed_trades"].append(trade_record)
                self.log_trade(trade_record)
                self.add_detailed_log("TAKE_PROFIT", f"{sym} bateu alvo (+{change_pct:.2f}%)! Lucro Líquido Real: +R$ {net_profit_brl:.2f} (Taxa Binance: R$ {total_trade_fees:.3f}).")
                print(f"\n🎉 [TAKE PROFIT SPOT REAL] {sym} vendido! Lucro Líquido: +R$ {net_profit_brl:.2f} | Taxas Pagas: R$ {total_trade_fees:.3f}!")
            else:
                # Mantém em custódia (Mercado Spot puro: nunca vende no prejuízo)
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
            entry = f"\n### Trade SPOT ({trade.get('timeframe', '1H')}) - {trade['exit_time']}\n" \
                    f"- **Ativo:** {trade['symbol']}\n" \
                    f"- **Compra:** {trade['entry_price']} ➔ **Venda:** {trade['exit_price']} (+{trade['profit_pct']}%)\n" \
                    f"- **Lucro Líquido Real:** +R$ {trade['net_profit_brl']:.2f} (Taxas: R$ {trade['fees_paid_brl']:.3f})\n" \
                    f"- **Banca Atualizada:** R$ {self.state['total_equity_brl']:.2f}\n" \
                    f"---\n"
            with open(JOURNAL_FILE, 'a', encoding='utf-8') as f:
                f.write(entry)
        except Exception:
            pass

    def run_cycle(self):
        t0 = time.time()
        print("\n" + "=" * 68)
        print("🤖 ROBÔ BINANCE SPOT (SIMULADOR PAPER TRADING - BANCA R$ 50,00)")
        print(f"💰 Saldo Líquido: R$ {self.state['cash_balance_brl']:.2f} | Patrimônio Total: R$ {self.state['total_equity_brl']:.2f}")
        print(f"📈 Lucro Acumulado: R$ {self.state['accumulated_profit_brl']:.2f} ({self.state['profit_pct']:+.2f}%) | Taxas Pagas: R$ {self.state.get('total_fees_paid_brl', 0.0):.3f}")
        print("=" * 68)

        # 1. Atualiza posições em andamento
        self.update_open_positions()

        # Mede latência
        self.state["api_latency_ms"] = max(25, int((time.time() - t0) * 1000))

        # 2. Verifica se o usuário pausou as compras
        if self.state.get("is_paused", False):
            self.state["current_thought"] = "⏸️ Robô em modo PAUSADO pelo usuário. Monitorando lucros das posições abertas."
            self.add_detailed_log("PAUSA", "Simulador pausado manualmente pelo operador.")
            self.save_state()
            return

        # 3. Verifica a Lei #3 (Filtro Macro SMA 200 do Bitcoin)
        macro_ok = self.check_macro_sma200()

        if not macro_ok:
            self.state["current_thought"] = "🛡️ [LEI #3 ATIVA]: Bitcoin abaixo da SMA 200 diária. Robô mantém o dinheiro 100% protegido em caixa."
            self.add_detailed_log("MACRO_DEFESA", "Mercado global em correção. Novas compras bloqueadas.")
            self.save_state()
            return

        # 4. Escaneia mercado amplo da Binance (Top pares líquidos)
        dynamic_targets = self.market_scanner.scan_full_market(max_pairs=12)
        self.state["total_pairs_market"] = self.market_scanner.total_pairs_market
        self.state["active_monitored_pairs_count"] = len(dynamic_targets)

        # Atualiza inteligência histórica (500 velas)
        self.historical_analyzer.target_pairs = dynamic_targets
        hist_data = self.historical_analyzer.run_full_historical_analysis()
        self.state["historical_analysis"] = hist_data.get("pairs", {})

        # 5. Escaneamento Multi-Timeframe (15m, 1h, 4h)
        print(f"\n🔍 Escaneando {len(dynamic_targets)} pares líquidos da Binance em Multi-Timeframe (15m, 1h, 4h)...")
        has_cash_to_buy = self.state["cash_balance_brl"] >= ORDER_SIZE_BRL
        pair_studies = []
        if not has_cash_to_buy:
            print(f"ℹ️ Caixa atual (R$ {self.state['cash_balance_brl']:.2f}) aguardando fechamento de posições para novas compras. Continuando estudo do mercado...")

        for target in dynamic_targets:
            sym = target["symbol"]

            # Coleta dados nos 3 Timeframes
            t15 = self.fetch_candles_and_indicators(sym, interval="15m")
            t1h = self.fetch_candles_and_indicators(sym, interval="1h")
            t4h = self.fetch_candles_and_indicators(sym, interval="4h")

            if not t1h:
                continue

            price = t1h["current_price"]
            rsi_15m = t15["rsi"] if t15 else 50.0
            rsi_1h = t1h["rsi"]
            rsi_4h = t4h["rsi"] if t4h else 50.0

            trend_1h = "ALTA ↗" if t1h["ema9"] > t1h["ema21"] else "BAIXA ↘"
            trend_4h = "ALTA ↗" if (t4h and t4h["ema9"] > t4h["ema21"]) else "BAIXA ↘"

            pair_studies.append({
                "symbol": sym,
                "name": target["name"],
                "price": price,
                "rsi_15m": rsi_15m,
                "rsi_1h": rsi_1h,
                "rsi_4h": rsi_4h,
                "trend": trend_1h
            })

            # Evita comprar o mesmo par se já tiver posição aberta nele
            already_open = any(p["symbol"] == sym for p in self.state["open_positions"])
            if already_open:
                continue

            # DETECÇÃO MULTI-TIMEFRAME DE OPORTUNIDADES:
            is_scalp_15m = (rsi_15m <= 38 and trend_1h == "ALTA ↗")
            is_swing_1h = (rsi_1h <= 45 or (t1h["ema9"] > t1h["ema21"] and t1h["is_bull_candle"]))
            is_breakout_4h = (trend_4h == "ALTA ↗" and 48 <= rsi_4h <= 60 and (t15 and t15["is_bull_candle"]))

            matched_tf = None
            setup_desc = ""

            if is_scalp_15m:
                matched_tf = "15m"
                setup_desc = f"Scalp Dip 15M (RSI {rsi_15m} em suporte de 1H)"
            elif is_swing_1h:
                matched_tf = "1H"
                setup_desc = f"Swing Pullback 1H (RSI {rsi_1h} + EMA9/21 {trend_1h})"
            elif is_breakout_4h:
                matched_tf = "4H"
                setup_desc = f"Breakout Institucional 4H (Tendência Macro {trend_4h})"

            print(f"   • {sym:<10}: R$/$ {price:<9.2f} | 15m RSI: {rsi_15m:<4.1f} | 1h RSI: {rsi_1h:<4.1f} | 4h: {trend_4h} | Gatilho: {matched_tf or 'Nenhum'}")

            if matched_tf:
                if not has_cash_to_buy:
                    continue

                # 1. Filtro de Inteligência Machine Learning (Previsão de Probabilidade)
                ml_res = self.ml_predictor.train_and_evaluate_symbol(sym)
                if not ml_res.get("ml_approved", True):
                    self.add_detailed_log("ML_BLOCK", f"{sym} barrado pelo ML ({ml_res['confidence_score_pct']}% prob.): {ml_res.get('verdict')}")
                    print(f"   ⚠️ [Machine Learning]: {sym} barrado ({ml_res['confidence_score_pct']}% prob).")
                    continue

                # 2. Filtro Histórico (evita comprar no topo da resistência)
                hist_ok, hist_reason = self.historical_analyzer.evaluate_entry_safety(sym)
                if not hist_ok:
                    self.add_detailed_log("FILTRO_HISTORICO", f"{sym} bloqueado: {hist_reason}")
                    continue

                # 3. Risk Manager
                allowed, risk_reason, risk_status = self.risk_manager.evaluate_order(self.state, sym, ORDER_SIZE_BRL)
                if not allowed:
                    self.add_detailed_log("RISK_BLOCK", f"Ordem de {sym} bloqueada pelo Risk Manager: {risk_reason}")
                    continue

                # 4. Execução com Desconto de Taxas Reais da Binance
                buy_fee_brl = round(ORDER_SIZE_BRL * (TOTAL_ORDER_COST_PCT / 100.0), 4) # Taxa 0.10% + 0.05% slippage
                target_profit_price = price * (1 + (TAKE_PROFIT_PCT / 100.0))

                self.state["cash_balance_brl"] -= (ORDER_SIZE_BRL + buy_fee_brl)
                self.state["total_fees_paid_brl"] = round(self.state.get("total_fees_paid_brl", 0.0) + buy_fee_brl, 4)

                new_position = {
                    "symbol": sym,
                    "name": target["name"],
                    "timeframe": matched_tf,
                    "entry_time": datetime.now().strftime("%d/%m %H:%M:%S"),
                    "entry_price": price,
                    "target_price": round(target_profit_price, 4),
                    "stake_brl": ORDER_SIZE_BRL,
                    "buy_fee_brl": buy_fee_brl,
                    "current_price": price,
                    "current_pnl_pct": 0.0,
                    "ml_score": ml_res.get("confidence_score_pct", 75.0),
                    "reason": f"[{matched_tf}] {setup_desc} (ML: {ml_res.get('confidence_score_pct')}%)"
                }
                self.state["open_positions"].append(new_position)
                self.add_detailed_log("COMPRA_EXECUTADA", f"[{matched_tf}] Compra de R$ 10 em {sym} a {price:.4f} [ML Score: {ml_res.get('confidence_score_pct')}%]. Taxa: R$ {buy_fee_brl:.3f}.")
                print(f"\n🛒 [COMPRA EXECUTADA SPOT ({matched_tf})]: R$ {ORDER_SIZE_BRL:.2f} de {sym} a {price:.4f} [ML: {ml_res.get('confidence_score_pct')}%]!")
                print(f"💸 Taxa Binance Descontada: R$ {buy_fee_brl:.3f} | Alvo Líquido (+2%): {target_profit_price:.4f}")
                self.save_state()
                break

        # 6. Atualiza o Cérebro de IA com Modelo de Contingência
        thought, provider = self.ai_contingency.generate_market_thought(
            pair_studies, self.state["last_macro_status"], self.state.get("open_positions", []), self.state["total_equity_brl"]
        )
        self.state["current_thought"] = thought
        self.state["active_ai_provider"] = provider

        # 7. Registra estudo na Super Skill
        self.brain.record_market_study(pair_studies, self.state["last_macro_status"], self.state.get("closed_trades", []))
        self.state["super_skill"] = self.brain.state
        self.save_state()

if __name__ == '__main__':
    engine = BinanceSpotPaperEngine()
    engine.run_cycle()
