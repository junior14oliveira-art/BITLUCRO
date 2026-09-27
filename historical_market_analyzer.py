"""
BITLUCRO - Analisador de Histórico de Mercado & Backtesting Autônomo
Coleta centenas de velas horárias (1H) da Binance para cada par,
calcula suporte, resistência, volatilidade e assertividade histórica do Take Profit (+2%).
"""

import os
import json
import time
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORICAL_CACHE_FILE = os.path.join(BASE_DIR, 'historico_moedas.json')
BINANCE_API_URL = "https://api.binance.com/api/v3"

class HistoricalMarketAnalyzer:
    def __init__(self, target_pairs):
        self.target_pairs = target_pairs
        self.data = self.load_cache()

    def load_cache(self):
        if os.path.exists(HISTORICAL_CACHE_FILE):
            try:
                with open(HISTORICAL_CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "last_updated": None,
            "pairs": {}
        }

    def save_cache(self):
        try:
            with open(HISTORICAL_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[!] Erro ao salvar cache histórico: {e}")

    def should_refresh(self):
        """Atualiza a análise histórica a cada 30 minutos para evitar chamadas repetitivas."""
        if not self.data.get("last_updated"):
            return True
        try:
            last = datetime.strptime(self.data["last_updated"], "%d/%m/%Y %H:%M:%S")
            diff_minutes = (datetime.now() - last).total_seconds() / 60.0
            return diff_minutes >= 30.0
        except Exception:
            return True

    def analyze_pair_history(self, symbol, limit=500):
        """
        Coleta até 500 velas de 1h (~21 dias de dados) da Binance e executa backtest do gatilho.
        """
        try:
            url = f"{BINANCE_API_URL}/klines?symbol={symbol}&interval=1h&limit={limit}"
            candles = requests.get(url, timeout=6).json()
            if not candles or len(candles) < 50:
                return None

            closes = [float(c[4]) for c in candles]
            highs = [float(c[2]) for c in candles]
            lows = [float(c[3]) for c in candles]
            volumes = [float(c[5]) for c in candles]

            # 1. Suporte e Resistência dos últimos ~21 dias
            min_support = min(lows)
            max_resistance = max(highs)
            current_price = closes[-1]
            range_total = max_resistance - min_support
            
            # Posição percentual no range (0% = suporte mínimo, 100% = topo da resistência)
            range_position_pct = ((current_price - min_support) / range_total * 100.0) if range_total > 0 else 50.0

            # 2. Volatilidade média horária (%)
            volatilities = [((h - l) / l * 100.0) for h, l in zip(highs, lows)]
            avg_hourly_volatility = sum(volatilities) / len(volatilities) if volatilities else 1.0

            # 3. Backtest histórico do Alvo de +2.0%
            signals_count = 0
            wins_count = 0
            total_hours_to_win = 0

            for i in range(20, len(candles) - 36):
                # RSI 14
                diffs = [closes[j] - closes[j-1] for j in range(i-14, i)]
                gains = [d for d in diffs if d > 0]
                losses = [abs(d) for d in diffs if d < 0]
                avg_g = sum(gains) / 14 if gains else 0.0001
                avg_l = sum(losses) / 14 if losses else 0.0001
                rs = avg_g / avg_l if avg_l > 0 else 100.0
                rsi = 100.0 - (100.0 / (1.0 + rs))

                # Gatilho de compra
                if rsi <= 45:
                    signals_count += 1
                    entry = closes[i]
                    target = entry * 1.02 # +2.0%

                    # Verifica se atingiu nas próximas 48 velas (2 dias)
                    future_slice = highs[i+1 : min(i+49, len(candles))]
                    hit_target = False
                    for idx, h in enumerate(future_slice):
                        if h >= target:
                            hit_target = True
                            wins_count += 1
                            total_hours_to_win += (idx + 1)
                            break

            win_rate = (wins_count / signals_count * 100.0) if signals_count > 0 else 0.0
            avg_hours = round(total_hours_to_win / wins_count, 1) if wins_count > 0 else 12.0

            return {
                "candles_analyzed": len(candles),
                "support_price": round(min_support, 4),
                "resistance_price": round(max_resistance, 4),
                "current_price": round(current_price, 4),
                "range_position_pct": round(range_position_pct, 1),
                "historical_win_rate_pct": round(win_rate, 1),
                "signals_tested": signals_count,
                "wins_count": wins_count,
                "avg_hours_to_tp": avg_hours,
                "avg_hourly_volatility_pct": round(avg_hourly_volatility, 2),
                "status": "EXCELENTE" if win_rate >= 70 else ("BOM" if win_rate >= 55 else "MODERADO")
            }
        except Exception as e:
            print(f"[!] Erro ao analisar histórico de {symbol}: {e}")
            return None

    def run_full_historical_analysis(self, force=False):
        """Varre todas as moedas monitoradas e constrói a base de dados histórica."""
        if not force and not self.should_refresh():
            return self.data

        print("\n[HISTORICO DE MERCADO]: Baixando 500 velas de 1H da Binance para cada par...")
        updated_pairs = {}

        for item in self.target_pairs:
            sym = item["symbol"]
            res = self.analyze_pair_history(sym, limit=500)
            if res:
                res["name"] = item.get("name", sym)
                updated_pairs[sym] = res
                print(f"   * {sym:<10}: Win Rate: {res['historical_win_rate_pct']}% | Alvo: {res['avg_hours_to_tp']}h | Suporte: {res['support_price']} | Resistencia: {res['resistance_price']}")

        self.data["pairs"] = updated_pairs
        self.data["last_updated"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.save_cache()
        return self.data

    def evaluate_entry_safety(self, symbol):
        """
        Avalia se historicamente é seguro comprar agora.
        Regra: Se o preço estiver acima de 88% do topo histórico dos 21 dias (perto da resistência),
        o robô evita comprar no topo!
        """
        pair_info = self.data.get("pairs", {}).get(symbol)
        if not pair_info:
            return True, "Sem dados históricos prévios suficientes. Prosseguindo com filtros técnicos."

        range_pos = pair_info.get("range_position_pct", 50.0)
        win_rate = pair_info.get("historical_win_rate_pct", 60.0)

        if range_pos >= 90.0:
            return False, f"Ativo em Resistência Máxima dos últimos 21 dias ({range_pos:.1f}% do range). Evitando compra no topo."

        if win_rate < 50.0:
            return False, f"Assertividade histórica de +2% abaixo do corte de segurança ({win_rate:.1f}%)."

        return True, f"Zona de Valor Histórica favorável ({range_pos:.1f}% do range | Win Rate Histórico: {win_rate:.1f}%)."
