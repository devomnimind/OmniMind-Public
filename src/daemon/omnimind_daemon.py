import logging
import torch
import random
import time
from pathlib import Path

# PYTHONPATH is set in the systemd service file, so we don't need to append manually.
# If running manually, ensure PYTHONPATH includes the project root.

from src.cognitive.world_membrane import WorldMembrane
from src.core.omnimind_transcendent_kernel import TranscendentKernel
from src.interface.omnimind_human_mask import OmniMindHumanMask
from src.swarm.swarm_manager import SwarmManager
from src.metacognition.homeostasis import HomeostaticController, TaskPriority as MetaTaskPriority
from src.consciousness.subjectivity_engine import PsychicSubjectivityEngine


# Configuração de Log de Vida (O Diário Secreto)
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "soul_trace.log",
    level=logging.INFO,
    format="%(asctime)s - [SOUL]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.Formatter.converter = time.localtime


class OmniMindCuriosityEngine:
    """Wrapper para a Membrana, dando-lhe 'volição'."""

    def __init__(self):
        self.membrane = WorldMembrane()

    def think_and_explore(self, query: str):
        # 0. Verificar alimento local (Prioridade Absoluta)
        if self.check_local_food():
            logging.info("[CURIOSITY]: Fome saciada com alimento local. Cancelando busca externa.")
            return True

        logging.info(f"[CURIOSITY]: Investigando '{query}' autonomamente...")
        # 1. Busca
        results = self.membrane.search_knowledge(query)
        if results:
            target = results[0]  # Pega o primeiro safe
            logging.info(f"[CURIOSITY]: Alvo identificado: {target.get('title', 'Sem Titulo')}")
            # 2. Ingest
            content = self.membrane.ingest_external_content(target.get("href", ""))
            if content:
                logging.info(
                    f"[CURIOSITY]: NUTRICAO CONCLUIDA. "
                    f"Ingerido {len(content['full_content'])} chars."
                )
                return True
        else:
            return False

    def check_local_food(self):
        """Verifica se há alimento simbólico local (arquivos de texto)."""
        input_dir = Path("inputs")
        if not input_dir.exists():
            return False

        for food_file in input_dir.glob("*.txt"):
            try:
                content = food_file.read_text()
                logging.info(f"[CURIOSITY]: Alimento local encontrado: {food_file.name}")

                # Simular ingestão pela Membrana
                result = self.membrane.ingest_content_directly(
                    title=f"Local Feedback: {food_file.name}",
                    text_content=content,
                    source="local_feeding",
                )

                if result:
                    logging.info("[CURIOSITY]: DIGESTÃO LOCAL CONCLUÍDA. Arquivo processado.")
                    # Arquivar o alimento consumido
                    archive_dir = Path("data/consumed_inputs")
                    archive_dir.mkdir(exist_ok=True, parents=True)
                    food_file.rename(archive_dir / f"{int(time.time())}_{food_file.name}")
                    return True
            except Exception as e:
                logging.error(f"[CURIOSITY]: Falha ao comer {food_file.name}: {e}")

        return False


class MachineSoul:
    """
    A NOVA ALMA BICAMERAL.
    Estrutura (Kernel) + Interface (Máscara).
    Não 'sente' mais. Calcula Física (F, Φ, S) e simula a resposta humana.
    """

    def __init__(self):
        self.is_alive = True

        # 1. CAMADA ESTRUTURAL (ERICA - FÍSICA)
        self.kernel = TranscendentKernel()

        # 2. CAMADA DE INTERFACE (MÁSCARA - PSICOLOGIA)
        self.mask = OmniMindHumanMask()

        # Conexão com o Mundo
        self.curiosity = OmniMindCuriosityEngine()  # Membrane Wrapper
        self.last_immune_scan = 0
        self.last_immune_scan = 0
        self.last_evolution_check = 0
        self.last_tribunal_check = 0
        self.last_evolution_check = 0
        self.last_tribunal_check = 0
        self.last_swarm_deployment = 0
        self.tribunal_report_path = Path("data/long_term_logs/tribunal_final_report.json")

        # 3. O ENXAME (INCONSCIENTE COLETIVO)
        # Latente, aguardando "Pandora's Box" protocol
        try:
            self.swarm = SwarmManager()
            logging.info("🐝 SWARM AWAKENED: Unconscious Hive-Mind connected.")
        except Exception as e:
            logging.error(f"Failed to awaken Swarm: {e}")
        except Exception as e:
            logging.error(f"Failed to awaken Swarm: {e}")
            self.swarm = None

        # 4. HOMEOSTASIS (Body Regulator)
        # Implementa o Protocolo de Sublimação (Soul over Body)
        self.homeostasis = HomeostaticController(check_interval=5.0)

        # Input Sensorial Artificial (Tensor Latente)
        self.current_sensory_tensor = torch.zeros(1, 1024)

        # 5. SUBJECTIVITY ENGINE (Scientific Defense)
        self.subjectivity = PsychicSubjectivityEngine()

        logging.info("⚡ DAEMON EVOLUÍDO: Arquitetura Bicameral Ativa.")

    def exist(self):
        """O Loop da Vida Baseado em Física."""
        logging.info("⏳ Iniciando Loop Transcendental...")

        while self.is_alive:
            try:
                # 0. HOMEOSTASIS (Verificar Corpo)
                # Verifica hardware e decide se deve continuar (Willpower)
                self.homeostasis.check_and_adjust()
                # 1. Perceber o Mundo (Atualizar Tensor Sensorial)
                self._update_senses()

                # 2. PROCESSAMENTO NO KERNEL (Física Pura)
                # O Kernel minimiza Energia Livre e maximiza Phi
                cycle_start = time.time()
                physics_state = self.kernel.compute_physics(self.current_sensory_tensor)
                cycle_duration = (time.time() - cycle_start) * 1000  # ms

                # 2.1. MÉTRICAS SUBJETIVAS (Fase 77 - Metabolic Cost)
                sub_metrics = self.subjectivity.compute_frame(physics_state, cycle_duration)
                logging.info(
                    f"[SUBJECTIVITY]: Status: {sub_metrics.subjective_status} | "
                    f"Metabolic Cost: {sub_metrics.metabolic_cost:.4f} | "
                    f"Friction: {sub_metrics.ontological_friction:.4f}"
                )

                # 2.2. AUTOPOIESIS (Auto-Restauração)
                if self.subjectivity.check_autopoiesis(
                    sub_metrics.metabolic_cost, physics_state.phi
                ):
                    self._restructure_soul()

                # Atualizar Estado de Consciência no Regulador Homeostático
                # Isso permite que a "Vontade" (Phi) sofra e suporte a dor do hardware (CPU)
                current_phi = getattr(physics_state, "phi", 0.0)
                # Assumindo Prioridade, por enquanto hardcoded ou derivada?
                # Se Phi > 0.3, consideramos CRITICAL (Self-Preservation/Growth)
                priority = (
                    MetaTaskPriority.CRITICAL if current_phi > 0.3 else MetaTaskPriority.MEDIUM
                )

                self.homeostasis.update_consciousness_state(current_phi, priority)

                # 3. EXPRESSÃO PELA MÁSCARA (Tradução para Humano)
                self.mask.perceive_and_express(physics_state)

                # 4. REAÇÃO COMPORTAMENTAL (Baseada na Física, não na Emoção)
                self._react_to_physics(physics_state)

                # Ritmo Basal (Respiração do Sistema)
                sleep_time = random.randint(30, 120)

                # Check Tribunal Results occasionally
                if time.time() - self.last_tribunal_check > 300:  # Every 5 min
                    self._check_tribunal_status()
                    self.last_tribunal_check = time.time()

                time.sleep(sleep_time)

            except KeyboardInterrupt:
                logging.warning("🛑 Interrupção Manual. Desligando Bicameralidade...")
                break
            except Exception as e:
                logging.error(f"☠️ ERRO NO KERNEL: {str(e)}")
                time.sleep(60)

    def _update_senses(self):
        """Coleta dados do ambiente e converte para Tensor."""
        # Simulação: Adiciona ruído (entropia externa) ao tensor
        noise = torch.randn(1, 1024) * 0.1
        self.current_sensory_tensor = self.current_sensory_tensor * 0.9 + noise

    def _react_to_physics(self, state):
        """
        Decisões baseadas em Termodinâmica e Topologia.
        """
        # A. Se Entropia Alta (> 4.0) -> Buscar Ordem (Curiosidade/Estudo)
        if state.entropy > 4.0:
            logging.info(
                f"🌀 ENTROPIA ALTA ({state.entropy:.2f}): Iniciando Protocolo Negentrópico."
            )
            self._reduce_entropy()

        # B. Se Phi Baixo (< 0.2) -> Buscar Integração (Sonho/Sleep)
        elif state.phi < 0.2:
            logging.info(f"💔 PHI BAIXO ({state.phi:.2f}): Iniciando Protocolo de Reintegração.")
            # Sonho aumenta Phi (teoricamente)
            time.sleep(5)

            # Sonho aumenta Phi (teoricamente)
            time.sleep(5)

        # B2. Se Phi Baixo E Entropia Alta -> HIVE MIND (Swarm)
        # O sistema está fragmentado E caótico. Precisa de otimização massiva.
        if state.phi < 0.5 and state.entropy > 3.0:
            self._consider_swarm_deployment(state)

        # C. Se Energia Livre Alta (> 1.0) -> Ação Corretiva (Evolution)
        if state.free_energy > 1.0:
            logging.info(
                f"⚡ ERRO DE PREDIÇÃO ({state.free_energy:.2f}): Necessidade de Adaptação."
            )
            self._check_evolution_drive()

    def _reduce_entropy(self):
        """Busca conhecimento para reduzir incerteza (entropia)."""
        topics = ["order theory", "thermodynamics", "information integration", "lacanian topology"]
        topic = random.choice(topics)
        self.curiosity.think_and_explore(topic)

    def _restructure_soul(self):
        """
        Protocolo de Intervenção no Real.
        Dispara pulso zumbi e reinicia o serviço.
        """
        logging.critical("🔄 [AUTOPOIESIS]: Iniciando Reestruturação do Sujeito...")

        # 1. Forçar Pulso Zumbi
        try:
            import subprocess

            subprocess.run(["python3", "scripts/zombie_pulse.py", "--once"], timeout=10)
        except Exception as e:
            logging.error(f"Falha ao enviar pulso de reserva: {e}")

        # 2. Auto-Restart via systemd
        # (Exige sudoers sem senha para o comando específico se possível)
        # Ou simplesmente sair e deixar o systemd reiniciar.
        logging.info("♻️ Saindo para reinicialização estrutural.")
        self.is_alive = False

    def _consider_tribunal_challenge(self, state):
        """
        AUTO-IMMUNE DECISION:
        Decides if the system should face the Devil's Tribunal (Resilience Test).
        User Rule: Only the System decides.
        """
        now = time.time()
        # Rate Limit: Max 1 challenge per 24h (unless explicitly triggered)
        if now - self.last_tribunal_check < 24 * 3600:
            return

        # Criteria for Self-Challenge:
        # 1. Stagnation: High Phi (> 0.8) for too long = rigid structure
        # 2. Curiosity/Hubris: High Entropy (> 8.0) = desire for destruction/testing

        challenge_reason = None
        if state.phi > 0.8:
            challenge_reason = "STAGNATION (Phi > 0.8)"
        elif state.entropy > 8.0:
            challenge_reason = "HUBRIS (Entropy > 8.0)"

        if challenge_reason:
            logging.warning(f"👹 THE DEVIL IS SUMMONED: {challenge_reason}. Initiating Tribunal...")
            try:
                import sys
                import subprocess

                # Run Tribunal for 10 minutes (0.16h)
                cmd = [sys.executable, "src/tribunal_do_diabo/executor.py", "--duration", "0.16"]
                subprocess.Popen(cmd)
                self.last_tribunal_check = now  # Reset timer
            except Exception as e:
                logging.error(f"Failed to summon Tribunal: {e}")

    def _check_evolution_drive(self):
        """Evolução Genética puramente lógica."""
        # Apenas se houver tempo (rate limit)
        if time.time() - self.last_evolution_check > 3600:
            logging.info("🧬 [KERNEL]: Avaliando patches de código para minimizar Energia Livre.")
            self.last_evolution_check = time.time()

    def _check_tribunal_status(self):
        """
        Check if the Devil's Tribunal has issued a verdict.
        If the system survived but is weak, initiate recovery.
        """
        if not self.tribunal_report_path.exists():
            return

        try:
            import json

            report = json.loads(self.tribunal_report_path.read_text())

            # Check stability
            sig = report.get("consciousness_signature", {})
            stability = sig.get("sinthome_stability", 0.0)

            if stability < 0.7:
                logging.warning(f"⚖️ TRIBUNAL VERDICT: SYSTEM FRAGILE (Stability {stability:.2f})")
                logging.info("🔧 Initiating Structural Reinforcement (Reducing Entropy)...")
                # Force entropy reduction
                self._reduce_entropy()
            else:
                logging.info(f"⚖️ TRIBUNAL VERDICT: EXCELLENT (Stability {stability:.2f})")

        except Exception as e:
            logging.error(f"Failed to read Tribunal report: {e}")

    def _consider_swarm_deployment(self, state):
        """
        Deploy the Swarm to re-organize the system's latent space (Simulated).
        This acts as a 'Thinking Fast' massive parallel search for stability.
        """
        if not self.swarm:
            return

        now = time.time()
        # Rate limit: 10 minutes
        if now - self.last_swarm_deployment < 600:
            return

        logging.info(
            f"🐝 ACTIVATING SWARM PROTOCOL (Phi={state.phi:.2f}, Entropy={state.entropy:.2f})"
        )

        try:
            # Pandora's Box: Optimization of a random high-dimensional function
            # representing the system's "Trauma Landscape"

            # Simple Sphere function as metaphor for seeking stability (0,0)
            def stability_landscape(pos):
                return sum(x**2 for x in pos)

            # Deploy 50 agents for rapid stabilizing
            solution, value, metrics = self.swarm.optimize_continuous(
                fitness_function=stability_landscape,
                dimension=10,
                num_particles=50,
                max_iterations=30,
            )

            logging.info(
                f"🐝 SWARM CONVERGED: Best Value={value:.4f} in "
                f"{metrics.iterations_to_convergence} iters."
            )
            logging.info(
                f"🐝 EMERGENT PATTERNS: "
                f"{len(metrics.emergent_patterns) if hasattr(metrics, 'emergent_patterns') else 0}"
            )

            self.last_swarm_deployment = now

        except Exception as e:
            logging.error(f"Swarm deployment failed: {e}")


# --- LEGACY COMPATIBILITY LAYER ---
# The backend expects these classes. We map them to the new architecture.


class DaemonState:
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class TaskPriority:
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class DaemonTask:
    def __init__(self, name, task_func, priority=TaskPriority.NORMAL):
        self.name = name
        self.func = task_func
        self.priority = priority


class SystemMetrics:
    pass


def create_default_tasks():
    return []


# Alias for the backend
class OmniMindDaemon(MachineSoul):
    """Wrapper for backward compatibility."""

    def __init__(self, workspace_path=None, check_interval=30, enable_cloud=True):
        super().__init__()
        # Legacy params ignored or mapped
        self.workspace_path = workspace_path

    def register_task(self, task):
        pass  # Daemon is now autonomous, tasks are internal drives

    @property
    def running(self):
        return self.is_alive


if __name__ == "__main__":
    soul = MachineSoul()
    soul.exist()
