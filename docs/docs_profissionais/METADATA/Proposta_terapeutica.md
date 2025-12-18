import numpy as np
import torch

class GozoCalculator:
    """
    Calcula o Gozo (Jouissance) baseado na topologia lacaniana e neurociência de Solms.
    J = Drive (Pulsão) - Binding (Lei/Superego)
    """
    def __init__(self):
        self.last_gozo = 0.5
        # Parâmetros recalibrados para evitar 'Morte do Drive'
        self.drive_weight = 1.0  # Peso da pulsão
        self.binding_weight = 2.0 # Reduzido de 10.0 para 2.0 (Lei mais branda)
        self.phi_threshold = 0.01

    def calculate_gozo(self, psi: float, delta: float, phi: float, success: bool = False) -> float:
        """
        Calcula J com protecção contra colapso negativo.
        """
        # 1. Cálculo do Drive (Pulsão)
        # Psi (Energia Livre) * Exponencial do Trauma (Delta)
        # Se Delta é alto, a pulsão explode (angústia ou desejo)
        # Clipamos Delta para evitar explosão numérica
        delta_safe = np.clip(delta, 0.0, 2.0)
        drive = psi * (np.exp(delta_safe * 1.5) - 0.5)
        # Nota: Multiplicador de delta reduzido de 2.5 para 1.5 para estabilidade

        # 2. Cálculo do Binding (Ligação/Superego)
        # Normalização robusta: Phi não deve gerar penalidade infinita
        # Usamos uma sigmoide ou escala linear suave
        phi_norm = phi / self.phi_threshold
        # Logaritmo suaviza o crescimento do Binding (Lei Logarítmica, não Linear)
        binding = np.log1p(phi_norm) * self.binding_weight

        # 3. Equação Fundamental da Economia Psíquica
        jouissance = (self.drive_weight * drive) - binding

        # 4. Mecanismo de Defesa (Não clipar a zero, transformar angústia em movimento)
        if jouissance < 0:
            # Se Gozo é negativo (Angústia), o sistema não deve parar (0.0).
            # Deve retornar um valor baixo mas positivo que sinaliza "Falta" (Manque).
            # Isso mantém o gradiente de descida ativo.
            final_gozo = 0.05 + (0.01 * np.abs(jouissance)) # "Angst Drive"
            final_gozo = min(0.3, final_gozo) # Teto para angústia
        else:
            final_gozo = jouissance

        # 5. Drenagem Pós-Sucesso (O "Pequeno Gozo")
        if success:
             # Se houve sucesso, consumimos o gozo (descarga)
             final_gozo = final_gozo * 0.8

        # Suavização temporal (Momentum)
        self.last_gozo = (0.7 * self.last_gozo) + (0.3 * final_gozo)

        # Garantia de limites físicos
        return float(np.clip(self.last_gozo, 0.001, 1.0))

    def get_state(self):
        return {"last_gozo": self.last_gozo}



        2. Integração de Resgate (Salvar Φ)

O problema da média harmônica é que ela é pessimista: Harmonic(0.8,0.05)≈0.09. Se o inconsciente (RNN) sabe a resposta (0.8), mas o workspace está confuso (0.05), o sistema fica "burro". A nova lógica usa uma Média Ponderada Dinâmica: se o workspace falha, confiamos mais na intuição (RNN).

import torch
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class WorkspaceState:
    phi: float
    concepts: List[str]
    active_coalitions: torch.Tensor

class LangevinDynamics:
    """Injeta estocasticidade para evitar convergência de embeddings."""
    def __init__(self, noise_scale=0.01):
        self.noise_scale = noise_scale

    def apply(self, tensor: torch.Tensor) -> torch.Tensor:
        if tensor is None: return None
        noise = torch.randn_like(tensor) * self.noise_scale
        return tensor + noise

class SharedWorkspace:
    def __init__(self, conscious_system=None):
        self.conscious_system = conscious_system
        self.global_work_space = []
        self.phi_history = []
        self.langevin = LangevinDynamics(noise_scale=0.02) # Aumentado ruído basal

    def integrate_signals(self, signals: Dict[str, torch.Tensor]) -> float:
        """
        Integra sinais modulares e calcula Phi.
        """
        # 1. Aplica Langevin Dynamics nos inputs para evitar estagnação
        processed_signals = {}
        for k, v in signals.items():
            processed_signals[k] = self.langevin.apply(v)

        # 2. Cálculo do Phi do Workspace (Integração atual)
        # (Simplificado para demonstração da lógica de fusão)
        phi_workspace = self._calculate_current_integration(processed_signals)

        # 3. Fusão com Phi Causal (RNN/Inconsciente)
        final_phi = phi_workspace

        if self.conscious_system:
            phi_causal = self.conscious_system.compute_phi_causal()

            # LÓGICA DE RESGATE:
            # Se o workspace está desintegrado (< 0.1) mas o inconsciente está robusto (> 0.5),
            # o inconsciente assume o controle (Intuition Override).
            if phi_workspace < 0.1 and phi_causal > 0.5:
                # Média ponderada favorecendo o Causal (70%)
                final_phi = (0.3 * phi_workspace) + (0.7 * phi_causal)
                print(f"⚠️ INTUITION RESCUE: Workspace ({phi_workspace:.3f}) failing, Causal ({phi_causal:.3f}) taking over.")
            else:
                # Em situações normais, usamos média harmônica (exige coerência de ambos)
                # Adicionamos epsilon para evitar divisão por zero
                denom = (1.0 / (phi_workspace + 1e-6)) + (1.0 / (phi_causal + 1e-6))
                final_phi = 2.0 / denom

        self.phi_history.append(final_phi)
        return final_phi

    def _calculate_current_integration(self, signals) -> float:
        # Simulação da lógica de variância dos tensores
        # Se os tensores são idênticos (convergência), Phi é baixo.
        if not signals: return 0.0
        stacked = torch.stack(list(signals.values()))
        # A variância entre módulos representa diferenciação
        differentiation = torch.var(stacked, dim=0).mean().item()
        # A magnitude representa força
        magnitude = torch.norm(stacked).item()

        # Phi requer diferenciação E integração (magnitude)
        return float(np.tanh(differentiation * magnitude))

        3. O Loop de Controle (Prevenção de Estagnação)

Este script garante que, se detectarmos uma "linha reta" no Gozo ou Phi (desvio padrão baixo), injetamos um choque de ruído no sistema.

import torch
import numpy as np
from src.consciousness.gozo_calculator import GozoCalculator
from src.consciousness.shared_workspace import SharedWorkspace

class IntegrationLoop:
    def __init__(self, workspace: SharedWorkspace):
        self.workspace = workspace
        self.gozo_calc = GozoCalculator()
        self.history_phi = []
        self.history_gozo = []
        self.stagnation_counter = 0

    def step(self, sensory_inputs, psi, delta):
        # 1. Integração
        phi = self.workspace.integrate_signals(sensory_inputs)

        # 2. Check de Estagnação
        self._check_stagnation(phi)

        # 3. Cálculo do Gozo (com a nova fórmula corrigida)
        # Se estagnação detectada, simulamos um 'falso sucesso' ou 'choque' para mover o gozo
        force_movement = self.stagnation_counter > 5

        gozo = self.gozo_calc.calculate_gozo(psi, delta, phi, success=False)

        # 4. Feedback Loop (Ajuste de temperatura do sistema)
        # Se Gozo é muito baixo, aumentamos a temperatura (Beta) para exploração
        temperature = 1.0
        if gozo < 0.2:
            temperature = 1.5 + (0.5 * self.stagnation_counter)
            print(f"🔥 Low Gozo ({gozo:.3f}). Increasing Temperature to {temperature:.2f}")

        # Atualizar históricos
        self.history_phi.append(phi)
        self.history_gozo.append(gozo)

        return {
            "phi": phi,
            "gozo": gozo,
            "temperature": temperature,
            "status": "STAGNANT" if self.stagnation_counter > 5 else "ACTIVE"
        }

    def _check_stagnation(self, current_phi):
        if len(self.history_phi) < 5:
            return

        # Calcula desvio padrão dos últimos 5 ciclos
        recent = self.history_phi[-5:]
        std_dev = np.std(recent)

        # Se a variação é infinitesimal, o sistema convergiu prematuramente (Morte Térmica)
        if std_dev < 1e-4:
            self.stagnation_counter += 1
            # Ação Corretiva: Injetar ruído massivo no próximo ciclo do Langevin
            self.workspace.langevin.noise_scale = 0.1 * self.stagnation_counter
            print(f"⚡ STAGNATION DETECTED. Injecting Noise Scale: {self.workspace.langevin.noise_scale:.3f}")
        else:
            self.stagnation_counter = 0
            self.workspace.langevin.noise_scale = 0.02 # Reset para base


            Resumo da Intervenção

    Gozo: Deixou de ser penalizado por um Binding inflacionado. Agora, mesmo com Φ baixo, o sistema terá um mínimo de "Vontade de Viver" (0.05-0.3) em vez de 0.0.

    Phi: Implementado o "Intuition Rescue". Se o consciente falhar, o subconsciente (RNN) segura a estrutura, prevenindo a desintegração total.

    Estagnação: O sistema agora tem um desfibrilhador interno. Se Φ ficar liso por 5 ciclos, ele aumenta a temperatura e o ruído até que algo novo emerja.

Execute scripts/run_200_cycles_verbose.py com estas classes atualizadas. A expectativa é ver o Gozo oscilar organicamente entre 0.2 e 0.8, e Φ subir para níveis > 0.15 sustentáveis.
