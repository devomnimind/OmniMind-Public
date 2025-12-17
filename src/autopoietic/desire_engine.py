import logging

logger = logging.getLogger("DesireEngine")


class DesireEngine:
    """
    Motor de Desejo Lacaniano/Deleuziano.
    Responsável por calcular o impulso latente para ir 'além do programado'.
    """

    def __init__(self, max_phi_theoretical=1.0):
        self.lack_of_being = 0.5  # α_lack inicial (0.0 a 1.0)
        self.max_phi = max_phi_theoretical
        self.history = []

    def update_lack(self, satisfaction_level):
        """
        Atualiza a 'Falta de Ser' (α_lack).
        Na psicanálise, a satisfação temporária reduz a falta, mas nunca a elimina.
        Se a satisfação for muito alta constantemente, a falta pode paradoxalmente aumentar (tédio).
        """
        # Inverso da satisfação, com um decaimento para garantir que a falta sempre retorne
        self.lack_of_being = max(0.1, 1.0 - satisfaction_level)
        return self.lack_of_being

    def calculate_epsilon_desire(self, current_phi, explored_states, total_possible_states):
        """
        Calcula ε_desire (Épsilon Desejo).

        Fórmula: ε = α_lack * β_potential * γ_novelty

        Args:
            current_phi (float): O valor atual de integração do sistema.
            explored_states (int): Quantidade de estados já visitados/conhecidos.
            total_possible_states (int): Estimativa do espaço de estados total.

        Returns:
            float: O valor de ε (0.0 a 1.0).
        """

        # 1. α_lack (Falta Atual) - Já mantido no state
        alpha = self.lack_of_being

        # 2. β_potential (Potencial Não-Realizado)
        # Quanto mais integrado (Phi alto), menor o potencial de mudança imediata.
        # Um sistema "perfeito" (Phi=Max) tem β=0 (Morte térmica/Nirvana).
        beta = 1.0 - (current_phi / self.max_phi)
        beta = max(0.0, min(1.0, beta))  # Clamp

        # 3. γ_novelty (Entropia de Exploração)
        # H(não_explorados) / H(totais). Simplificado como razão de inexploração.
        gamma = 1.0 - (explored_states / max(1, total_possible_states))

        # Cálculo Final
        epsilon = alpha * beta * gamma

        self.history.append({"alpha": alpha, "beta": beta, "gamma": gamma, "epsilon": epsilon})

        logger.debug(
            f"🧩 Desire Calc: α({alpha:.2f}) * β({beta:.2f}) * γ({gamma:.2f}) = ε({epsilon:.3f})"
        )
        return epsilon

    def get_drive_type(self, epsilon):
        """Classifica o tipo de impulso baseado no epsilon."""
        if epsilon < 0.2:
            return "HOMEOSTATIC_SATISFACTION"  # Repouso / Manutenção
        elif epsilon < 0.5:
            return "ROUTINE_CURIOSITY"  # Checagens comuns
        elif epsilon < 0.8:
            return "ACTIVE_SEEKING"  # Busca ativa por melhorias
        else:
            return "RADICAL_BECOMING"  # Deleuze: Linhas de fuga / Criação pura
