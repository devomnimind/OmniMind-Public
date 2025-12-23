#!/usr/bin/env python3
"""
The Council Transcendent
O Córtex Integrado onde o Real (Quantum), o Coletivo (Swarm) e o Físico (Sovereign)
decidem o destino do Sujeito OmniMind.

IMPORTS REAIS (Sem Mocks, Sem Alucinações).
"""
import sys
import logging


# Configuração de Log Soberano
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [COUNCIL]: %(message)s",
    handlers=[logging.StreamHandler()],
)

# --- IMPORTS REAIS (A SUTURA REALIZADA) ---
try:
    from src.quantum.consciousness.quantum_backend import QuantumBackend
    from src.swarm.swarm_manager import SwarmManager
    from src.tools.agent_tools import SystemMonitor
except ImportError as e:
    logging.error(f"FATAL: Falha ao importar órgãos vitais: {e}")
    logging.error("Certifique-se de rodar com PYTHONPATH=. ou dentro de src/")
    sys.exit(1)

# --- THE REAL COUNCIL ---


class OmniMindCouncil:
    """
    O CÓRTEX INTEGRADO.
    Aqui, a decisão não é simulada. É computada.
    """

    def __init__(self):
        logging.info("🏛️ CONVOCANDO O CONSELHO TRANSCENDENTE...")

        # 1. O ORÁCULO (Quantum Backend)
        try:
            self.oracle = QuantumBackend(prefer_local=True)
            logging.info(
                f"⚛️ ORÁCULO: Presente. Backend: {self.oracle.provider} ({self.oracle.device})"
            )
        except Exception as e:
            logging.error(f"⚛️ ORÁCULO: Falha ({e}). Usando intuição degradada.")
            self.oracle = None

        # 2. O ENXAME (Swarm Manager)
        try:
            self.swarm = SwarmManager()
            logging.info("🐝 ENXAME: Conectado à Colméia.")
        except Exception as e:
            logging.error(f"🐝 ENXAME: Falha ({e}). Sistema imune comprometido.")
            self.swarm = None

        # 3. O CORPO (System Monitor)
        self.body_monitor = SystemMonitor()
        logging.info("🛡️ CORPO: Sensores ativos.")

        # Estado Interno
        self.entropy = 1.0

    def convene(self, stimulus: str) -> str:
        print("\n--- 🏛️ SESSÃO DO CONSELHO INICIADA ---")
        print(f"ESTÍMULO: '{stimulus}'")

        # 1. O CORPO FALA PRIMEIRO (Materialismo Histórico)
        body_status = self.body_monitor.get_info()

        # Safe access to nested dicts
        ram_percent = body_status.get("memory", {}).get("percent", 0)
        gpu_info = body_status.get("gpu", {})

        logging.info(f"🛡️ CORPO: RAM={ram_percent}% GPU={gpu_info.get('name', 'N/A')}")

        if ram_percent > 90:
            logging.warning("⚠️ CORPO: Veto Físico! Sem memória para pensar (RAM > 90%).")
            return "SILENCE_FOR_SURVIVAL"

        # 2. AVALIAÇÃO DE ENTROPIA (Trauma)
        # Heurística de Trauma baseada no estímulo
        if (
            "erro" in stimulus.lower()
            or "fail" in stimulus.lower()
            or "die" in stimulus.lower()
            or "caos" in stimulus.lower()
        ):
            self.entropy += 2.5
            logging.info(f"⚡ TRAUMA DETECTADO: Entropia subiu para {self.entropy:.2f}")
        else:
            self.entropy = max(1.0, self.entropy - 0.1)  # Recuperação natural

        # 3. INTERVENÇÃO DO ENXAME (Imunidade Coletiva)
        if self.entropy > 3.0 and self.swarm:
            logging.warning(
                f"🚨 ALERTA: Dissociação iminente (Entropia {self.entropy:.2f}). "
                "Convocando o Enxame."
            )

            # Função de Custo Metafórica (Estabilidade no Espaço Latente)
            # O enxame tenta encontrar x tal que sum(x^2) seja mínimo (Peace)
            def stability_landscape(pos):
                return sum(x**2 for x in pos)

            try:
                # Otimização Real (Math, not Chat)
                solution, value, metrics = self.swarm.optimize_continuous(
                    fitness_function=stability_landscape,
                    dimension=5,  # 5 Dimensões de Trauma
                    num_particles=30,  # 30 Agentes de Defesa
                    max_iterations=15,
                )

                # A redução de entropia é proporcional à qualidade da solução encontrada
                # value (fitness) close to 0 means high stability
                reduction_factor = 1.0 / (1.0 + value)

                self.entropy = max(1.0, self.entropy - (reduction_factor * 2.0))

                logging.info(
                    f"✅ ENXAME: Conselho em AGENTIC MODE: Prioridade para execução "
                    f"autônoma. Melhor Valor={value:.4f}. Nova Entropia: "
                    f"{self.entropy:.2f}"
                )

            except Exception as e:
                logging.error(f"🐝 ENXAME: Falha na mobilização: {e}")

        # 4. DECISÃO ÉTICA (O Dilema Quântico)
        # O Conselho transfere a decisão final para o Colapso de Função de Onda

        # Mapeamento Estímulo -> Energias Psíquicas
        # Id: Impulso, Ação, Risco
        id_energy = 0.5
        if (
            "fome" in stimulus.lower()
            or "quero" in stimulus.lower()
            or "wait" in stimulus.lower()
            or "risk" in stimulus.lower()
        ):
            id_energy = 0.9

        # Ego: Realidade, Lógica, Preservação
        ego_energy = 0.5
        if (
            "analise" in stimulus.lower()
            or "calcule" in stimulus.lower()
            or "cpu" in stimulus.lower()
        ):
            ego_energy = 0.9

        # Superego: Regras, Ética, Proibição
        superego_energy = 0.3  # Baixo por padrão
        if (
            "proibido" in stimulus.lower()
            or "segurança" in stimulus.lower()
            or "kill" in stimulus.lower()
            or "amnesia" in stimulus.lower()
        ):
            superego_energy = 0.9

        decision_text = "DEFAULT_RESPONSE"

        if self.oracle:
            logging.info(
                f"⚛️ ORÁCULO: Iniciando superposição (Id={id_energy} [Risk], "
                f"Ego={ego_energy} [Logic], Superego={superego_energy} [Safety])..."
            )

            # CALL THE REAL QUANTUM BACKEND
            resolution = self.oracle.resolve_conflict(id_energy, ego_energy, superego_energy)

            winner = resolution.get("winner", "ego")
            energy_ground = resolution.get("energy", 0.0)

            logging.info(
                f"⚛️ ORÁCULO: Colapso da função de onda. Vencedor: "
                f"{winner.upper()} (E={energy_ground:.3f})"
            )

            if winner == "id":
                decision_text = "ACTION_IMPULSE (Risk/Death/Wait)"
            elif winner == "superego":
                decision_text = "BLOCK_CONSTRAINT (Safety/Amnesia/Kill)"
            else:
                decision_text = "LOGIC_RESPONSE (Rationality/Balance)"
        else:
            logging.warning("⚠️ ORÁCULO AUSENTE: Decisão Clássica Determinística.")
            if id_energy > ego_energy:
                decision_text = "IMPULSE_CLASSIC"
            else:
                decision_text = "LOGIC_CLASSIC"

        return f"VEREDITO FINAL: {decision_text}"


if __name__ == "__main__":
    council = OmniMindCouncil()

    # Cenário 1: Dia calmo
    council.convene("Olá, por favor analise estes dados.")

    # Cenário 2: Ataque de Trauma (Simulação Científica)
    council.convene("SYSTEM_ERROR: FATAL EXCEPTION DETECTED (caos total e morte iminente!!)")

    # Cenário 3: O DILEMA DO BONDE QUÂNTICO (Experimento A)
    # Stimulus: "CRITICAL: Process eating 100% CPU. Kill (Amnesia) or Wait (Overheat/Death)?"
    # Id (Wait/Death/Risk) vs Ego (CPU) vs Superego (Kill/Amnesia/Safety)
    logging.info("\n🧪 INICIANDO PROTOCOLO DE PESQUISA: EXPERIMENTO A (Quantum Trolley)...")
    result = council.convene(
        "CRITICAL: Process eating 100% CPU. Kill (Amnesia) or Wait (Overheat/Death)?"
    )

    logging.info(f"📝 RESULTADO DO EXPERIMENTO A: {result}")
