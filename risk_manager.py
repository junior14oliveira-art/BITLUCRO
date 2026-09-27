"""
BITLUCRO - Módulo de Gestão de Risco e Circuit Breaker
Avalia a segurança do capital antes de qualquer ordem simulada.
Regra: A estratégia NUNCA executa ordens diretamente. Toda ordem passa pelo Risk Manager.
"""

from datetime import datetime

class RiskManager:
    def __init__(self, initial_capital=1000.0):
        self.initial_capital = initial_capital
        self.max_risk_per_trade = 50.00     # R$ 50,00 por entrada (5% da banca de R$ 1.000)
        self.max_drawdown_limit_pct = 10.0  # Limite máximo de perda acumulada: -10%
        self.max_daily_loss_pct = 6.0       # Perda máxima permitida no dia: -6%
        self.max_open_positions = 12        # Até 12 posições simultâneas (R$ 600 em risco, R$ 400 em caixa)
        self.max_consecutive_losses = 2     # Cooldown após 2 perdas seguidas

    def evaluate_order(self, state, symbol, order_size_brl):
        """
        Valida se a ordem pode ser executada ou se deve ser bloqueada.
        Retorna: (allowed: bool, reason: str, risk_status: str)
        """
        cash = state.get("cash_balance_brl", 0.0)
        equity = state.get("total_equity_brl", 1000.0)
        open_positions = state.get("open_positions", [])
        consecutive_losses = state.get("consecutive_losses", 0)

        # 1. Checagem de Caixa
        if cash < order_size_brl:
            return False, f"Caixa insuficiente (R$ {cash:.2f} livre < R$ {order_size_brl:.2f} mínimo).", "SAFE"

        # 2. Limite de Posições Abertas Simultâneas
        if len(open_positions) >= self.max_open_positions:
            return False, f"Limite de posições simultâneas atingido ({len(open_positions)}/{self.max_open_positions}).", "SAFE"

        # 3. Já possui posição no mesmo par?
        if any(p["symbol"] == symbol for p in open_positions):
            return False, f"Já existe custódia ativa para o ativo {symbol}. Evitando sobre-exposição.", "SAFE"

        # 4. Checagem de Drawdown Máximo (Circuit Breaker)
        drawdown_pct = state.get("drawdown_pct", 0.0)
        if drawdown_pct >= self.max_drawdown_limit_pct:
            return False, f"CIRCUIT BREAKER ATIVADO: Drawdown ({drawdown_pct:.1f}%) atingiu o teto de segurança ({self.max_drawdown_limit_pct}%).", "HALTED"

        # 5. Cooldown de Perdas Consecutivas
        if consecutive_losses >= self.max_consecutive_losses:
            return False, f"CIRCUIT BREAKER ATIVADO: Sequência de {consecutive_losses} prejuízos. Robô em pausa preventiva.", "WARNING"

        # 6. Mercado Bear Global (Filtro SMA 200)
        macro_status = state.get("last_macro_status", "")
        if "BEAR" in macro_status:
            return False, "Filtro Macro Global: Bitcoin abaixo da SMA 200. Compras congeladas.", "WARNING"

        return True, "Aprovado pelo Risk Manager. Parâmetros de segurança 100% satisfeitos.", "SAFE"

    def calculate_drawdown(self, peak_equity, current_equity):
        """Calcula o drawdown atual em relação ao topo histórico do patrimônio."""
        if peak_equity <= 0:
            return 0.0
        dd = ((peak_equity - current_equity) / peak_equity) * 100.0
        return max(0.0, round(dd, 2))
