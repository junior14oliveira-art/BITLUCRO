# 🤖 BITLUCRO | Robô Quantitativo Binance Spot 24/7

Sistema automatizado de análise quantitativa e operações no **Mercado Spot da Binance**, executando **24 horas por dia** com foco em preservação máxima de capital, acumulação consistente e **risco zero de liquidação**.

---

## 🛡️ As 3 Regras de Ouro (Blindagem de Capital)

Diferente de robôs de opções binárias ou alavancagem de futuros, o **BITLUCRO** opera exclusivamente com base em 3 princípios matemáticos fundamentais:

1. **Velas de 1 Hora a 4 Horas (Timeframe Maior)**:
   - Elimina o ruído aleatório e manipulações de gráficos de segundos (30s / 1m). O algoritmo só toma decisões quando a tendência do gráfico horário é confirmada.
2. **Mercado Spot Puro (Propriedade Real)**:
   - Não há alavancagem nem margem. Você compra a fração real do ativo cripto (Bitcoin, Solana, Ethereum, Render, etc.).
   - **Nunca vende no prejuízo**: se o mercado recuar temporariamente, o robô mantém a custódia do ativo com paciência até que ele valorize e bata o alvo de lucro pré-definido (**+2.0%**).
3. **Filtro Macro Global (Bitcoin > SMA 200)**:
   - Antes de abrir qualquer compra, o robô consulta a **Média Móvel Simples de 200 dias (SMA 200)** do Bitcoin.
   - Se o Bitcoin estiver abaixo da média de 200 dias (Mercado Bear / Queda Global), o robô **bloqueia novas compras** e mantém o capital 100% protegido em caixa (BRL / USDT).

---

## 💰 Simulação Ativa (Paper Trading R$ 50,00)

O robô está configurado com um motor de **Paper Trading** conectado diretamente aos livros de ofertas e cotações ao vivo da API oficial da Binance.
- **Banca Inicial:** R$ 50,00
- **Tamanho da Entrada:** R$ 10,00 por ordem (ordem mínima permitida pela Binance)
- **Meta de Lucro (Take Profit):** +2.0% por trade
- **Pares Monitorados:** `SOLBRL`, `BTCBRL`, `ETHBRL`, `NEARUSDT`, `RENDERUSDT`

---

## 📊 Dashboard Web em Tempo Real

O projeto já inclui um painel web responsivo (pronto para computador e celular) com atualização automática a cada 4 segundos:
- **Patrimônio Total e Saldo Líquido em Caixa**
- **Lucro Líquido Acumulado (R$ e %)**
- **Termômetro Macro Mundial (Bitcoin vs SMA 200)**
- **Tabela de Posições Abertas (Preço de Entrada, Cotação ao Vivo, Alvo de Lucro)**
- **Histórico de Trades Fechados com Sucesso**
- **Terminal de Pensamento e Diário de Bordo do Algoritmo**
- **Botão para Escaneamento Manual Instantâneo**

---

## ☁️ Como Hospedar Grátis 24/7 no Render.com

1. Crie uma conta gratuita em [render.com](https://render.com).
2. Clique em **New +** ➔ **Web Service**.
3. Conecte o repositório GitHub: `https://github.com/junior14oliveira-art/BITLUCRO.git`.
4. Preencha as configurações:
   - **Name:** `bitlucro-spot-bot`
   - **Region:** Ohio (US East) ou Frankfurt
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** `Free`
5. Clique em **Deploy Web Service**.
6. Em 2 minutos, o Render gerará um link público seguro HTTPS (exemplo: `https://bitlucro-spot-bot.onrender.com`) onde você poderá acompanhar seu robô de qualquer lugar pelo celular!

### 💡 Dica Ninja: Manter o Render Acordado 24/7 Sem Dormir
Na versão gratuita, o Render suspende serviços sem visitas após 15 minutos. Para manter seu robô operando 24 horas por dia ininterruptamente:
- Acesse [cron-job.org](https://cron-job.org) ou [uptimerobot.com](https://uptimerobot.com) (100% gratuitos).
- Cadastre a URL do seu endpoint de saúde: `https://seu-app-no-render.onrender.com/health`.
- Configure para disparar a cada **10 minutos**.
- Pronto! O robô ficará acordado, escaneando o mercado da Binance dia e noite.

---

## 💻 Como Rodar no Computador Localmente

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Iniciar o servidor web e robô
python app.py
```
Acesse no navegador: `http://localhost:5000`
