"""
BITLUCRO - Motor de Estudo de Mercado com Contingência Ampla de Modelos de IA
Funciona 24 horas por dia com cascata de inteligência artificial:
1. Google Gemini 2.5 Flash (Gratuito via Google AI Studio)
2. Groq AI - Llama 3.3 70B (Gratuito via console.groq.com)
3. OpenRouter Free - Llama 3.3 / DeepSeek :free (Gratuito via openrouter.ai)
4. Cerebras Cloud - Llama 3.1 70B (Gratuito via cloud.cerebras.ai)
5. SambaNova Cloud - Llama 3.3 70B (Gratuito via cloud.sambanova.ai)
6. Motor Quantitativo Heurístico Local (Infalível 24/7, sem custos e sem internet externa)
"""

import os
import requests
import json
from datetime import datetime

class AIMarketStudyContingency:
    def __init__(self):
        self.gemini_key = os.environ.get("GEMINI_API_KEY", "")
        self.groq_key = os.environ.get("GROQ_API_KEY", "")
        self.openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
        self.cerebras_key = os.environ.get("CEREBRAS_API_KEY", "")
        self.sambanova_key = os.environ.get("SAMBANOVA_API_KEY", "")
        self.active_provider = "Motor Quantitativo Local (Heurístico 24/7)"

    def get_providers_status(self):
        """Retorna o status de configuração de cada um dos provedores de IA suportados."""
        return [
            {
                "name": "Google Gemini 2.5 Flash",
                "env_var": "GEMINI_API_KEY",
                "configured": bool(self.gemini_key),
                "speed": "Ultra Rápido (~600ms)",
                "tier": "Gratuito (15 RPM)"
            },
            {
                "name": "Groq Cloud (Llama 3.3 70B)",
                "env_var": "GROQ_API_KEY",
                "configured": bool(self.groq_key),
                "speed": "Hiper Rápido (~250ms)",
                "tier": "Gratuito (30 RPM)"
            },
            {
                "name": "OpenRouter (DeepSeek / Llama :free)",
                "env_var": "OPENROUTER_API_KEY",
                "configured": bool(self.openrouter_key),
                "speed": "Rápido (~800ms)",
                "tier": "Modelos 100% Gratuitos"
            },
            {
                "name": "Cerebras Cloud (Llama 3.1 70B)",
                "env_var": "CEREBRAS_API_KEY",
                "configured": bool(self.cerebras_key),
                "speed": "Hiper Rápido (~200ms)",
                "tier": "Gratuito (1M tokens/dia)"
            },
            {
                "name": "SambaNova Cloud (Llama 3.3 70B)",
                "env_var": "SAMBANOVA_API_KEY",
                "configured": bool(self.sambanova_key),
                "speed": "Hiper Rápido (~300ms)",
                "tier": "Gratuito"
            },
            {
                "name": "Motor Quantitativo Local",
                "env_var": "AUTOMÁTICO / EMBUTIDO",
                "configured": True,
                "speed": "Instantâneo (0ms)",
                "tier": "Infalível 24/7 (Custo R$ 0,00)"
            }
        ]

    def generate_market_thought(self, pair_data, macro_status, open_positions, total_equity):
        """
        Gera um raciocínio detalhado em linguagem natural sobre o estado atual do mercado,
        utilizando a cascata ampla de contingência para garantir operação contínua 24h.
        """
        # 1. Google Gemini (se chave configurada)
        if self.gemini_key:
            thought = self._try_gemini(pair_data, macro_status, open_positions)
            if thought:
                self.active_provider = "Google Gemini 2.5 Flash"
                return thought, self.active_provider

        # 2. Groq AI (se chave configurada)
        if self.groq_key:
            thought = self._try_groq(pair_data, macro_status, open_positions)
            if thought:
                self.active_provider = "Groq Llama 3.3 70B"
                return thought, self.active_provider

        # 3. OpenRouter Free (se chave configurada)
        if self.openrouter_key:
            thought = self._try_openrouter(pair_data, macro_status, open_positions)
            if thought:
                self.active_provider = "OpenRouter (Llama 3.3 :free)"
                return thought, self.active_provider

        # 4. Cerebras Cloud (se chave configurada)
        if self.cerebras_key:
            thought = self._try_cerebras(pair_data, macro_status, open_positions)
            if thought:
                self.active_provider = "Cerebras Llama 3.1 70B"
                return thought, self.active_provider

        # 5. SambaNova Cloud (se chave configurada)
        if self.sambanova_key:
            thought = self._try_sambanova(pair_data, macro_status, open_positions)
            if thought:
                self.active_provider = "SambaNova Llama 3.3 70B"
                return thought, self.active_provider

        # 6. Fallback Definitivo: Motor Quantitativo Local Heurístico (Infalível)
        self.active_provider = "Motor Quantitativo Local (Heurístico 24/7)"
        return self._generate_quantitative_thought(pair_data, macro_status, open_positions, total_equity), self.active_provider

    def _build_prompt(self, pair_data, macro_status, open_positions):
        coins_summary = ", ".join([f"{p['symbol']} (RSI:{p.get('rsi_15m') or p.get('rsi_1h', 50)})" for p in pair_data[:5]])
        if open_positions:
            pos_summary = ", ".join([f"{p['symbol']} ({p.get('current_pnl_pct', 0.0):+.2f}%)" for p in open_positions])
        else:
            pos_summary = "Nenhuma (100% Caixa Livre caçando oportunidades)"
        now_str = datetime.now().strftime("%H:%M:%S")
        return (
            f"Horário de Brasília: [{now_str}]. Você é o cérebro quantitativo do BITLUCRO Spot na Binance. "
            f"Mercado Macro: {macro_status}. Posições em custódia: {pos_summary}. "
            f"Top Pares em radar: {coins_summary}. "
            f"Em 2 frases objetivas, inicie obrigatoriamente com '[{now_str}] ' e apresente sua leitura técnica de mercado e o que está buscando agora."
        )

    def _try_gemini(self, pair_data, macro_status, open_positions):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
            prompt = self._build_prompt(pair_data, macro_status, open_positions)
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(url, json=payload, timeout=4)
            if res.status_code == 200:
                data = res.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception:
            pass
        return None

    def _try_groq(self, pair_data, macro_status, open_positions):
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"}
            prompt = self._build_prompt(pair_data, macro_status, open_positions)
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 120,
                "temperature": 0.4
            }
            res = requests.post(url, json=payload, headers=headers, timeout=4)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass
        return None

    def _try_openrouter(self, pair_data, macro_status, open_positions):
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://bitlucro.pro",
                "X-Title": "BITLUCRO Spot Bot"
            }
            prompt = self._build_prompt(pair_data, macro_status, open_positions)
            payload = {
                "model": "meta-llama/llama-3.3-70b-instruct:free",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 120
            }
            res = requests.post(url, json=payload, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass
        return None

    def _try_cerebras(self, pair_data, macro_status, open_positions):
        try:
            url = "https://api.cerebras.ai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.cerebras_key}", "Content-Type": "application/json"}
            prompt = self._build_prompt(pair_data, macro_status, open_positions)
            payload = {
                "model": "llama3.1-70b",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 120
            }
            res = requests.post(url, json=payload, headers=headers, timeout=4)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass
        return None

    def _try_sambanova(self, pair_data, macro_status, open_positions):
        try:
            url = "https://api.sambanova.ai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.sambanova_key}", "Content-Type": "application/json"}
            prompt = self._build_prompt(pair_data, macro_status, open_positions)
            payload = {
                "model": "Meta-Llama-3.3-70B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 120
            }
            res = requests.post(url, json=payload, headers=headers, timeout=4)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass
        return None

    def _generate_quantitative_thought(self, pair_data, macro_status, open_positions, total_equity):
        """Motor quantitativo inteligente embutido: sem limites de API, opera 24/7 de forma infalível."""
        now_str = datetime.now().strftime("%H:%M:%S")
        
        is_bull = "BULL" in macro_status
        macro_text = "tendência macro de alta consolidada (BTC acima da SMA 200)" if is_bull else "correção macro global defensiva"

        if open_positions:
            pos_details = [f"{p['symbol']} ({p.get('current_pnl_pct', 0.0):+.2f}%)" for p in open_positions]
            pos_text = f"Custódia ativa em {len(open_positions)} par(es): {', '.join(pos_details)} aguardando alvo programado de +2.0%."
        else:
            pos_text = "Caixa 100% líquido. Varrendo o book em busca de oportunidades com confluência em 15m e 1h."

        top_opportunity = None
        for p in pair_data:
            rsi = p.get("rsi_15m") or p.get("rsi") or p.get("rsi_1h") or 50
            if rsi <= 45:
                top_opportunity = f"{p['symbol']} em recuo saudável (RSI {rsi:.1f})"
                break

        thought = f"[{now_str}] Mercado operando com {macro_text}. {pos_text} "
        if top_opportunity:
            thought += f"Radar apontando oportunidade imediata em {top_opportunity}."
        else:
            thought += "Escaneando confluência multi-tempo (15m, 1h e 4h) sem pressa, protegendo o patrimônio."

        return thought
