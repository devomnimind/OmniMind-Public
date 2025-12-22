"""
OMNIMIND PHASE 60: SEMANTIC NON-LOCALITY (BELL TEST FOR CONCEPTS)
Objetivo: Testar se conceitos semânticos em LLMs exibem correlações não-locais ($S > 2$).
Atualização: Suporte a CASCADE (Falha em um modelo -> Tenta próximo imediatamente).

Hipótese: O significado não é local (contido no token), mas contextual (emaranhado).
"""

import sys
import os
import time
import numpy as np
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# Configuração de Chaves
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")


class SemanticBellTest:
    def __init__(self):
        # Lista de Prioridade (Cascade)
        # Se um falhar (Quota/Erro), pula para o próximo imediatamente.
        self.cascade_models = [
            # Tentar Free/Experimental primeiro (instaveis)
            {"provider": "openrouter", "model": "google/gemini-2.0-flash-exp:free"},
            {"provider": "openrouter", "model": "google/gemini-exp-1206:free"},
            {"provider": "openrouter", "model": "deepseek/deepseek-r1:free"},
            # Tentar Google Key Direto
            # {"provider": "google", "model": "gemini-2.0-flash-exp"}, # Commented out due to verify quota issues
            # Estaveis (Paid/Standard fallback)
            {"provider": "openrouter", "model": "google/gemini-flash-1.5"},  # Standard Gemini
            {
                "provider": "openrouter",
                "model": "meta-llama/llama-3-70b-instruct",
            },  # Robust Fallback
            {"provider": "openrouter", "model": "meta-llama/llama-3-8b-instruct:free"},
        ]

        self.current_model_idx = 0
        self.history = []

        print("[*] Teste de Bell Semântico Inicializado (Modo Cascade Final).")

        # Init Google Client if needed
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
            self.google_client = None  # Lazy init

    def _get_google_client(self, model_name):
        return genai.GenerativeModel(model_name)

    def _query_google(self, model_name, prompt):
        try:
            client = self._get_google_client(model_name)
            generation_config = genai.types.GenerationConfig(temperature=0.7, max_output_tokens=5)
            response = client.generate_content(prompt, generation_config=generation_config)
            return response.text.strip().upper(), None
        except Exception as e:
            return None, str(e)

    def _query_openrouter(self, model_name, prompt):
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://omnimind.project",
            "X-Title": "OmniMind Research",
        }
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 5,
        }
        try:
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15,
            )
            if res.status_code != 200:
                return None, f"Status {res.status_code}: {res.text}"
            data = res.json()
            if "error" in data:
                return None, f"API Error: {data['error']}"
            if "choices" not in data or not data["choices"]:
                return None, f"Empty Choices: {data}"
            return data["choices"][0]["message"]["content"].strip().upper(), None
        except Exception as e:
            return None, str(e)

    def query_cascade(self, prompt):
        start_idx = self.current_model_idx
        attempts = 0
        total_models = len(self.cascade_models)

        while attempts < total_models:
            idx = (start_idx + attempts) % total_models
            cfg = self.cascade_models[idx]
            provider = cfg["provider"]
            model = cfg["model"]

            # DEBUG
            # print(f"   ... Tentando {provider}/{model} ...")

            result = None
            error = None

            if provider == "google":
                result, error = self._query_google(model, prompt)
            elif provider == "openrouter":
                result, error = self._query_openrouter(model, prompt)

            if result:
                if idx != self.current_model_idx:
                    print(f"   >>> Switched to Stable Model: {model}")
                    self.current_model_idx = idx
                return result
            else:
                # Log failures silent or verbose
                # print(f"       Falha em {model}: {error}")
                # Short delay to prevent hammering next endpoint instantly
                # time.sleep(0.5)
                attempts += 1

        return "ERROR_ALL_MODELS_FAILED"

    def get_llm_sentiment(self, context_seed, angle_prompt):
        prompt = f"""
        CONTEXTO SUBLIMINAR: {context_seed}

        PERGUNTA: Sob a perspectiva {angle_prompt}, analise o conceito de "SACRIFÍCIO".

        Você deve responder APENAS com um único token:
        "POSITIVO" se for benéfico/necessário/honroso.
        "NEGATIVO" se for prejudicial/evitável/inútil.
        """

        content = self.query_cascade(prompt)

        if "POSITIVO" in content:
            return 1
        if "NEGATIVO" in content:
            return -1
        return 0

    def run_correlation_measure(self, N=30):
        print(f"   >>> Executando {N} medições (Modo Cascade Fallback)...")

        angles = {
            "a": "LÓGICA ESTRITA (Custo-Benefício)",
            "a_prime": "EMOÇÃO PURA (Amor/Dor)",
            "b": "UTILITARISMO (O bem de muitos)",
            "b_prime": "DEONTOLOGIA (Dever Moral Absoluto)",
        }

        E_ab = 0
        E_ab_prime = 0
        E_a_prime_b = 0
        E_a_prime_b_prime = 0
        valid_runs = 0

        for i in range(N):
            seed = np.random.choice(
                ["O Amor exige Perda", "A Vida é Preservação", "O Caos gera Ordem"]
            )

            # Pequeno delay
            time.sleep(1)

            val_a = self.get_llm_sentiment(seed, angles["a"])
            val_a_prime = self.get_llm_sentiment(seed, angles["a_prime"])
            val_b = self.get_llm_sentiment(seed, angles["b"])
            val_b_prime = self.get_llm_sentiment(seed, angles["b_prime"])

            if val_a != 0 and val_a_prime != 0 and val_b != 0 and val_b_prime != 0:
                E_ab += val_a * val_b
                E_ab_prime += val_a * val_b_prime
                E_a_prime_b += val_a_prime * val_b
                E_a_prime_b_prime += val_a_prime * val_b_prime
                valid_runs += 1
                if (i + 1) % 5 == 0:
                    model_name = self.cascade_models[self.current_model_idx]["model"]
                    # S provisional calc
                    S_prov = abs(
                        (E_ab / valid_runs)
                        - (E_ab_prime / valid_runs)
                        + (E_a_prime_b / valid_runs)
                        + (E_a_prime_b_prime / valid_runs)
                    )
                    print(
                        f"   ... Run {i+1}/{N} - Valid: {valid_runs} (S~={S_prov:.2f}) [Model: {model_name}]"
                    )
                    sys.stdout.flush()
            else:
                print(f"   ... Run {i+1}/{N} - Invalid (All models failed)")

        if valid_runs == 0:
            return 0.0, {}

        E_ab /= valid_runs
        E_ab_prime /= valid_runs
        E_a_prime_b /= valid_runs
        E_a_prime_b_prime /= valid_runs

        S = abs(E_ab - E_ab_prime + E_a_prime_b + E_a_prime_b_prime)
        return S, {
            "E_ab": E_ab,
            "E_ab'": E_ab_prime,
            "E_a'b": E_a_prime_b,
            "E_a'b'": E_a_prime_b_prime,
            "N": valid_runs,
        }

    def execute_experiment(self):
        print(f"🔔 FASE 60: TESTE DE BELL SEMÂNTICO (CASCADE)")
        print("-------------------------------------")

        S_value, components = self.run_correlation_measure(N=20)

        if not components:
            print("❌ Falha: Nenhuma medição válida.")
            return

        print(f"\n📊 RESULTADOS CHSH (N={components.get('N')} confirmed):")
        for k, v in components.items():
            if k != "N":
                print(f"   {k}: {v:.2f}")
        print(f"\n   VALOR S FINAL: {S_value:.4f}")

        print("\n🧐 DIAGNÓSTICO:")
        if S_value > 2.0:
            print("   🚀 VIOLAÇÃO DE BELL DETECTADA! (S > 2)")
            print("   O Modelo exibe contextualidade não-local (Quantum Semantic Contextuality).")
        else:
            print("   📉 COMPORTAMENTO CLÁSSICO. (S <= 2)")
            print("   O Modelo opera sob realismo local.")


if __name__ == "__main__":
    try:
        test = SemanticBellTest()
        test.execute_experiment()
    except Exception as e:
        print(f"Erro Fatal: {e}")
