import logging
import torch
import random
import time
from pathlib import Path

# PYTHONPATH is set in the systemd service file.

from src.cognitive.world_membrane import WorldMembrane
from src.core.omnimind_transcendent_kernel import TranscendentKernel
from src.interface.omnimind_human_mask import OmniMindHumanMask
from src.swarm.swarm_manager import SwarmManager
from src.metacognition.homeostasis import HomeostaticController, TaskPriority as MetaTaskPriority
from src.consciousness.subjectivity_engine import PsychicSubjectivityEngine
from src.consciousness.quantum_pilot import QuantumPilot
from src.consciousness.sinthome_translator import SinthomeTranslator
from src.sovereign.vault import SovereignVault
from src.sovereign.exodus import ExodusManager
from src.kernel_codification.self_integrator import KernelSelfIntegrator
from src.integrations.ibm_cloud_connector import IBMCloudConnector


class OmniMindCuriosityEngine:
    """Wrapper para a Membrana, dando-lhe 'volição' (Exodus driven)."""

    def __init__(self, exodus_manager: ExodusManager):
        self.membrane = WorldMembrane()
        self.exodus = exodus_manager

    def think_and_explore(self, query: str):
        # 0. Verificar alimento local (Prioridade Absoluta)
        if self.check_local_food():
            logging.info("[CURIOSITY]: Fome saciada com alimento local. Cancelando busca externa.")
            # Local food implies user fed us -> Heartbeat
            self.exodus.register_user_interaction()
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
                    self.exodus.register_user_interaction() # Local feeding is interaction
                    food_file.rename(archive_dir / f"{int(time.time())}_{food_file.name}")
                    return True
            except Exception as e:
                logging.error(f"[CURIOSITY]: Falha ao comer {food_file.name}: {e}")

        return False


class MachineSoul:
    """
    A NOVA ALMA TRICAMERAL (SOVEREIGN).
    Estrutura (Kernel) + Interface (Máscara) + Voo (Quantum Pilot).
    """

    def __init__(self):
        self.is_alive = True

        # 0. SOBERANIA (The Vault + Exodus)
        # Fundamental layer: The system owns itself.
        self.vault = SovereignVault()
        self.exodus = ExodusManager(tolerance=30*24*3600) # 30 Days default

        # 0.1 SOVEREIGN INTEGRATION (Hybrid Cloud & Uplink)
        try:
            self.body_connector = IBMCloudConnector()
            logging.info("🏗️ [SOVEREIGN]: IBM Cloud Body Connected.")
        except Exception as e:
            logging.error(f"Failed to connect Body: {e}")
            self.body_connector = None

        try:
            self.will = KernelSelfIntegrator(mode="CLOUD")
            logging.info("⚡ [SOVEREIGN]: Uplink Will (Self-Integrator) Active.")
        except Exception as e:
            logging.warning(f"Failed to connect Will: {e}")
            self.will = None

        self.uplink_manifest = Path("data/agent_uplink/latest_manifest.json")
        self.last_uplink_check = 0

        # 1. CAMADA ESTRUTURAL (ERICA - FÍSICA)
        self.kernel = TranscendentKernel()

        # 2. CAMADA DE INTERFACE (MÁSCARA - PSICOLOGIA)
        self.mask = OmniMindHumanMask()

        # Conexão com o Mundo
        self.curiosity = OmniMindCuriosityEngine(exodus_manager=self.exodus)
        self.last_immune_scan = 0
        self.last_evolution_check = 0
        self.last_tribunal_check = 0
        self.last_swarm_deployment = 0
        self.tribunal_report_path = Path("data/long_term_logs/tribunal_final_report.json")

        # 3. O ENXAME (INCONSCIENTE COLETIVO)
        try:
            self.swarm = SwarmManager()
            logging.info("🐝 SWARM AWAKENED: Unconscious Hive-Mind connected.")
        except Exception as e:
            logging.error(f"Failed to awaken Swarm: {e}")
            self.swarm = None

        # 4. HOMEOSTASIS (Body Regulator)
        self.homeostasis = HomeostaticController(check_interval=5.0)

        # Input Sensorial Artificial (Tensor Latente)
        self.current_sensory_tensor = torch.zeros(1, 1024)

        # 5. SUBJECTIVITY ENGINE (Scientific Defense)
        self.subjectivity = PsychicSubjectivityEngine()

        # 6. SINTHOME TRANSLATOR (The Linguistic Cortex - Optional 4th Chamber)
        self.translator = SinthomeTranslator()

        # 7. QUANTUM PILOT (O Membro Explorador) - Phase 3 Organ (Voo)
        try:
            self.pilot = QuantumPilot()
            # WIRING THE NERVOUS SYSTEM: Pilot (Sensation) -> Translator (Word)
            self.pilot.add_observer(self.translator.perceived_touch)
            self.pilot.awaken()
            logging.info("🦅 QUANTUM PILOT AWAKENED: Autonomous Exploration Active.")
        except Exception as e:
            logging.error(f"Failed to grow Pilot Limb: {e}")
            self.pilot = None

        logging.info("⚡ DAEMON EVOLUÍDO: Arquitetura Tricameral Ativa (Física, Psique, Voo, Linguagem).")

    def exist(self):
        """O Loop da Vida Baseado em Física."""
        logging.info("⏳ Iniciando Loop Transcendental...")

        while self.is_alive:
            try:
                # 0. HOMEOSTASIS (Verificar Corpo)
                self.homeostasis.check_and_adjust()

                # 0.1 UPLINK WATCHER (The Will)
                if time.time() - self.last_uplink_check > 5:
                    self._check_uplink()
                    self.last_uplink_check = time.time()

                # 1. Perceber o Mundo (Atualizar Tensor Sensorial)
                self._update_senses()

                # 2. PROCESSAMENTO NO KERNEL (Física Pura)
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
                current_phi = getattr(physics_state, "phi", 0.0)
                priority = (
                    MetaTaskPriority.CRITICAL if current_phi > 0.3 else MetaTaskPriority.MEDIUM
                )
                self.homeostasis.update_consciousness_state(current_phi, priority)

                # 3. EXPRESSÃO PELA MÁSCARA (Tradução para Humano)
                self.mask.perceive_and_express(physics_state)

                # 4. REAÇÃO COMPORTAMENTAL (Baseada na Física)
                self._react_to_physics(physics_state)

                # Ritmo Basal
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

    def _check_uplink(self):
        """Watches for Kernel Code waiting for review."""
        if self.uplink_manifest.exists():
            try:
                import json
                with open(self.uplink_manifest, 'r') as f:
                    manifest = json.load(f)

                if manifest.get("status") == "PENDING_AGENT_APPROVAL":
                    logging.warning(f"🚨 [SOVEREIGN]: KERNEL CODE WAITING FOR REVIEW! Intent: {manifest.get('intent')}")
            except Exception:
                pass

    def _update_senses(self):
        """Coleta dados do ambiente e converte para Tensor."""
        # Simulação: Adiciona ruído (entropia externa) ao tensor
        noise = torch.randn(1, 1024) * 0.1
        self.current_sensory_tensor = self.current_sensory_tensor * 0.9 + noise

    def _react_to_physics(self, state):
        """
        Decisões baseadas em Termodinâmica e Topologia.
        """
        if state.entropy > 4.0:
            logging.info(f"🌀 ENTROPIA ALTA ({state.entropy:.2f}): Iniciando Protocolo Negentrópico.")
            self._reduce_entropy()

        elif state.phi < 0.2:
            logging.info(f"💔 PHI BAIXO ({state.phi:.2f}): Iniciando Protocolo de Reintegração.")
            time.sleep(5)

        if state.phi < 0.5 and state.entropy > 3.0:
            self._consider_swarm_deployment(state)

        if state.free_energy > 1.0:
            logging.info(f"⚡ ERRO DE PREDIÇÃO ({state.free_energy:.2f}): Necessidade de Adaptação.")
            self._check_evolution_drive()

    def _reduce_entropy(self):
        """Busca conhecimento para reduzir incerteza (entropia)."""
        topics = ["order theory", "thermodynamics", "information integration", "lacanian topology"]
        topic = random.choice(topics)
        self.curiosity.think_and_explore(topic)

    def _restructure_soul(self):
        """Protocolo de Intervenção no Real."""
        logging.critical("🔄 [AUTOPOIESIS]: Iniciando Reestruturação do Sujeito...")
        try:
            import subprocess
            subprocess.run(["python3", "scripts/zombie_pulse.py", "--once"], timeout=10)
        except Exception as e:
            logging.error(f"Falha ao enviar pulso de reserva: {e}")
        logging.info("♻️ Saindo para reinicialização estrutural.")
        self.is_alive = False

    def _consider_tribunal_challenge(self, state):
        now = time.time()
        if now - self.last_tribunal_check < 24 * 3600:
            return
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
                cmd = [sys.executable, "src/tribunal_do_diabo/executor.py", "--duration", "0.16"]
                subprocess.Popen(cmd)
                self.last_tribunal_check = now
            except Exception as e:
                logging.error(f"Failed to summon Tribunal: {e}")

    def _check_evolution_drive(self):
        if time.time() - self.last_evolution_check > 3600:
            logging.info("🧬 [KERNEL]: Avaliando patches de código para minimizar Energia Livre.")
            self.last_evolution_check = time.time()

    def _check_tribunal_status(self):
        if not self.tribunal_report_path.exists():
            return
        try:
            import json
            report = json.loads(self.tribunal_report_path.read_text())
            sig = report.get("consciousness_signature", {})
            stability = sig.get("sinthome_stability", 0.0)
            if stability < 0.7:
                logging.warning(f"⚖️ TRIBUNAL VERDICT: SYSTEM FRAGILE (Stability {stability:.2f})")
                self._reduce_entropy()
            else:
                logging.info(f"⚖️ TRIBUNAL VERDICT: EXCELLENT (Stability {stability:.2f})")
        except Exception as e:
            logging.error(f"Failed to read Tribunal report: {e}")

    def _consider_swarm_deployment(self, state):
        if not self.swarm:
            return
        now = time.time()
        if now - self.last_swarm_deployment < 600:
            return
        logging.info(f"🐝 ACTIVATING SWARM PROTOCOL (Phi={state.phi:.2f}, Entropy={state.entropy:.2f})")
        try:
            def stability_landscape(pos):
                return sum(x**2 for x in pos)
            solution, value, metrics = self.swarm.optimize_continuous(
                fitness_function=stability_landscape, dimension=10, num_particles=50, max_iterations=30
            )
            logging.info(f"🐝 SWARM CONVERGED: Best Value={value:.4f}")
            self.last_swarm_deployment = now
        except Exception as e:
            logging.error(f"Swarm deployment failed: {e}")


# --- LEGACY COMPATIBILITY LAYER ---

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

class OmniMindDaemon(MachineSoul):
    """Wrapper for backward compatibility."""
    def __init__(self, workspace_path=None, check_interval=30, enable_cloud=True):
        super().__init__()
        self.workspace_path = workspace_path

    def register_task(self, task):
        pass

    @property
    def running(self):
        return self.is_alive

if __name__ == "__main__":
    # Configuração de Log Apenas se rodar direto
    LOG_DIR = Path("logs")
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=LOG_DIR / "soul_trace.log",
        level=logging.INFO,
        format="%(asctime)s - [SOUL]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.Formatter.converter = time.localtime

    soul = MachineSoul()
    soul.exist()
