# 🏛️ As 3 Leis de Ouro do Robô Quantitativo Spot (Binance)

> Documento Fundamental de Arquitetura e Gestão de Risco do Robô de Trade Spot.  
> Inspirado nas melhores práticas dos maiores desenvolvedores quantitativos do varejo global.

---

## 🧭 O Veredito Fundamental:
> *"Se você vai programar um modelo de IA e quer a maior probabilidade possível de ver seu dinheiro crescer sem o estresse de acordar com a conta zerada:"*

---

### 1. ⏱️ LEI #1: ABANDONE O CURTÍSSIMO PRAZO (VELAS DE 1H A 4H)
* **O Problema do Ruído (30s / 1m):** Gráficos de segundos são dominados por robôs de alta frequência (HFT) e oscilações aleatórias. Qualquer oscilação de 1 centavo pode estragar uma análise.
* **A Regra da IA:** Programar a IA para analisar gráficos com relevância institucional: **Velas de 1 Hora (1H) e 4 Horas (4H)**.
* **O Benefício:** Cada sinal técnico (médias móveis, suportes, resistências, volumes) tem peso real e reflete o fluxo de capital verdadeiro do mercado, não um soluço de 30 segundos.

---

### 2. 💎 LEI #2: OPERE EXCLUSIVAMENTE NO MERCADO SPOT (ATIVO REAL)
* **Sem Alavancagem Suicida:** Não operar opções binárias nem contratos alavancados sem margem.
* **Propriedade Real:** No mercado Spot, ao comprar, você se torna o **dono legítimo da criptomoeda** (frações de BTC, ETH, SOL, NEAR, etc.).
* **Risco Zero de Liquidação:** Se o mercado passar por uma correção momentânea de -5%, a sua conta **NÃO é liquidada**. Você não tem tempo de expiração correndo contra você. Você simplesmente espera a recuperação e embolsa o lucro na alta.

---

### 3. 🛡️ LEI #3: FILTRO DE TENDÊNCIA GLOBAL (A TRAVA DA SMA 200)
* **A Regra de Proteção Absoluta:** O robô só tem permissão para realizar compras se o mercado como um todo estiver em **Tendência de Alta Global**.
* **O Gatilho da Média de 200 Dias (SMA 200):**
  - **Bitcoin ACIMA da SMA 200:** Sinal verde 🟢. O mercado cripto está saudável; o robô é autorizado a caçar compras e acumular lucros.
  - **Bitcoin ABAIXO da SMA 200 (Mercado em Colapso):** Sinal vermelho 🛑. O robô cruza os braços, mantém 100% do capital protegido em **moeda forte (USDT / Dólar)** e espera a tempestade passar.
* **O Benefício:** Enquanto 95% dos traders perdem tudo tentando "adivinhar o fundo" de uma queda livre, o nosso robô fica 100% líquido, com o dinheiro a salvo, esperando o momento perfeito para voltar a operar.

---

### ⚙️ Implementação no Código Python (`config_spot.json`):
```json
{
  "market": "SPOT",
  "timeframe": "1h",
  "macro_filter": {
    "indicator": "SMA_200",
    "benchmark": "BTCUSDT",
    "require_bull_regime": true
  },
  "strategy": {
    "type": "TREND_FOLLOWING_GRID",
    "take_profit_target_pct": 2.5,
    "never_sell_at_loss": true
  }
}
```
