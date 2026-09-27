"""
BITLUCRO - Robô Quantitativo Binance Spot 24/7 (Hospedagem Render)
Servidor Web Flask + Dashboard Moderno com Heurísticas de Usabilidade de Nielsen
"""

import os
import sys
import io
import json
import time
import threading
from datetime import datetime
import requests
from flask import Flask, jsonify, render_template_string, request, Response

# Configuração de encoding para UTF-8 seguro
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Importa o motor de trading
from spot_paper_engine import BinanceSpotPaperEngine, STATE_FILE

app = Flask(__name__)
engine = BinanceSpotPaperEngine()

# Histórico de logs para exibição no dashboard web
activity_logs = [
    f"[{datetime.now().strftime('%H:%M:%S')}] BITLUCRO inicializado. Conexão pública com Binance Spot ativa."
]

def add_log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    activity_logs.insert(0, entry)
    if len(activity_logs) > 35:
        activity_logs.pop()

# Worker em segundo plano (roda 24/7)
def background_trading_loop():
    time.sleep(2)
    add_log("Worker 24/7 em execução contínua. Intervalo de análise ágil: 25s.")
    while True:
        try:
            engine.run_cycle()
            status = engine.state.get("last_macro_status", "Ativo")
            add_log(f"Ciclo executado. Macro: {status} | Saldo: R$ {engine.state['cash_balance_brl']:.2f}")
        except Exception as e:
            add_log(f"Alerta no ciclo: {str(e)}")
        time.sleep(25)

worker_thread = threading.Thread(target=background_trading_loop, daemon=True)
worker_thread.start()

# Rastreador de PnL e Alvos Ultrarrápido (executa a cada 3s)
def fast_pnl_tracker_loop():
    time.sleep(4)
    while True:
        try:
            if engine.state.get("open_positions"):
                engine.update_open_positions_pnl()
        except Exception:
            pass
        time.sleep(3)

pnl_thread = threading.Thread(target=fast_pnl_tracker_loop, daemon=True)
pnl_thread.start()

# Keep-Alive Automático para evitar que o Render hiberne (a cada 10 minutos)
def keep_alive_self_ping():
    time.sleep(60)
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "https://bitlucro-spot-bot.onrender.com")
    while True:
        try:
            requests.get(f"{render_url}/health", timeout=10)
        except Exception:
            pass
        time.sleep(600)

ping_thread = threading.Thread(target=keep_alive_self_ping, daemon=True)
ping_thread.start()

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>BITLUCRO | Binance Spot Bot 24/7</title>

  <!-- PWA & Mobile Web App Meta Tags -->
  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#0B0E14">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="BITLUCRO">
  <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/5968/5968260.png">
  <link rel="icon" type="image/png" href="https://cdn-icons-png.flaticon.com/512/5968/5968260.png">

  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: { 500: '#F0B90B', 600: '#D9A408' },
            darkbg: '#0B0E14',
            cardbg: '#121722',
            bordercol: '#1E2538'
          }
        }
      }
    }
  </script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0B0E14; }
    .mono { font-family: 'JetBrains Mono', monospace; }
    .pulse-dot {
      box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
      animation: pulseAnim 2s infinite;
    }
    @keyframes pulseAnim {
      0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
      70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
      100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }
    .custom-scroll::-webkit-scrollbar { width: 5px; height: 5px; }
    .custom-scroll::-webkit-scrollbar-track { background: #0e121a; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #232c3f; border-radius: 4px; }
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    button, a { -webkit-tap-highlight-color: transparent; }
  </style>
</head>
<body class="text-slate-100 min-h-screen flex flex-col justify-between antialiased selection:bg-amber-500/30 selection:text-amber-300">

  <!-- ==========================================
       BANNER PWA: INSTALAR NO CELULAR
       ========================================== -->
  <div id="pwaInstallBanner" class="bg-gradient-to-r from-amber-500/20 via-purple-500/20 to-blue-500/20 border-b border-amber-500/30 px-3 py-2 text-xs flex items-center justify-between hidden transition-all sticky top-0 z-50 backdrop-blur-md">
    <div class="flex items-center space-x-2.5">
      <div class="w-7 h-7 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center text-sm font-bold shrink-0">
        <i class="fa-solid fa-mobile-screen-button"></i>
      </div>
      <div>
        <span class="font-bold text-white">Instalar BITLUCRO no Celular</span>
        <span class="text-slate-400 hidden sm:inline"> — Use como app nativo em tela cheia na sua tela inicial</span>
      </div>
    </div>
    <div class="flex items-center space-x-2 shrink-0">
      <button onclick="installPWA()" class="bg-amber-500 hover:bg-amber-400 text-slate-950 font-black px-3 py-1 rounded-lg text-xs transition shadow flex items-center gap-1.5">
        <i class="fa-solid fa-download"></i> <span>Instalar App</span>
      </button>
      <button onclick="dismissPWABanner()" class="text-slate-400 hover:text-white p-1 text-sm" title="Fechar">
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>
  </div>

  <!-- ==========================================
       HEURÍSTICA #1 & #4: CABEÇALHO COM VISIBILIDADE DO STATUS
       ========================================== -->
  <header class="border-b border-slate-800/80 bg-cardbg/80 backdrop-blur-md sticky top-0 z-40 px-3 sm:px-4 py-2.5 sm:py-3">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-2.5">
      
      <!-- Topo: Logo + Botão App Mobile + Botão Ajuda -->
      <div class="flex items-center justify-between w-full md:w-auto">
        <div class="flex items-center space-x-2.5">
          <div class="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 font-extrabold text-lg shadow-lg">
            <i class="fa-brands fa-bitcoin"></i>
          </div>
          <div>
            <div class="flex items-center space-x-2">
              <h1 class="text-base sm:text-lg font-black tracking-tight text-white flex items-center gap-1.5 leading-tight">
                BITLUCRO <span class="text-amber-400 text-[10px] sm:text-xs px-1.5 py-0.2 rounded bg-amber-500/10 border border-amber-500/20 font-bold">SPOT PRO</span>
              </h1>
            </div>
            <p class="text-[10px] sm:text-[11px] text-slate-400 leading-tight">Algoritmo Quantitativo 24/7 | Proteção Sem Liquidação</p>
          </div>
        </div>

        <div class="flex items-center space-x-1.5 md:hidden">
          <button onclick="installPWA()" class="text-amber-400 bg-amber-500/10 border border-amber-500/30 hover:bg-amber-500/20 px-2 py-1 rounded-lg text-xs font-bold flex items-center gap-1" title="Instalar no Celular">
            <i class="fa-solid fa-mobile-screen"></i> <span>App</span>
          </button>
          <button onclick="toggleHelpModal(true)" class="text-slate-400 hover:text-white p-1.5 text-sm" title="Guia do Investidor">
            <i class="fa-solid fa-circle-question"></i>
          </button>
        </div>
      </div>

      <!-- Barra de Status do Sistema & Controles Rápidos (com swipe horizontal suave no mobile) -->
      <div class="flex items-center space-x-2 w-full md:w-auto overflow-x-auto pb-1 md:pb-0 no-scrollbar shrink-0">
        
        <!-- Status da API Binance (Heurística #1) -->
        <div class="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-2.5 py-1.5 rounded-lg text-xs shrink-0" title="Status da Conexão com Binance Spot">
          <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 pulse-dot" id="statusDot"></span>
          <span class="font-bold text-emerald-400 uppercase tracking-wider text-[11px]" id="statusText">ONLINE 24H</span>
          <span class="text-slate-500">|</span>
          <span class="mono text-slate-400 text-[11px]" id="latencyBadge"><i class="fa-solid fa-bolt text-amber-400 text-[10px]"></i> 54ms</span>
          <span class="text-slate-500 hidden lg:inline">|</span>
          <span class="text-amber-400 font-bold text-[11px] hidden lg:flex items-center gap-1" id="pairsCountBadge" title="Varredura de todo o mercado Binance">
            <i class="fa-solid fa-globe text-amber-400 text-[10px]"></i> <span id="pairsCountText">3.716 Pares</span>
          </span>
        </div>

        <!-- Botão Pausar / Retomar -->
        <button onclick="togglePause()" id="btnPause" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold px-3 py-1.5 rounded-lg flex items-center space-x-1.5 transition shrink-0">
          <i class="fa-solid fa-pause" id="pauseIcon"></i>
          <span id="pauseLabel">Pausar</span>
        </button>

        <!-- Botão Escanear Agora -->
        <button onclick="triggerScan()" id="btnScan" class="text-xs bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold px-3 py-1.5 rounded-lg flex items-center space-x-1.5 transition shadow shrink-0">
          <i class="fa-solid fa-arrows-rotate" id="scanIcon"></i>
          <span>Escanear</span>
        </button>

        <!-- Botão Super Skill (Aprendizado Contínuo) -->
        <button onclick="toggleSkillModal(true)" class="text-xs bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/30 font-bold px-2.5 py-1.5 rounded-lg flex items-center space-x-1.5 transition shrink-0" title="Super Skill & Caderno de Inteligência">
          <i class="fa-solid fa-brain text-purple-400"></i>
          <span id="skillBadge">Super Skill</span>
        </button>

        <!-- Botão Histórico 500H -->
        <button onclick="toggleHistoryModal(true)" class="text-xs bg-blue-500/10 hover:bg-blue-500/20 text-blue-300 border border-blue-500/30 font-bold px-2.5 py-1.5 rounded-lg flex items-center space-x-1.5 transition shrink-0" title="Inteligência Histórica dos Últimos 21 Dias">
          <i class="fa-solid fa-chart-line text-blue-400"></i>
          <span>Histórico 500H</span>
        </button>

        <!-- Botão Modelos IA (Contingência) -->
        <button onclick="toggleAiModal(true)" class="text-xs bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/30 font-bold px-2.5 py-1.5 rounded-lg flex items-center space-x-1.5 transition shrink-0" title="Modelos de IA & Contingência 24/7">
          <i class="fa-solid fa-server text-purple-400"></i>
          <span>Modelos IA</span>
        </button>

        <!-- Botão Baixar Excel -->
        <a href="/api/export/excel" download class="text-xs bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 font-bold px-2.5 py-1.5 rounded-lg flex items-center space-x-1.5 transition shadow shrink-0" title="Baixar Dados em Excel (CSV)">
          <i class="fa-solid fa-file-excel text-emerald-400"></i>
          <span>Excel</span>
        </a>

        <!-- Botão Guia / FAQ (Desktop) -->
        <button onclick="toggleHelpModal(true)" class="hidden md:flex text-xs bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700/80 font-semibold px-2.5 py-1.5 rounded-lg items-center space-x-1 transition shrink-0" title="Guia e Princípios de Operação">
          <i class="fa-solid fa-circle-question text-amber-400"></i>
          <span>Guia</span>
        </button>
      </div>

    </div>
  </header>

  <!-- ==========================================
       CONTEÚDO PRINCIPAL
       ========================================== -->
  <main class="max-w-7xl mx-auto p-4 space-y-4 w-full flex-1">

    <!-- Heurística #5: Prevenção de Erros & Heurística #6: Reconhecimento das Leis -->
    <div class="bg-gradient-to-r from-amber-950/30 via-cardbg to-slate-900/60 border border-amber-500/20 rounded-xl p-3 sm:p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs shadow-md">
      <div class="flex items-center space-x-2 text-amber-400 font-bold">
        <i class="fa-solid fa-shield-halved text-base"></i>
        <span>BLINDAGEM QUANTITATIVA (3 LEIS DE OURO):</span>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 w-full md:w-auto text-slate-300">
        <div class="bg-darkbg/90 px-2.5 py-1.5 rounded-lg border border-slate-800 flex items-center space-x-1.5">
          <span class="text-amber-400 font-extrabold">#1</span>
          <span>Multi-TF (15m, 1h, 4h)</span>
        </div>
        <div class="bg-darkbg/90 px-2.5 py-1.5 rounded-lg border border-slate-800 flex items-center space-x-1.5">
          <span class="text-emerald-400 font-extrabold">#2</span>
          <span>Spot (Sem Liquidação)</span>
        </div>
        <div class="bg-darkbg/90 px-2.5 py-1.5 rounded-lg border border-slate-800 flex items-center space-x-1.5">
          <span class="text-blue-400 font-extrabold">#3</span>
          <span>BTC > SMA 200 Macro</span>
        </div>
        <div class="bg-darkbg/90 px-2.5 py-1.5 rounded-lg border border-slate-800 flex items-center space-x-1.5">
          <span class="text-purple-400 font-extrabold">#4</span>
          <span>Machine Learning (>65%)</span>
        </div>
      </div>
    </div>

    <!-- Heurística #2: Correspondência com o Mundo Real (4 Cards de Métricas Financeiras) -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
      
      <!-- Patrimônio Total -->
      <div class="bg-cardbg border border-bordercol rounded-xl p-4 shadow-sm hover:border-slate-700 transition">
        <div class="flex items-center justify-between text-xs text-slate-400 font-medium">
          <span>Patrimônio Total</span>
          <i class="fa-solid fa-vault text-amber-400/80"></i>
        </div>
        <div class="text-2xl font-black text-white mono mt-1.5" id="totalEquity">R$ 50,00</div>
        <div class="text-[11px] text-slate-400 mt-1 flex items-center justify-between">
          <span>Banca Inicial:</span>
          <span class="mono font-semibold text-slate-300" id="initialCapital">R$ 50,00</span>
        </div>
      </div>

      <!-- Saldo Líquido Livre -->
      <div class="bg-cardbg border border-bordercol rounded-xl p-4 shadow-sm hover:border-slate-700 transition">
        <div class="flex items-center justify-between text-xs text-slate-400 font-medium">
          <span>Caixa Livre (BRL)</span>
          <i class="fa-solid fa-money-bill-wave text-emerald-400/80"></i>
        </div>
        <div class="text-2xl font-black text-emerald-400 mono mt-1.5" id="cashBalance">R$ 40,00</div>
        <div class="text-[11px] text-slate-400 mt-1">Disponível para Compras</div>
      </div>

      <!-- Lucro Líquido Acumulado -->
      <div class="bg-cardbg border border-bordercol rounded-xl p-4 shadow-sm hover:border-slate-700 transition">
        <div class="flex items-center justify-between text-xs text-slate-400 font-medium">
          <span>Lucro Líquido Realizado</span>
          <i class="fa-solid fa-chart-line-up text-blue-400/80"></i>
        </div>
        <div class="text-2xl font-black text-white mono mt-1.5" id="profitBrl">+R$ 0,00</div>
        <div class="text-[11px] font-bold text-emerald-400 mt-1 mono" id="profitPct">+0.00%</div>
      </div>

      <!-- Operações & Win Rate -->
      <div class="bg-cardbg border border-bordercol rounded-xl p-4 shadow-sm hover:border-slate-700 transition">
        <div class="flex items-center justify-between text-xs text-slate-400 font-medium">
          <span>Operações Finalizadas</span>
          <i class="fa-solid fa-trophy text-amber-400/80"></i>
        </div>
        <div class="text-2xl font-black text-amber-400 mono mt-1.5" id="winCountBadge">0 Wins</div>
        <div class="text-[11px] text-slate-400 mt-1 flex items-center justify-between">
          <span>0 Vendas no Prejuízo</span>
          <span class="text-emerald-400 font-bold text-[10px] bg-emerald-500/10 px-1 rounded">100% SPOT</span>
        </div>
      </div>

    </div>

    <!-- Barra de Fidelidade: Taxas da Binance -->
    <div class="bg-cardbg border border-bordercol rounded-xl px-4 py-2.5 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-300 gap-2 shadow-sm">
      <div class="flex items-center gap-2">
        <i class="fa-solid fa-receipt text-amber-400"></i>
        <span><b>Simulação Ultra-Fiel:</b> Taxas da Binance Descontadas (0.10% Spot + 0.05% Slippage):</span>
        <span class="mono font-bold text-amber-400 text-sm" id="totalFeesPaid">R$ 0.000</span>
      </div>
      <div class="text-[11px] text-slate-400 flex items-center gap-1.5">
        <i class="fa-solid fa-shield-check text-emerald-400"></i>
        <span>Lucro exibido é <b>100% Líquido no Bolso</b> após todos os custos da exchange.</span>
      </div>
    </div>

    <!-- Heurística #1: Termômetro Macro Mundial (Bitcoin vs SMA 200) -->
    <div class="bg-cardbg border border-bordercol rounded-xl p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 shadow-sm">
      <div class="flex items-center space-x-3.5">
        <div class="w-11 h-11 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 text-xl shrink-0">
          <i class="fa-solid fa-globe"></i>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Termômetro Macro Mundial</span>
            <span class="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-mono">SMA 200 Diária</span>
          </div>
          <div class="text-sm font-bold text-white mt-0.5 flex items-center gap-2" id="macroStatus">
            Carregando cotações da Binance...
          </div>
        </div>
      </div>
      <div class="text-xs text-slate-400 md:text-right bg-darkbg/70 px-3 py-2 rounded-lg border border-slate-800/80 w-full md:w-auto">
        <span class="text-emerald-400 font-bold">🟢 Mercado de Alta (Bull):</span> Novas compras autorizadas.<br class="hidden sm:inline">
        <span class="text-amber-400 font-bold">🛑 Mercado de Baixa (Bear):</span> Robô protege 100% do capital em caixa.
      </div>
    </div>

    <!-- CARD: O Que o Robô Está Pensando & Analisando Agora -->
    <div class="bg-gradient-to-br from-cardbg via-slate-900 to-darkbg border border-purple-500/40 rounded-xl p-4 shadow-md">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-bordercol pb-2.5 mb-3">
        <div class="flex items-center space-x-2.5">
          <div class="w-9 h-9 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 text-lg">
            <i class="fa-solid fa-brain"></i>
          </div>
          <div>
            <h3 class="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              O Que o Robô Está Pensando & Analisando Agora
            </h3>
            <span class="text-[10px] text-slate-400">Raciocínio Quantitativo Autônomo com Contingência 24H</span>
          </div>
        </div>

        <div class="flex items-center space-x-2 flex-wrap gap-y-1">
          <!-- MODELO EM USO EM DESTAQUE MÁXIMO -->
          <div class="flex items-center space-x-1.5 bg-purple-950/80 border-2 border-purple-500/60 px-3 py-1.5 rounded-xl shadow-lg">
            <span class="text-[10px] uppercase font-black text-amber-400 tracking-wider flex items-center gap-1.5">
              <i class="fa-solid fa-microchip text-purple-400 animate-pulse text-xs"></i> MODELO EM AÇÃO:
            </span>
            <span class="text-xs font-black text-white font-mono" id="activeAiBadge">
              Motor Quantitativo Local (Heurístico 24/7)
            </span>
          </div>
          <button onclick="toggleAiModal(true)" class="text-[11px] bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/40 px-2.5 py-1.5 rounded-xl font-bold transition flex items-center gap-1.5 shadow" title="Ver status da contingência dos modelos de IA">
            <i class="fa-solid fa-layer-group text-purple-400"></i> Modelos de IA
          </button>
        </div>
      </div>

      <div class="bg-darkbg/90 border border-slate-800 rounded-lg p-3.5 text-xs text-slate-200 leading-relaxed font-sans shadow-inner space-y-2.5">
        <div>
          <i class="fa-solid fa-quote-left text-purple-400 mr-1.5 opacity-60"></i>
          <span id="currentThoughtText" class="italic">Analisando cotações em tempo real da Binance...</span>
        </div>
        <div class="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 flex-wrap gap-2">
          <div class="flex items-center gap-1.5">
            <span class="text-slate-500">Cérebro da Análise:</span>
            <span class="font-mono font-bold text-amber-400" id="thoughtSourceModel">Motor Quantitativo Local (Heurístico 24/7)</span>
          </div>
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-emerald-400 font-semibold flex items-center gap-1"><i class="fa-solid fa-shield-check"></i> Contingência Ativa</span>
            <span class="text-slate-600">|</span>
            <a href="/api/export/excel" download class="text-[11px] bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 px-2 py-0.5 rounded font-bold transition flex items-center gap-1 shadow">
              <i class="fa-solid fa-file-excel text-emerald-400"></i> Baixar Dados (Excel)
            </a>
            <span class="text-slate-600">|</span>
            <button onclick="toggleAiModal(true)" class="text-purple-400 hover:text-purple-300 font-bold underline">APIs Grátis</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabela de Posições Abertas (Custódia Spot) -->
    <div class="bg-cardbg border border-bordercol rounded-xl p-3 sm:p-4 shadow-sm">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center space-x-2">
          <i class="fa-solid fa-layer-group text-amber-400"></i>
          <h2 class="text-xs sm:text-sm font-bold text-white tracking-wide">Ativos em Custódia Spot (Posições Abertas)</h2>
          <span class="inline-flex items-center gap-1 text-[9px] sm:text-[10px] bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-full font-bold ml-1 shadow-sm" title="Preços e porcentagens atualizados a cada 1 segundo direto da Binance">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> TEMPO REAL (1s)
          </span>
        </div>
        <div class="flex items-center space-x-2 text-xs text-slate-400">
          <span class="mono bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700/60" id="openCount">0 ativas</span>
        </div>
      </div>

      <!-- VISÃO DESKTOP: TABELA (oculta em telas menores que 768px) -->
      <div class="hidden md:block overflow-x-auto custom-scroll">
        <table class="w-full text-left text-xs min-w-[700px]">
          <thead>
            <tr class="border-b border-bordercol text-slate-400 font-semibold uppercase text-[11px] tracking-wider">
              <th class="py-2.5 px-3">TF</th>
              <th class="py-2.5 px-3">Ativo</th>
              <th class="py-2.5 px-3">Data / Hora</th>
              <th class="py-2.5 px-3">Preço Compra</th>
              <th class="py-2.5 px-3">Cotação Atual</th>
              <th class="py-2.5 px-3">Alvo Lucro (+2%)</th>
              <th class="py-2.5 px-3">Rentabilidade</th>
              <th class="py-2.5 px-3">Taxa Paga</th>
              <th class="py-2.5 px-3 text-right">Valor em BRL</th>
            </tr>
          </thead>
          <tbody id="positionsTable" class="divide-y divide-bordercol/60 font-medium">
            <tr>
              <td colspan="9" class="py-6 text-center text-slate-400">
                <i class="fa-solid fa-spinner fa-spin text-amber-400 mr-2"></i> Carregando carteira de ativos...
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- VISÃO MOBILE: CARDS TOUCH-FRIENDLY (visível apenas em celulares < 768px) -->
      <div id="mobilePositionsCards" class="md:hidden space-y-2.5">
        <div class="py-6 text-center text-slate-400 bg-darkbg/50 rounded-xl border border-dashed border-slate-800">
          <i class="fa-solid fa-spinner fa-spin text-amber-400 mr-2"></i> Carregando carteira de ativos...
        </div>
      </div>
    </div>

    <!-- Grade Inferior: Histórico de Trades Fechados & Logs Detalhados em Tempo Real -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">

      <!-- Histórico de Trades Fechados com Lucro -->
      <div class="bg-cardbg border border-bordercol rounded-xl p-4 shadow-sm flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3.5">
            <div class="flex items-center space-x-2">
              <i class="fa-solid fa-circle-check text-emerald-400"></i>
              <h2 class="text-sm font-bold text-white tracking-wide">Histórico de Operações Lucradas</h2>
            </div>
            <span class="mono text-xs text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700/60" id="closedCount">0 fechadas</span>
          </div>

          <div class="overflow-x-auto max-h-64 overflow-y-auto custom-scroll pr-1">
            <table class="w-full text-left text-xs min-w-[340px]">
              <thead>
                <tr class="border-b border-bordercol text-slate-400 uppercase text-[11px] tracking-wider">
                  <th class="py-2 px-2">Ativo</th>
                  <th class="py-2 px-2">Saída</th>
                  <th class="py-2 px-2">Lucro %</th>
                  <th class="py-2 px-2 text-right">Lucro Líquido</th>
                </tr>
              </thead>
              <tbody id="historyTable" class="divide-y divide-bordercol/60">
                <tr>
                  <td colspan="4" class="py-6 text-center text-slate-400">
                    Ainda não há operações finalizadas. O robô aguarda o alvo de +2.0% para realizar a venda automática com lucro.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Heurística #3 & #5: Ação de Reset com Prevenção de Erros -->
        <div class="pt-3 border-t border-bordercol mt-3 flex items-center justify-between text-xs">
          <span class="text-slate-400">Deseja zerar a simulação para R$ 50?</span>
          <button onclick="confirmReset()" class="text-slate-400 hover:text-rose-400 transition font-medium flex items-center gap-1">
            <i class="fa-solid fa-rotate-left"></i>
            <span>Reiniciar Simulador</span>
          </button>
        </div>
      </div>

      <!-- CARD: Logs de Tudo o Que Está Acontecendo -->
      <div class="bg-cardbg border border-bordercol rounded-xl p-4 shadow-sm flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3.5">
            <div class="flex items-center space-x-2">
              <i class="fa-solid fa-list-check text-blue-400"></i>
              <h2 class="text-sm font-bold text-white tracking-wide">Logs de Tudo o Que Está Acontecendo</h2>
            </div>
            <span class="text-[10px] mono text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700/60">Tempo Real</span>
          </div>

          <div id="detailedLogConsole" class="bg-darkbg border border-slate-800 rounded-lg p-3 text-xs mono text-slate-300 h-64 overflow-y-auto space-y-1.5 custom-scroll">
            <div class="text-slate-500">Conectando ao fluxo de eventos...</div>
          </div>
        </div>

        <div class="pt-3 border-t border-bordercol mt-3 flex items-center justify-between text-xs text-slate-400">
          <span>Próxima varredura em: <b class="text-white mono" id="countdownTimer">60s</b></span>
          <span class="text-[11px] text-emerald-400 font-semibold"><i class="fa-solid fa-check"></i> Binance REST v3</span>
        </div>
      </div>

    </div>

  </main>

  <!-- ==========================================
       RODAPÉ INFORMATIVO
       ========================================== -->
  <footer class="border-t border-bordercol bg-cardbg/50 py-3.5 px-4 text-xs text-slate-400 mt-4">
    <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-center sm:text-left">
      <div>
        <span class="font-bold text-white">BITLUCRO Spot Bot</span> • Ambiente de Testes Quantitativos • Cotações Oficiais da Binance em Tempo Real
      </div>
      <div class="mono text-slate-300 text-[11px]">
        Última Análise: <span id="lastUpdate" class="text-white font-semibold">--</span>
      </div>
    </div>
  </footer>

  <!-- ==========================================
       MODAL DE CONFIRMAÇÃO DE RESET (HEURÍSTICA #5: PREVENÇÃO DE ERROS)
       ========================================== -->
  <div id="resetModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-cardbg border border-rose-500/40 rounded-2xl max-w-sm w-full p-5 space-y-4 shadow-2xl">
      <div class="flex items-center space-x-3 text-rose-400">
        <div class="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-xl">
          <i class="fa-solid fa-triangle-exclamation"></i>
        </div>
        <h3 class="text-base font-bold text-white">Reiniciar Simulação?</h3>
      </div>
      <p class="text-xs text-slate-300 leading-relaxed">
        Esta ação irá zerar todas as posições em andamento, o histórico de lucros e restaurar o caixa exatamente para <b>R$ 50,00</b>. Tem certeza?
      </p>
      <div class="flex items-center justify-end space-x-2 pt-2">
        <button onclick="toggleResetModal(false)" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold px-4 py-2 rounded-lg transition">
          Cancelar
        </button>
        <button onclick="executeReset()" class="text-xs bg-rose-600 hover:bg-rose-500 text-white font-bold px-4 py-2 rounded-lg transition shadow-md">
          Sim, Resetar R$ 50
        </button>
      </div>
    </div>
  </div>

  <!-- ==========================================
       MODAL GUIA DO INVESTIDOR (HEURÍSTICA #10: AJUDA E DOCUMENTAÇÃO)
       ========================================== -->
  <div id="helpModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-cardbg border border-bordercol rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl max-h-[85vh] overflow-y-auto custom-scroll">
      <div class="flex items-center justify-between border-b border-bordercol pb-3">
        <div class="flex items-center space-x-2.5 text-amber-400">
          <i class="fa-solid fa-book-bookmark text-lg"></i>
          <h3 class="text-base font-bold text-white">Guia Rápido do Operador BITLUCRO</h3>
        </div>
        <button onclick="toggleHelpModal(false)" class="text-slate-400 hover:text-white p-1">
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>

      <div class="space-y-3.5 text-xs text-slate-300 leading-relaxed">
        <div class="bg-darkbg p-3 rounded-xl border border-slate-800">
          <b class="text-white flex items-center gap-1.5 mb-1"><i class="fa-solid fa-shield text-amber-400"></i> Por que o Mercado Spot não quebra?</b>
          Ao contrário do mercado futuro ou opções binárias, no Spot você compra a criptomoeda real. Não há taxa de liquidação forçada. Se o preço cair, você continua dono das moedas e aguarda a valorização para vender no lucro.
        </div>

        <div class="bg-darkbg p-3 rounded-xl border border-slate-800">
          <b class="text-white flex items-center gap-1.5 mb-1"><i class="fa-solid fa-chart-line text-blue-400"></i> O que é o Filtro Macro SMA 200?</b>
          A Média Móvel de 200 dias do Bitcoin é o maior indicador institucional do mundo. Quando o Bitcoin está acima da SMA 200, estamos em Bull Market (compras seguras). Se cair abaixo, o robô congela compras e guarda o dinheiro 100% seguro em caixa.
        </div>

        <div class="bg-darkbg p-3 rounded-xl border border-slate-800">
          <b class="text-white flex items-center gap-1.5 mb-1"><i class="fa-solid fa-bullseye text-emerald-400"></i> Alvo de Lucro de +2.0% (Take Profit):</b>
          Toda ordem de R$ 10,00 tem alvo fixo programado de +2,00% de lucro líquido. Quando atingido, o robô vende automaticamente, recolhe o lucro e libera o capital para novas oportunidades.
        </div>
      </div>

      <div class="pt-2 text-right">
        <button onclick="toggleHelpModal(false)" class="text-xs bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-4 py-2 rounded-lg transition">
          Entendi, Fechar
        </button>
      </div>
    </div>
  </div>

  <!-- ==========================================
       MODAL SUPER SKILL: CADERNO DE INTELIGÊNCIA QUANTITATIVA
       ========================================== -->
  <div id="skillModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-cardbg border border-purple-500/40 rounded-2xl max-w-xl w-full p-6 space-y-4 shadow-2xl max-h-[85vh] overflow-y-auto custom-scroll">
      <div class="flex items-center justify-between border-b border-bordercol pb-3">
        <div class="flex items-center space-x-2.5 text-purple-400">
          <i class="fa-solid fa-brain text-xl"></i>
          <div>
            <h3 class="text-base font-bold text-white">Super Skill: Caderno de Inteligência</h3>
            <p class="text-[11px] text-slate-400">Auto-aprendizado quantitativo com cotações oficiais da Binance</p>
          </div>
        </div>
        <button onclick="toggleSkillModal(false)" class="text-slate-400 hover:text-white p-1">
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>

      <!-- Métricas da Super Skill -->
      <div class="grid grid-cols-3 gap-2.5 text-center">
        <div class="bg-darkbg p-3 rounded-xl border border-slate-800">
          <div class="text-[10px] text-slate-400 font-medium">Nível do Robô</div>
          <div class="text-sm font-black text-purple-400 mt-0.5" id="skillLevel">Nível 1</div>
          <div class="text-[9px] text-slate-500" id="skillTitle">Analista Júnior</div>
        </div>
        <div class="bg-darkbg p-3 rounded-xl border border-slate-800">
          <div class="text-[10px] text-slate-400 font-medium">Tempo Estudado</div>
          <div class="text-sm font-black text-emerald-400 mt-0.5" id="skillHours">0.1h</div>
          <div class="text-[9px] text-slate-500" id="skillCycles">0 ciclos</div>
        </div>
        <div class="bg-darkbg p-3 rounded-xl border border-slate-800">
          <div class="text-[10px] text-slate-400 font-medium">Leis Consolidadas</div>
          <div class="text-sm font-black text-amber-400 mt-0.5">3 Leis</div>
          <div class="text-[9px] text-slate-500">Spot Protegido</div>
        </div>
      </div>

      <!-- Lições e Padrões Aprendidos -->
      <div class="space-y-2">
        <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
          <i class="fa-solid fa-lightbulb text-amber-400"></i> Playbook & Lições Aprendidas
        </h4>
        <div id="skillLearningsList" class="space-y-2 text-xs">
          <!-- Dinâmico -->
        </div>
      </div>

      <!-- Leituras Técnicas Recentes -->
      <div class="space-y-2">
        <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
          <i class="fa-solid fa-chart-simple text-blue-400"></i> Leituras Técnicas Recentes
        </h4>
        <div id="skillObservationsList" class="bg-darkbg p-3 rounded-xl border border-slate-800 text-[11px] mono text-slate-300 space-y-1 max-h-32 overflow-y-auto custom-scroll">
          <div>Carregando observações...</div>
        </div>
      </div>

      <div class="pt-2 flex items-center justify-between border-t border-bordercol text-[11px] text-slate-400">
        <span>Documento salvo: <b class="text-purple-300">SUPER_SKILL_APRENDIZADO.md</b></span>
        <button onclick="toggleSkillModal(false)" class="text-xs bg-purple-600 hover:bg-purple-500 text-white font-bold px-4 py-2 rounded-lg transition shadow">
          Fechar
        </button>
      </div>
    </div>
  </div>

  <!-- ==========================================
       MODAL INTELIGÊNCIA HISTÓRICA & BACKTEST 500 VELAS
       ========================================== -->
  <div id="historyModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-cardbg border border-blue-500/30 rounded-2xl max-w-2xl w-full p-6 space-y-4 shadow-2xl max-h-[85vh] overflow-y-auto custom-scroll">
      <div class="flex items-center justify-between border-b border-bordercol pb-3">
        <div class="flex items-center space-x-2.5 text-blue-400">
          <i class="fa-solid fa-chart-line text-xl"></i>
          <div>
            <h3 class="text-base font-bold text-white">Inteligência Histórica das Moedas (500 Velas / 21 Dias)</h3>
            <p class="text-[11px] text-slate-400">Backtest autônomo coletado diretamente da API oficial da Binance</p>
          </div>
        </div>
        <button onclick="toggleHistoryModal(false)" class="text-slate-400 hover:text-white p-1">
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>

      <p class="text-xs text-slate-300 leading-relaxed bg-darkbg p-3 rounded-xl border border-slate-800">
        💡 <b>Como o Robô Usa Esse Histórico:</b> O algoritmo avalia as últimas 500 horas de cada criptomoeda para identificar os suportes e resistências reais. <b>Ele bloqueia compras se a moeda estiver acima de 90% do topo histórico (evitando comprar na máxima)</b> e prioriza ativos com maior assertividade histórica do alvo de +2.0%!
      </p>

      <div class="overflow-x-auto custom-scroll">
        <table class="w-full text-left text-xs min-w-[500px]">
          <thead>
            <tr class="border-b border-bordercol text-slate-400 uppercase text-[11px]">
              <th class="py-2.5 px-3">Ativo</th>
              <th class="py-2.5 px-3">Win Rate Histórico (+2%)</th>
              <th class="py-2.5 px-3">Tempo Médio p/ Lucro</th>
              <th class="py-2.5 px-3">Suporte (21D)</th>
              <th class="py-2.5 px-3">Resistência (21D)</th>
              <th class="py-2.5 px-3 text-right">Posição no Range</th>
            </tr>
          </thead>
          <tbody id="historyPairsTable" class="divide-y divide-bordercol/60 font-medium">
            <tr>
              <td colspan="6" class="py-6 text-center text-slate-400">Carregando dados históricos da Binance...</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pt-2 flex items-center justify-between border-t border-bordercol text-[11px] text-slate-400">
        <a href="/api/export/excel" download class="text-xs bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-3 py-1.5 rounded-lg transition shadow flex items-center gap-1.5">
          <i class="fa-solid fa-file-excel"></i> Baixar Relatório Excel (.CSV)
        </a>
        <button onclick="toggleHistoryModal(false)" class="text-xs bg-blue-600 hover:bg-blue-500 text-white font-bold px-4 py-2 rounded-lg transition shadow">
          Fechar
        </button>
      </div>
    </div>
  </div>

  <!-- ==========================================
       MODAL CONTINGÊNCIA AMPLA DE MODELOS DE IA
       ========================================== -->
  <div id="aiModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-cardbg border border-purple-500/40 rounded-2xl max-w-2xl w-full p-6 space-y-4 shadow-2xl max-h-[85vh] overflow-y-auto custom-scroll">
      <div class="flex items-center justify-between border-b border-bordercol pb-3">
        <div class="flex items-center space-x-2.5 text-purple-400">
          <i class="fa-solid fa-server text-xl"></i>
          <div>
            <h3 class="text-base font-bold text-white">Cascata de Contingência de Modelos de IA (24/7)</h3>
            <p class="text-[11px] text-slate-400">Múltiplos provedores gratuitos com fallback infalível para zero downtime</p>
          </div>
        </div>
        <button onclick="toggleAiModal(false)" class="text-slate-400 hover:text-white p-1">
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>

      <div class="bg-purple-950/40 border border-purple-500/30 rounded-xl p-3 text-xs text-purple-200">
        🤖 <b>Como Funciona a Contingência:</b> O robô tenta os modelos na ordem abaixo a cada ciclo. Se a primeira API falhar, demorar mais de 4s ou atingir rate limit, ele salta instantaneamente para a próxima sem travar suas operações.
      </div>

      <div class="space-y-2.5" id="aiProvidersList">
        <div class="bg-darkbg p-3 rounded-xl border border-slate-800 flex items-center justify-between">
          <div class="space-y-0.5">
            <div class="font-bold text-white text-xs flex items-center gap-1.5">
              <span>1. Google Gemini 2.5 Flash</span>
              <span class="text-[10px] bg-blue-500/10 text-blue-400 px-1.5 py-0.2 rounded">Google AI Studio</span>
            </div>
            <div class="text-[11px] text-slate-400">Variável no Render: <code class="text-amber-400">GEMINI_API_KEY</code> | Grátis (15 RPM)</div>
          </div>
          <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400" id="statusGemini">Standby</span>
        </div>

        <div class="bg-darkbg p-3 rounded-xl border border-slate-800 flex items-center justify-between">
          <div class="space-y-0.5">
            <div class="font-bold text-white text-xs flex items-center gap-1.5">
              <span>2. Groq Cloud (Llama 3.3 70B)</span>
              <span class="text-[10px] bg-orange-500/10 text-orange-400 px-1.5 py-0.2 rounded">console.groq.com</span>
            </div>
            <div class="text-[11px] text-slate-400">Variável no Render: <code class="text-amber-400">GROQ_API_KEY</code> | Grátis (30 RPM, 250ms)</div>
          </div>
          <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400" id="statusGroq">Standby</span>
        </div>

        <div class="bg-darkbg p-3 rounded-xl border border-slate-800 flex items-center justify-between">
          <div class="space-y-0.5">
            <div class="font-bold text-white text-xs flex items-center gap-1.5">
              <span>3. OpenRouter (Llama 3.3 / DeepSeek :free)</span>
              <span class="text-[10px] bg-emerald-500/10 text-emerald-400 px-1.5 py-0.2 rounded">openrouter.ai</span>
            </div>
            <div class="text-[11px] text-slate-400">Variável no Render: <code class="text-amber-400">OPENROUTER_API_KEY</code> | Modelos Free</div>
          </div>
          <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400" id="statusOpenrouter">Standby</span>
        </div>

        <div class="bg-darkbg p-3 rounded-xl border border-slate-800 flex items-center justify-between">
          <div class="space-y-0.5">
            <div class="font-bold text-white text-xs flex items-center gap-1.5">
              <span>4. Cerebras Cloud (Llama 3.1 70B)</span>
              <span class="text-[10px] bg-cyan-500/10 text-cyan-400 px-1.5 py-0.2 rounded">cloud.cerebras.ai</span>
            </div>
            <div class="text-[11px] text-slate-400">Variável no Render: <code class="text-amber-400">CEREBRAS_API_KEY</code> | 1M tokens/dia Grátis</div>
          </div>
          <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400" id="statusCerebras">Standby</span>
        </div>

        <div class="bg-darkbg p-3 rounded-xl border border-slate-800 flex items-center justify-between">
          <div class="space-y-0.5">
            <div class="font-bold text-white text-xs flex items-center gap-1.5">
              <span>5. SambaNova Cloud (Llama 3.3 70B)</span>
              <span class="text-[10px] bg-rose-500/10 text-rose-400 px-1.5 py-0.2 rounded">cloud.sambanova.ai</span>
            </div>
            <div class="text-[11px] text-slate-400">Variável no Render: <code class="text-amber-400">SAMBANOVA_API_KEY</code> | Grátis Ultra-Rápido</div>
          </div>
          <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400" id="statusSambanova">Standby</span>
        </div>

        <div class="bg-darkbg p-3 rounded-xl border border-emerald-500/40 flex items-center justify-between">
          <div class="space-y-0.5">
            <div class="font-bold text-white text-xs flex items-center gap-1.5">
              <span>6. Motor Quantitativo Local (Heurístico)</span>
              <span class="text-[10px] bg-emerald-500/20 text-emerald-400 px-1.5 py-0.2 rounded font-bold">EMBUTIDO 24/7</span>
            </div>
            <div class="text-[11px] text-slate-400">Algoritmo matemático em Python | Zero Downtime, sem internet externa</div>
          </div>
          <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">ATIVO PERMANENTE</span>
        </div>
      </div>

      <div class="pt-2 flex items-center justify-between border-t border-bordercol text-[11px] text-slate-400">
        <span>Como ativar: configure a chave no Render em <b class="text-slate-200">Environment Variables</b></span>
        <button onclick="toggleAiModal(false)" class="text-xs bg-purple-600 hover:bg-purple-500 text-white font-bold px-4 py-2 rounded-lg transition shadow">
          Entendido
        </button>
      </div>
    </div>
  </div>

  <!-- ==========================================
       SCRIPTS FRONTEND (ATUALIZAÇÃO REATIVA & REGRAS NIELSEN)
       ========================================== -->
  <script>
    let countdown = 25;
    setInterval(() => {
      countdown = countdown > 1 ? countdown - 1 : 25;
      const el = document.getElementById('countdownTimer');
      if (el) el.innerText = `${countdown}s`;
    }, 1000);

    async function toggleAiModal(show) {
      document.getElementById('aiModal').classList.toggle('hidden', !show);
      if (show) {
        try {
          const res = await fetch('/api/ai_status');
          const data = await res.json();
          if (data && data.providers) {
            data.providers.forEach(p => {
              let elId = '';
              if (p.name.includes('Gemini')) elId = 'statusGemini';
              else if (p.name.includes('Groq')) elId = 'statusGroq';
              else if (p.name.includes('OpenRouter')) elId = 'statusOpenrouter';
              else if (p.name.includes('Cerebras')) elId = 'statusCerebras';
              else if (p.name.includes('SambaNova')) elId = 'statusSambanova';
              
              if (elId) {
                const el = document.getElementById(elId);
                if (el) {
                  if (p.configured) {
                    el.innerText = 'CONECTADO 🟢';
                    el.className = 'text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40';
                  } else {
                    el.innerText = 'Chave Ausente (Standby)';
                    el.className = 'text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400';
                  }
                }
              }
            });
          }
        } catch (e) {
          console.error(e);
        }
      }
    }

    function toggleResetModal(show) {
      document.getElementById('resetModal').classList.toggle('hidden', !show);
    }

    function toggleHelpModal(show) {
      document.getElementById('helpModal').classList.toggle('hidden', !show);
    }

    function toggleSkillModal(show) {
      document.getElementById('skillModal').classList.toggle('hidden', !show);
    }

    function toggleHistoryModal(show) {
      document.getElementById('historyModal').classList.toggle('hidden', !show);
    }

    function confirmReset() {
      toggleResetModal(true);
    }

    async function executeReset() {
      try {
        await fetch('/api/reset', { method: 'POST' });
        toggleResetModal(false);
        countdown = 25;
        await updateDashboard();
      } catch (err) {
        alert("Erro ao reiniciar: " + err);
      }
    }

    async function togglePause() {
      try {
        const res = await fetch('/api/toggle_pause', { method: 'POST' });
        const data = await res.json();
        updatePauseUI(data.is_paused);
        await updateDashboard();
      } catch (e) {
        console.error(e);
      }
    }

    function updatePauseUI(isPaused) {
      const btn = document.getElementById('btnPause');
      const icon = document.getElementById('pauseIcon');
      const label = document.getElementById('pauseLabel');
      if (isPaused) {
        btn.className = "text-xs bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 font-bold px-3 py-1.5 rounded-lg flex items-center space-x-1.5 transition";
        icon.className = "fa-solid fa-play";
        label.innerText = "Retomar";
      } else {
        btn.className = "text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold px-3 py-1.5 rounded-lg flex items-center space-x-1.5 transition";
        icon.className = "fa-solid fa-pause";
        label.innerText = "Pausar";
      }
    }

    function formatPrice(val, symbol) {
      if (val === undefined || val === null || isNaN(val)) return '--';
      const num = parseFloat(val);
      const isBrl = (symbol || '').toUpperCase().endsWith('BRL');
      const prefix = isBrl ? 'R$ ' : '$ ';
      if (num >= 1000) {
        return prefix + num.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      } else if (num >= 1) {
        return prefix + num.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 4 });
      } else {
        return prefix + num.toLocaleString('pt-BR', { minimumFractionDigits: 4, maximumFractionDigits: 6 });
      }
    }

    async function updateDashboard() {
      try {
        const res = await fetch('/api/state');
        if (!res.ok) return;
        const data = await res.json();

        // Latência & Scanner
        if (data.api_latency_ms) {
          document.getElementById('latencyBadge').innerHTML = `<i class="fa-solid fa-bolt text-amber-400 text-[10px]"></i> ${data.api_latency_ms}ms`;
        }
        if (data.total_pairs_market) {
          const pEl = document.getElementById('pairsCountText');
          if (pEl) pEl.innerText = `${data.total_pairs_market.toLocaleString('pt-BR')} Pares`;
        }

        // Estado de Pausa
        updatePauseUI(data.is_paused || false);

        // 1. Top Metrics & Taxas
        document.getElementById('totalEquity').innerText = `R$ ${data.total_equity_brl.toFixed(2)}`;
        document.getElementById('initialCapital').innerText = `R$ ${data.initial_capital_brl.toFixed(2)}`;
        document.getElementById('cashBalance').innerText = `R$ ${data.cash_balance_brl.toFixed(2)}`;
        
        const feesEl = document.getElementById('totalFeesPaid');
        if (feesEl) feesEl.innerText = `R$ ${(data.total_fees_paid_brl || 0).toFixed(3)}`;
        const feesF = document.getElementById('feesFooter');
        if (feesF) feesF.innerText = (data.total_fees_paid_brl || 0).toFixed(3);

        const profitBrl = data.accumulated_profit_brl || 0;
        const profitPct = data.profit_pct || 0;
        document.getElementById('profitBrl').innerText = `${profitBrl >= 0 ? '+' : ''}R$ ${profitBrl.toFixed(2)}`;
        
        const pEl = document.getElementById('profitPct');
        pEl.innerText = `${profitPct >= 0 ? '+' : ''}${profitPct.toFixed(2)}%`;
        pEl.className = profitPct >= 0 ? "text-[11px] font-bold text-emerald-400 mt-1 mono" : "text-[11px] font-bold text-rose-400 mt-1 mono";

        document.getElementById('winCountBadge').innerText = `${data.win_count || 0} Wins`;
        document.getElementById('macroStatus').innerHTML = data.last_macro_status || 'Em Análise...';
        document.getElementById('lastUpdate').innerText = data.last_update || '--';

        // 2. Raciocínio & Pensamento da IA
        const tEl = document.getElementById('currentThoughtText');
        if (tEl && data.current_thought) tEl.innerText = data.current_thought;
        const aiBadge = document.getElementById('activeAiBadge');
        if (aiBadge && data.active_ai_provider) {
          aiBadge.innerText = data.active_ai_provider;
        }
        const srcModel = document.getElementById('thoughtSourceModel');
        if (srcModel && data.active_ai_provider) {
          srcModel.innerText = data.active_ai_provider;
        }

        // 3. Tabela de Posições Abertas (Custódia Spot)
        const positions = data.open_positions || [];
        window.currentPositions = positions;
        document.getElementById('openCount').innerText = `${positions.length} ativa${positions.length === 1 ? '' : 's'}`;
        const pTable = document.getElementById('positionsTable');
        const mCards = document.getElementById('mobilePositionsCards');

        if (positions.length === 0) {
          if (pTable) pTable.innerHTML = `<tr><td colspan="9" class="py-6 text-center text-slate-400"><i class="fa-solid fa-magnifying-glass text-slate-500 mr-2"></i> Nenhuma posição aberta no momento. O robô está rastreando oportunidades em 15M, 1H e 4H.</td></tr>`;
          if (mCards) mCards.innerHTML = `
            <div class="p-6 text-center text-slate-400 bg-darkbg/60 rounded-xl border border-dashed border-slate-800">
              <i class="fa-solid fa-magnifying-glass text-slate-500 text-lg mb-2"></i>
              <p class="text-xs font-semibold text-slate-300">Nenhuma posição aberta no momento</p>
              <p class="text-[11px] text-slate-500 mt-1">O robô está rastreando oportunidades em 15M, 1H e 4H.</p>
            </div>
          `;
        } else {
          // Render Desktop Table
          if (pTable) {
            pTable.innerHTML = positions.map(pos => {
              const pnl = pos.current_pnl_pct || 0;
              const isProfit = pnl >= 0;
              const pnlClass = isProfit ? 'text-emerald-400 bg-emerald-500/10' : 'text-amber-400 bg-amber-500/10';
              const curPrice = pos.current_price || pos.entry_price;
              const tf = pos.timeframe || '1H';
              const tfBadge = tf === '15m' ? '<span class="bg-blue-500/20 text-blue-400 px-1.5 py-0.5 rounded font-bold text-[10px]">15m</span>' : (tf === '4H' ? '<span class="bg-purple-500/20 text-purple-400 px-1.5 py-0.5 rounded font-bold text-[10px]">4H</span>' : '<span class="bg-amber-500/20 text-amber-400 px-1.5 py-0.5 rounded font-bold text-[10px]">1H</span>');
              const feeBrl = pos.buy_fee_brl || (pos.stake_brl * 0.0015);

              return `
                <tr class="hover:bg-slate-800/40 transition">
                  <td class="py-2.5 px-3">${tfBadge}</td>
                  <td class="py-2.5 px-3">
                    <div class="font-bold text-white text-xs flex items-center gap-1.5">
                      <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                      ${pos.symbol}
                      ${pos.ml_score ? `<span class="bg-purple-500/20 text-purple-300 font-mono text-[9px] px-1 rounded font-bold" title="Score Machine Learning">ML ${pos.ml_score}%</span>` : ''}
                    </div>
                    <div class="text-[10px] text-slate-400">${pos.name || ''}</div>
                  </td>
                  <td class="py-2.5 px-3 text-slate-400 text-[11px]">${pos.entry_time}</td>
                  <td class="py-2.5 px-3 mono text-slate-300">${formatPrice(pos.entry_price, pos.symbol)}</td>
                  <td class="py-2.5 px-3 mono text-white font-bold transition-colors duration-300" id="livePrice_${pos.symbol}">${formatPrice(curPrice, pos.symbol)}</td>
                  <td class="py-2.5 px-3 mono text-emerald-400 font-semibold">${formatPrice(pos.target_price, pos.symbol)} <span class="text-[10px] text-emerald-500">(+2%)</span></td>
                  <td class="py-2.5 px-3">
                    <span id="livePnl_${pos.symbol}" class="px-2 py-0.5 rounded font-mono font-bold text-[11px] transition-all duration-300 ${pnlClass}">
                      ${isProfit ? '+' : ''}${pnl.toFixed(2)}%
                    </span>
                  </td>
                  <td class="py-2.5 px-3 mono text-slate-400 text-[11px]">R$ ${feeBrl.toFixed(3)}</td>
                  <td class="py-2.5 px-3 mono text-right font-bold text-slate-100">
                    R$ ${pos.stake_brl.toFixed(2)}
                  </td>
                </tr>
              `;
            }).join('');
          }

          // Render Mobile Cards
          if (mCards) {
            mCards.innerHTML = positions.map(pos => {
              const pnl = pos.current_pnl_pct || 0;
              const isProfit = pnl >= 0;
              const pnlClass = isProfit ? 'text-emerald-400 bg-emerald-500/15 border border-emerald-500/30' : 'text-amber-400 bg-amber-500/15 border border-amber-500/30';
              const curPrice = pos.current_price || pos.entry_price;
              const tf = pos.timeframe || '1H';
              const tfBadge = tf === '15m' ? '<span class="bg-blue-500/20 text-blue-400 px-1.5 py-0.5 rounded font-bold text-[10px]">15m</span>' : (tf === '4H' ? '<span class="bg-purple-500/20 text-purple-400 px-1.5 py-0.5 rounded font-bold text-[10px]">4H</span>' : '<span class="bg-amber-500/20 text-amber-400 px-1.5 py-0.5 rounded font-bold text-[10px]">1H</span>');
              const feeBrl = pos.buy_fee_brl || (pos.stake_brl * 0.0015);

              return `
                <div class="bg-darkbg/90 border border-slate-800 rounded-xl p-3 space-y-2.5 shadow-md">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-1.5">
                      <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                      <span class="font-extrabold text-white text-sm tracking-wide">${pos.symbol}</span>
                      ${tfBadge}
                      ${pos.ml_score ? `<span class="bg-purple-500/20 text-purple-300 font-mono text-[9px] px-1.5 py-0.5 rounded font-bold border border-purple-500/30">ML ${pos.ml_score}%</span>` : ''}
                    </div>
                    <span id="livePnlMob_${pos.symbol}" class="px-2.5 py-1 rounded-lg font-mono font-black text-xs ${pnlClass} shadow-sm">
                      ${isProfit ? '+' : ''}${pnl.toFixed(2)}%
                    </span>
                  </div>

                  <div class="grid grid-cols-2 gap-2 text-xs pt-1 border-t border-slate-800/80">
                    <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800/90">
                      <div class="text-[10px] text-slate-400 font-medium">Preço Compra</div>
                      <div class="font-mono text-slate-200 font-semibold mt-0.5 text-[11px]">${formatPrice(pos.entry_price, pos.symbol)}</div>
                    </div>
                    <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800/90">
                      <div class="text-[10px] text-slate-400 font-medium flex items-center justify-between">
                        <span>Cotação (1s)</span>
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                      </div>
                      <div class="font-mono text-white font-black mt-0.5 text-[11px]" id="livePriceMob_${pos.symbol}">${formatPrice(curPrice, pos.symbol)}</div>
                    </div>
                    <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800/90">
                      <div class="text-[10px] text-slate-400 font-medium">Alvo Lucro (+2%)</div>
                      <div class="font-mono text-emerald-400 font-bold mt-0.5 text-[11px]">${formatPrice(pos.target_price, pos.symbol)}</div>
                    </div>
                    <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800/90">
                      <div class="text-[10px] text-slate-400 font-medium">Investido / Taxa</div>
                      <div class="font-mono text-slate-200 mt-0.5 font-semibold text-[11px]">R$ ${pos.stake_brl.toFixed(2)} <span class="text-[10px] text-slate-500">(${feeBrl.toFixed(2)})</span></div>
                    </div>
                  </div>

                  <div class="flex items-center justify-between text-[10px] text-slate-400 pt-0.5">
                    <span>Entrada: <b class="text-slate-300 font-mono">${pos.entry_time}</b></span>
                    <span class="text-emerald-400 font-semibold flex items-center gap-1">
                      <i class="fa-solid fa-shield-halved text-[9px]"></i> Spot 100% Protegido
                    </span>
                  </div>
                </div>
              `;
            }).join('');
          }
        }

        // 4. Histórico de Trades Fechados
        const closed = data.closed_trades || [];
        document.getElementById('closedCount').innerText = `${closed.length} finalizada${closed.length === 1 ? '' : 's'}`;
        const hTable = document.getElementById('historyTable');

        if (closed.length === 0) {
          hTable.innerHTML = `<tr><td colspan="4" class="py-6 text-center text-slate-400">Ainda não há operações fechadas. As posições estão em andamento.</td></tr>`;
        } else {
          hTable.innerHTML = closed.slice(-15).reverse().map(trade => `
            <tr class="hover:bg-slate-800/40 transition">
              <td class="py-2 px-2 font-bold text-white">${trade.symbol} <span class="text-[9px] text-slate-500">(${trade.timeframe || '1H'})</span></td>
              <td class="py-2 px-2 text-slate-400 text-[11px]">${trade.exit_time}</td>
              <td class="py-2 px-2 font-bold text-emerald-400 mono">+${trade.profit_pct}%</td>
              <td class="py-2 px-2 text-right font-bold text-emerald-400 mono">+R$ ${(trade.net_profit_brl || trade.profit_brl).toFixed(2)}</td>
            </tr>
          `).join('');
        }

        // 5. Card de Logs de Tudo o que Está Acontecendo
        const dLogs = data.detailed_logs || [];
        const dConsole = document.getElementById('detailedLogConsole');
        if (dConsole) {
          if (dLogs.length === 0 && data.activity_logs) {
            dConsole.innerHTML = data.activity_logs.map(l => `<div class="leading-relaxed text-slate-300">${l}</div>`).join('');
          } else {
            dConsole.innerHTML = dLogs.map(l => {
              let badgeColor = 'bg-slate-800 text-slate-300';
              if (l.type === 'COMPRA_EXECUTADA') badgeColor = 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
              else if (l.type === 'TAKE_PROFIT') badgeColor = 'bg-amber-500/20 text-amber-400 border border-amber-500/30';
              else if (l.type === 'ML_BLOCK') badgeColor = 'bg-purple-500/20 text-purple-300 border border-purple-500/30';
              else if (l.type === 'RISK_BLOCK' || l.type === 'FILTRO_HISTORICO') badgeColor = 'bg-rose-500/20 text-rose-400 border border-rose-500/30';
              else if (l.type === 'MACRO_DEFESA') badgeColor = 'bg-blue-500/20 text-blue-400 border border-blue-500/30';
              return `
                <div class="flex items-start space-x-2 py-0.5 hover:bg-slate-900/60 rounded px-1 transition text-[11px]">
                  <span class="text-slate-500 shrink-0 mt-0.5 font-mono">[${l.time}]</span>
                  <span class="shrink-0 text-[9px] font-bold px-1.5 py-0.2 rounded font-mono ${badgeColor}">${l.type}</span>
                  <span class="text-slate-200">${l.msg}</span>
                </div>
              `;
            }).join('');
          }
        }

        // 5. Super Skill Brain
        if (data.super_skill) {
          const sk = data.super_skill;
          const badge = document.getElementById('skillBadge');
          if (badge) badge.innerText = `Super Skill (Nv. ${sk.brain_level || 1})`;
          const lvlEl = document.getElementById('skillLevel');
          if (lvlEl) lvlEl.innerText = `Nível ${sk.brain_level || 1}`;
          const titleEl = document.getElementById('skillTitle');
          if (titleEl) titleEl.innerText = sk.level_title || 'Analista Júnior';
          const hrsEl = document.getElementById('skillHours');
          if (hrsEl) hrsEl.innerText = `${sk.hours_studied || 0.1}h`;
          const cycEl = document.getElementById('skillCycles');
          if (cycEl) cycEl.innerText = `${sk.total_cycles_studied || 0} ciclos`;

          const lList = document.getElementById('skillLearningsList');
          if (lList && sk.key_learnings) {
            lList.innerHTML = sk.key_learnings.map(k => `
              <div class="bg-darkbg p-2.5 rounded-lg border border-slate-800">
                <div class="flex items-center justify-between">
                  <b class="text-white">${k.title}</b>
                  <span class="text-[10px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded font-bold">${k.status}</span>
                </div>
                <p class="text-slate-300 text-[11px] mt-1">${k.insight}</p>
                <div class="text-[10px] text-amber-400 mt-1">Confiança: <b>${k.confidence}</b></div>
              </div>
            `).join('');
          }

          const obsList = document.getElementById('skillObservationsList');
          if (obsList && sk.last_observations) {
            obsList.innerHTML = sk.last_observations.map(o => `<div>${o}</div>`).join('') || '<div>Aguardando leituras...</div>';
          }
        }

        // 6. Inteligência Histórica (500 Velas)
        if (data.historical_analysis) {
          const hMap = data.historical_analysis;
          const hTable = document.getElementById('historyPairsTable');
          const keys = Object.keys(hMap);
          if (hTable && keys.length > 0) {
            hTable.innerHTML = keys.map(k => {
              const item = hMap[k];
              const pos = item.range_position_pct || 50;
              const posColor = pos < 50 ? 'bg-emerald-500' : (pos < 80 ? 'bg-amber-500' : 'bg-rose-500');
              const posText = pos < 50 ? 'Zona de Suporte 🟢' : (pos < 80 ? 'Meio de Range 🟡' : 'Resistência 🛑');
              return `
                <tr class="hover:bg-slate-800/40 transition">
                  <td class="py-2.5 px-3">
                    <div class="font-bold text-white">${k}</div>
                    <div class="text-[10px] text-slate-400">${item.name || ''}</div>
                  </td>
                  <td class="py-2.5 px-3 mono font-bold text-emerald-400">
                    ${item.historical_win_rate_pct}% <span class="text-[10px] text-slate-400">(${item.wins_count}/${item.signals_tested})</span>
                  </td>
                  <td class="py-2.5 px-3 mono text-slate-300">~${item.avg_hours_to_tp}h</td>
                  <td class="py-2.5 px-3 mono text-slate-300">${formatPrice(item.support_price, k)}</td>
                  <td class="py-2.5 px-3 mono text-slate-300">${formatPrice(item.resistance_price, k)}</td>
                  <td class="py-2.5 px-3 text-right">
                    <div class="flex items-center justify-end gap-1.5">
                      <span class="mono text-[11px] text-slate-300 font-bold">${pos}%</span>
                      <div class="w-12 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div class="${posColor} h-full" style="width: ${pos}%"></div>
                      </div>
                    </div>
                    <div class="text-[9px] text-slate-400">${posText}</div>
                  </td>
                </tr>
              `;
            }).join('');
          }
        }

      } catch (err) {
        console.error("Erro ao sincronizar dashboard:", err);
      }
    }

    async function triggerScan() {
      const btn = document.getElementById('btnScan');
      const icon = document.getElementById('scanIcon');
      icon.classList.add('fa-spin');
      btn.disabled = true;
      try {
        await fetch('/api/scan', { method: 'POST' });
        countdown = 25;
        await updateDashboard();
      } catch (e) {
        console.error(e);
      } finally {
        setTimeout(() => {
          icon.classList.remove('fa-spin');
          btn.disabled = false;
        }, 1200);
      }
    }

    // ==========================================
    // COTAÇÕES E PORCENTAGENS EM TEMPO REAL (1 SEGUNDO DIRETO DA BINANCE)
    // ==========================================
    let livePrices = {};
    let previousPrices = {};

    async function updateLiveTicker() {
      if (!window.currentPositions || window.currentPositions.length === 0) return;
      const symbols = [...new Set(window.currentPositions.map(p => p.symbol))];
      try {
        const formatted = encodeURIComponent(JSON.stringify(symbols));
        const res = await fetch(`https://api.binance.com/api/v3/ticker/price?symbols=${formatted}`);
        if (!res.ok) return;
        const items = await res.json();
        
        items.forEach(t => {
          const sym = t.symbol;
          const newPrice = parseFloat(t.price);
          if (livePrices[sym]) previousPrices[sym] = livePrices[sym];
          else previousPrices[sym] = newPrice;
          livePrices[sym] = newPrice;
        });

        window.currentPositions.forEach(pos => {
          const sym = pos.symbol;
          const curPrice = livePrices[sym];
          if (!curPrice) return;
          
          const entryPrice = pos.entry_price;
          const pnl = ((curPrice - entryPrice) / entryPrice) * 100;
          const isProfit = pnl >= 0;
          
          const formatted = formatPrice(curPrice, sym);
          const pnlText = `${isProfit ? '+' : ''}${pnl.toFixed(2)}%`;
          
          // Desktop elements
          const priceEl = document.getElementById(`livePrice_${sym}`);
          const pnlEl = document.getElementById(`livePnl_${sym}`);
          
          // Mobile elements
          const priceMobEl = document.getElementById(`livePriceMob_${sym}`);
          const pnlMobEl = document.getElementById(`livePnlMob_${sym}`);
          
          if (priceEl) {
            priceEl.innerText = formatted;
            if (curPrice > previousPrices[sym]) {
              priceEl.classList.add('text-emerald-400');
              setTimeout(() => priceEl.classList.remove('text-emerald-400'), 450);
            } else if (curPrice < previousPrices[sym]) {
              priceEl.classList.add('text-rose-400');
              setTimeout(() => priceEl.classList.remove('text-rose-400'), 450);
            }
          }

          if (priceMobEl) {
            priceMobEl.innerText = formatted;
            if (curPrice > previousPrices[sym]) {
              priceMobEl.classList.add('text-emerald-400');
              setTimeout(() => priceMobEl.classList.remove('text-emerald-400'), 450);
            } else if (curPrice < previousPrices[sym]) {
              priceMobEl.classList.add('text-rose-400');
              setTimeout(() => priceMobEl.classList.remove('text-rose-400'), 450);
            }
          }
          
          if (pnlEl) {
            pnlEl.innerText = pnlText;
            pnlEl.className = `px-2 py-0.5 rounded font-mono font-bold text-[11px] transition-all duration-300 ${isProfit ? 'text-emerald-400 bg-emerald-500/10' : 'text-amber-400 bg-amber-500/10'}`;
          }

          if (pnlMobEl) {
            pnlMobEl.innerText = pnlText;
            pnlMobEl.className = `px-2.5 py-1 rounded-lg font-mono font-black text-xs transition-all duration-300 ${isProfit ? 'text-emerald-400 bg-emerald-500/15 border border-emerald-500/30' : 'text-amber-400 bg-amber-500/15 border border-amber-500/30'}`;
          }
        });
      } catch (err) {
        // Silencioso em caso de falha transitória
      }
    }

    // ==========================================
    // PWA (PROGRESSIVE WEB APP) & REGISTRO SERVICE WORKER
    // ==========================================
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch(err => console.log('SW fail:', err));
      });
    }

    let deferredPrompt = null;
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      const banner = document.getElementById('pwaInstallBanner');
      if (banner && !localStorage.getItem('pwa_dismissed')) {
        banner.classList.remove('hidden');
      }
    });

    // Se estiver em mobile e não tiver dispensado, mostra banner de sugestão após 2.5s
    setTimeout(() => {
      const banner = document.getElementById('pwaInstallBanner');
      if (banner && !localStorage.getItem('pwa_dismissed') && window.innerWidth < 768) {
        banner.classList.remove('hidden');
      }
    }, 2500);

    function installPWA() {
      const isIos = /iPhone|iPad|iPod/i.test(navigator.userAgent);
      if (isIos) {
        alert("📲 Como Instalar o BITLUCRO no iPhone (Safari):\\n\\n1. Toque no botão 'Compartilhar' (ícone de quadrado com seta para cima no Safari).\\n2. Role para baixo e selecione 'Adicionar à Tela de Início'.\\n3. Toque em 'Adicionar' no canto superior direito.\\n\\nPronto! O ícone do BITLUCRO aparecerá na tela inicial como um app nativo.");
        return;
      }
      if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
          if (choiceResult.outcome === 'accepted') {
            const banner = document.getElementById('pwaInstallBanner');
            if (banner) banner.classList.add('hidden');
          }
          deferredPrompt = null;
        });
      } else {
        alert("📲 Instalar no Celular:\\n\\nToque no menu (três pontinhos) do seu navegador e escolha 'Instalar aplicativo' ou 'Adicionar à tela inicial'.");
      }
    }

    function dismissPWABanner() {
      const banner = document.getElementById('pwaInstallBanner');
      if (banner) banner.classList.add('hidden');
      localStorage.setItem('pwa_dismissed', 'true');
    }

    setInterval(updateDashboard, 4000);
    setInterval(updateLiveTicker, 1000);
    updateDashboard();
  </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_DASHBOARD)

@app.route('/api/state')
def get_state():
    state = engine.state.copy()
    state["activity_logs"] = activity_logs
    if hasattr(engine, 'brain'):
        state["super_skill"] = engine.brain.state
    return jsonify(state)

@app.route('/api/skill')
def get_skill():
    return jsonify(engine.brain.state)

@app.route('/api/historical')
def get_historical():
    return jsonify(engine.historical_analyzer.data)

@app.route('/api/ai_status')
def get_ai_status():
    return jsonify({
        "active_provider": engine.ai_contingency.active_provider,
        "providers": engine.ai_contingency.get_providers_status()
    })

@app.route('/api/export/excel')
@app.route('/api/export/csv')
def export_excel():
    try:
        csv_data = engine.generate_export_csv()
        filename = f"BITLUCRO_Relatorio_Quant_IA_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return Response(
            csv_data,
            mimetype="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/csv; charset=utf-8"
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/scan', methods=['POST'])
def manual_scan():
    try:
        add_log("Escaneamento manual acionado pelo operador no Dashboard.")
        engine.run_cycle()
        return jsonify({"status": "success", "message": "Ciclo executado com sucesso!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/toggle_pause', methods=['POST'])
def toggle_pause():
    is_paused = engine.toggle_pause()
    msg = "Operações de novas compras PAUSADAS." if is_paused else "Operações de compras RETOMADAS."
    add_log(msg)
    return jsonify({"status": "success", "is_paused": is_paused, "message": msg})

@app.route('/api/reset', methods=['POST'])
def reset_simulation():
    engine.reset_simulation()
    add_log("Simulador reiniciado. Banca restaurada para R$ 50,00.")
    return jsonify({"status": "success", "message": "Simulação restaurada para R$ 50,00."})

@app.route('/health')
def health():
    return jsonify({
        "status": "UP",
        "service": "BITLUCRO Binance Spot Bot",
        "time": datetime.now().isoformat(),
        "total_equity_brl": engine.state.get("total_equity_brl", 50.0),
        "is_paused": engine.state.get("is_paused", False)
    })

@app.route('/manifest.json')
def pwa_manifest():
    manifest_data = {
        "name": "BITLUCRO - Robô Spot 24/7",
        "short_name": "BITLUCRO",
        "description": "Dashboard do Robô Quantitativo Binance Spot 24/7",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0B0E14",
        "theme_color": "#0B0E14",
        "orientation": "portrait-primary",
        "icons": [
            {
                "src": "https://cdn-icons-png.flaticon.com/512/5968/5968260.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "https://cdn-icons-png.flaticon.com/512/5968/5968260.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ]
    }
    return jsonify(manifest_data)

@app.route('/sw.js')
def service_worker():
    sw_code = """
    const CACHE_NAME = 'bitlucro-pwa-v1';
    self.addEventListener('install', (e) => {
        self.skipWaiting();
    });
    self.addEventListener('activate', (e) => {
        e.waitUntil(clients.claim());
    });
    self.addEventListener('fetch', (e) => {
        e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
    });
    """
    return Response(sw_code, mimetype="application/javascript")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 BITLUCRO rodando na porta {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
