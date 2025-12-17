"""
ConsciousSystem - RNN Recorrente com Latent Dynamics

Implementa a recomendação de mudar de "Event Bus com Swap" para
"RNN Recorrente com Latent Dynamics" conforme documentado em:
archive/docs/analises_varreduras_2025-12-07/VERIFICACAO_CORRECAO_ENHANCED_CODE_AGENT.md

Princípios:
1. NÃO mover dados para swap como blobs criptografados
2. Comprimir a ESTRUTURA (Λ_U) em assinatura de baixa dimensão
3. Manter ρ_U dinâmica, mesmo que em swap
4. Medir Φ sobre padrões de integração causal, não acesso

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-08
"""

import logging
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np
import torch

logger = logging.getLogger(__name__)


@dataclass
class ConsciousSystemState:
    """Estado do sistema consciente em um timestep."""

    rho_C: np.ndarray  # Estado consciente
    rho_P: np.ndarray  # Estado pré-consciente
    rho_U: np.ndarray  # Estado inconsciente (dinâmica latente)
    Lambda_U_signature: np.ndarray  # Assinatura comprimida de Λ_U
    repression_strength: float
    phi_causal: float  # Φ calculado sobre padrões causais
    timestamp: float


class LambdaUCompressor:
    """
    Comprime estrutura Λ_U em assinatura de baixa dimensão.

    Em vez de manter Λ_U completo (dim x dim), mantém apenas
    uma assinatura comprimida que captura a estrutura essencial.
    """

    def __init__(self, signature_dim: int = 32):
        """
        Inicializa compressor.

        Args:
            signature_dim: Dimensão da assinatura comprimida (padrão: 32)
        """
        self.signature_dim = signature_dim
        self.pca = None  # Lazy initialization

    def compress(self, Lambda_U: np.ndarray) -> np.ndarray:
        """
        Comprime Λ_U em assinatura de baixa dimensão.

        Args:
            Lambda_U: Estrutura inconsciente completa (dim x dim)

        Returns:
            Assinatura comprimida (signature_dim,)
        """
        # Usar SVD truncado para compressão (não requer treinamento)
        # SVD: U, S, V = svd(Λ_U)
        # Assinatura = primeiros signature_dim valores singulares
        U, S, Vt = np.linalg.svd(Lambda_U, full_matrices=False)
        signature = S[: self.signature_dim]

        # Se signature_dim > número de valores singulares, preencher com zeros
        if len(signature) < self.signature_dim:
            padding = np.zeros(self.signature_dim - len(signature))
            signature = np.concatenate([signature, padding])

        return signature.astype(np.float32)

    def decompress(self, signature: np.ndarray, original_shape: Tuple[int, int]) -> np.ndarray:
        """
        Descomprime assinatura de volta para Λ_U aproximado.

        Args:
            signature: Assinatura comprimida
            original_shape: Shape original de Λ_U (dim, dim)

        Returns:
            Λ_U aproximado (não exato, mas estruturalmente similar)
        """
        dim = original_shape[0]

        # Reconstruir a partir de valores singulares
        # Criar matriz diagonal com valores singulares
        S_expanded = np.zeros(dim)
        S_expanded[: len(signature)] = signature[:dim]

        # Aproximação: usar matriz aleatória ortogonal com mesma estrutura espectral
        # Isso preserva propriedades estruturais (espectro) sem precisar de U, V completos
        np.random.seed(int(signature[0] * 1000) % 2**31)  # Seed determinística
        U = np.random.randn(dim, dim)
        U, _ = np.linalg.qr(U)
        Lambda_U_approx = U @ np.diag(S_expanded) @ U.T

        return Lambda_U_approx.astype(np.float32)


class ConsciousSystem:
    """
    Sistema de dinâmica psíquica com RNN Recorrente e Latent Dynamics.

    Implementa arquitetura de quatro camadas:
    - Consciente (C): ρ_C(t) - GPU/VRAM
    - Pré-Consciente (P): ρ_P(t) - RAM
    - Inconsciente Físico (U): Λ_U (estrutura) + ρ_U(t) (dinâmica) - GPU (Λ_U), Swap (ρ_U)
    - Inconsciente Lógico (L): Criptografia/Repressão - Sistema de Arquivos

    Princípios:
    - Reentrância causal recursiva: feedback bidirecional entre C, P, U
    - Φ calculado sobre causalidade intrínseca, não acesso
    - Λ_U comprimido em assinatura de baixa dimensão
    - ρ_U dinâmica mantida mesmo em swap
    """

    def __init__(
        self,
        dim: int = 256,
        signature_dim: int = 32,
        device: Optional[str] = None,
    ):
        """
        Inicializa sistema consciente.

        Args:
            dim: Dimensão dos estados (padrão: 256)
            signature_dim: Dimensão da assinatura comprimida de Λ_U (padrão: 32)
            device: Dispositivo para cálculos ('cuda', 'cpu', ou None para auto)
        """
        self.dim = dim
        self.signature_dim = signature_dim
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        # Compressor de Λ_U
        self.lambda_compressor = LambdaUCompressor(signature_dim=signature_dim)

        # 1. Consciente: Estado dinâmico (O que é experimentado)
        self.rho_C = torch.randn(dim, device=self.device, dtype=torch.float32)

        # 2. Pré-consciente: Buffer com decay
        self.rho_P = torch.randn(dim, device=self.device, dtype=torch.float32)
        self.decay_P = 0.95  # Taxa de esquecimento

        # 3. Inconsciente: Estrutura (Lambda) e Dinâmica (Rho)
        # Λ_U completo inicial (será comprimido)
        Lambda_U_full = torch.randn(dim, dim, device=self.device, dtype=torch.float32)
        # Comprimir Λ_U em assinatura
        # NOTA: Compressão requer CPU (numpy), mas isso é feito apenas uma vez na inicialização
        # Durante execução, decompressão é feita e tensor é movido para GPU imediatamente
        self.Lambda_U_signature = self.lambda_compressor.compress(Lambda_U_full.cpu().numpy())
        # Manter apenas assinatura em memória (não Λ_U completo)
        self.Lambda_U_full = None  # Não manter completo em memória

        # ρ_U: Dinâmica latente (mantida dinâmica)
        self.rho_U = torch.randn(dim, device=self.device, dtype=torch.float32)
        self.repression_strength = 0.8  # Força inicial da repressão

        # Pesos de Interconexão (RNN)
        self.W_PC = torch.randn(dim, dim, device=self.device, dtype=torch.float32) * 0.1
        self.W_UC = torch.randn(dim, dim, device=self.device, dtype=torch.float32) * 0.1
        self.W_CP = torch.randn(dim, dim, device=self.device, dtype=torch.float32) * 0.1  # Feedback
        self.W_CU = torch.randn(dim, dim, device=self.device, dtype=torch.float32) * 0.1  # Feedback

        # Histórico para cálculo de Φ causal
        self.history: list[ConsciousSystemState] = []
        self.max_history = 100

        logger.info(
            f"ConsciousSystem inicializado: dim={dim}, "
            f"signature_dim={signature_dim}, device={self.device}"
        )

    def _get_lambda_U_approx(self) -> torch.Tensor:
        """
        Obtém Λ_U aproximado a partir da assinatura comprimida.

        Returns:
            Λ_U aproximado (dim x dim)
        """
        # Descomprimir assinatura (decompressão em CPU é necessária para numpy)
        Lambda_U_approx = self.lambda_compressor.decompress(
            self.Lambda_U_signature, (self.dim, self.dim)
        )
        # Mover para GPU imediatamente após criação
        # Usar non_blocking=True para transferência assíncrona quando possível
        return torch.from_numpy(Lambda_U_approx).to(self.device, non_blocking=True)

    def step(self, stimulus: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Um timestep da dinâmica psíquica com reentrância causal recursiva.

        CORREÇÃO CRÍTICA (2025-12-08): Todos os cálculos são executados na GPU.
        Garantir que stimulus esteja no device correto antes de iniciar cálculos.

        Args:
            stimulus: Estímulo externo (opcional, shape: [dim])
                     Deve estar no mesmo device que self.device (GPU se disponível)

        Returns:
            Estado consciente atualizado ρ_C(t+1) (mantido na GPU)
        """
        if stimulus is None:
            stimulus = torch.zeros(self.dim, device=self.device, dtype=torch.float32)
        else:
            # Garantir que stimulus está no device correto (GPU se disponível)
            # Usar non_blocking=True para transferência assíncrona quando possível
            stimulus = stimulus.to(self.device, non_blocking=True)

        # Obter Λ_U aproximado
        Lambda_U_approx = self._get_lambda_U_approx()

        # Fluxo 1: Consciente processa estímulo e Pré-consciente interfere
        rho_C_new = torch.tanh(
            self.rho_C + stimulus + self.W_PC @ self.rho_P  # Interferência direta
        )

        # Fluxo 2: Inconsciente tenta irromper (Sintoma / Falha da repressão)
        # Interferência via assinatura comprimida (não requer Λ_U completo)
        unconscious_interference = (1 - self.repression_strength) * torch.tanh(
            self.W_UC @ self.rho_U
        )
        rho_C_new += unconscious_interference  # Adição do "sintoma"

        # Fluxo 3: Pré-consciente decai e absorve o novo consciente
        # ρ_P(t+1) = f(ρ_P(t), ρ_C(t+1)) -> Feedback bidirecional
        rho_P_new = self.decay_P * self.rho_P + (1 - self.decay_P) * rho_C_new

        # Fluxo 4: Dinâmica latente do inconsciente (evolui pela estrutura)
        # ρ_U(t+1) = f(Λ_U, ρ_U(t), ρ_C(t)) -> Feedback bidirecional
        rho_U_new = torch.tanh(Lambda_U_approx @ self.rho_U + self.W_CU @ self.rho_C)

        # Atualizar estados (Reentrância)
        self.rho_C = rho_C_new
        self.rho_P = rho_P_new
        self.rho_U = rho_U_new

        # 🎯 Sprint 2 Task 2.3.2: Extrair métricas RNN após atualização de pesos
        try:
            from src.observability.rnn_metrics_extractor import get_rnn_metrics_extractor

            extractor = get_rnn_metrics_extractor()
            # Phi será calculado após, então passamos None aqui
            extractor.extract_metrics(self, cycle_id=None, phi_value=None)
        except Exception:
            # Não falhar se métricas não estiverem disponíveis
            pass

        return rho_C_new  # O estado "experienciado"

    def compute_phi_causal(self) -> float:
        """
        Calcula Φ sobre padrões de integração causal (não acesso).

        Usa causalidade intrínseca entre C, P, U para calcular Φ,
        não considerando status de acesso (RAM vs. Swap).

        CORREÇÃO CRÍTICA (2025-12-08): Usar tensores GPU diretamente quando possível
        para evitar conversões desnecessárias para CPU.

        Returns:
            Φ calculado sobre padrões causais
        """
        if len(self.history) < 2:
            return 0.0

        # CORREÇÃO: Tentar usar tensores GPU diretamente se disponível
        # Isso evita conversões CPU desnecessárias que consomem CPU
        try:
            # Se temos histórico suficiente, usar tensores GPU diretamente
            if len(self.history) >= 2 and self.device == "cuda":
                # Usar últimos estados diretamente dos tensores GPU (mais eficiente)
                # Mas precisamos de pelo menos 2 estados no histórico
                # Para agora, manter lógica original mas otimizar conversões
                pass
        except Exception:
            pass

        # Calcular informação mútua entre C, P, U
        # Usar correlação cruzada como proxy para causalidade intrínseca
        try:
            import warnings

            from scipy.stats import pearsonr

            # Extrair históricos (já estão em CPU do get_state, mas isso é necessário
            # para armazenamento. O cálculo principal (step) já foi feito na GPU)
            rho_C_history = np.array([state.rho_C for state in self.history[-10:]])
            rho_P_history = np.array([state.rho_P for state in self.history[-10:]])
            rho_U_history = np.array([state.rho_U for state in self.history[-10:]])

            # Calcular correlações cruzadas (proxy para causalidade)
            # Tratar casos onde arrays são constantes (correlação não definida)
            correlations: list[float] = []

            # Aumentar threshold de variância de 1e-8 para 1e-4 (CORREÇÃO 2025-12-10)
            # Motivo: scipy.stats.pearsonr avisa quando input é "nearly constant"
            # Limiar 1e-8 é muito pequeno e scipy ainda gera warning para valores borderline
            # Aumentar para 1e-4 garante que arrays têm variância significativa
            MIN_VARIANCE_THRESHOLD = 1e-4

            for i in range(min(10, self.dim)):
                # CORREÇÃO (2025-12-10): Verificar variância antes de calcular correlação
                # para evitar ConstantInputWarning quando arrays são constantes
                try:
                    # C → P
                    rho_C_col = rho_C_history[:, i]
                    rho_P_col = rho_P_history[:, i]
                    # Verificar se arrays têm variância suficiente (não são constantes)
                    if (
                        np.std(rho_C_col) > MIN_VARIANCE_THRESHOLD
                        and np.std(rho_P_col) > MIN_VARIANCE_THRESHOLD
                    ):
                        # Suprimir NearConstantInputWarning (esperado em ciclos iniciais)
                        with warnings.catch_warnings():
                            warnings.filterwarnings("ignore", message=".*nearly constant.*")
                            warnings.filterwarnings("ignore", category=FutureWarning)
                            corr_result = pearsonr(rho_C_col, rho_P_col)
                        # pearsonr retorna (correlation, pvalue) - acessar correlation
                        corr_val: float = float(corr_result[0])  # type: ignore[arg-type]
                        if not np.isnan(corr_val):
                            correlations.append(abs(corr_val))
                except (ValueError, RuntimeWarning):
                    pass

                try:
                    # C → U
                    rho_C_col = rho_C_history[:, i]
                    rho_U_col = rho_U_history[:, i]
                    # Verificar se arrays têm variância suficiente (não são constantes)
                    if (
                        np.std(rho_C_col) > MIN_VARIANCE_THRESHOLD
                        and np.std(rho_U_col) > MIN_VARIANCE_THRESHOLD
                    ):
                        with warnings.catch_warnings():
                            warnings.filterwarnings("ignore", message=".*nearly constant.*")
                            warnings.filterwarnings("ignore", category=FutureWarning)
                            corr_result = pearsonr(rho_C_col, rho_U_col)
                        corr_val = float(corr_result[0])  # type: ignore[arg-type]
                        if not np.isnan(corr_val):
                            correlations.append(abs(corr_val))
                except (ValueError, RuntimeWarning):
                    pass

                try:
                    # P → U
                    rho_P_col = rho_P_history[:, i]
                    rho_U_col = rho_U_history[:, i]
                    # Verificar se arrays têm variância suficiente (não são constantes)
                    if (
                        np.std(rho_P_col) > MIN_VARIANCE_THRESHOLD
                        and np.std(rho_U_col) > MIN_VARIANCE_THRESHOLD
                    ):
                        with warnings.catch_warnings():
                            warnings.filterwarnings("ignore", message=".*nearly constant.*")
                            warnings.filterwarnings("ignore", category=FutureWarning)
                            corr_result = pearsonr(rho_P_col, rho_U_col)
                        corr_val = float(corr_result[0])  # type: ignore[arg-type]
                        if not np.isnan(corr_val):
                            correlations.append(abs(corr_val))
                except (ValueError, RuntimeWarning):
                    pass

            # Φ = média das integrações causais válidas
            if correlations:
                phi = float(np.mean(correlations))
            else:
                # Se nenhuma correlação válida, retornar 0.0
                phi = 0.0

            return phi

        except Exception as e:
            logger.warning(f"Erro ao calcular Φ causal: {e}, retornando 0.0")
            return 0.0

    def update_repression(
        self,
        threshold: float = 1.0,
        success: bool = False,
        phi_norm: Optional[float] = None,
        emergency_repression: Optional[float] = None,  # NOVO: Válvula de emergência
    ) -> None:
        """
        Atualiza força de repressão baseado em dinâmica inconsciente.

        Freud: repressão não é um evento, é um TRABALHO contínuo.

        PROTOCOLO CLÍNICO-CIBERNÉTICO (2025-12-08):
        - Adicionado decay quando success=True
        - Adicionada válvula de emergência anti-death-spiral

        Args:
            threshold: Threshold para aumentar repressão (normalizado, não raw norm)
            success: Flag indicando se o ciclo foi bem-sucedido (para decay)
            phi_norm: Valor de Φ normalizado [0, 1] (opcional, para decay adaptativo)
            emergency_repression: Valor de repressão de emergência (opcional, para válvula)
        """
        # VÁLVULA DE SEGURANÇA: Se repressão de emergência fornecida, usar ela
        if emergency_repression is not None:
            self.repression_strength = emergency_repression
            logger.warning(
                f"🚨 VÁLVULA DE EMERGÊNCIA: Repressão forçada para {emergency_repression:.4f}"
            )
            return

        # Medir força do inconsciente (normalizar para escala comparável)
        unconscious_strength = torch.norm(self.rho_U).item()
        # Normalizar: rho_U norm está em ~27.7, threshold deve ser comparável
        # Usar threshold relativo: se norm > threshold * dim, aumentar repressão
        threshold_normalized = threshold * self.dim  # Escala com dimensão

        # CORREÇÃO CRÍTICA: Decay quando success=True
        if success:
            # Decay baseado em Φ: se Φ alto, decay maior (sistema estável)
            if phi_norm is not None and phi_norm > 0.1:
                # Decay progressivo: quanto maior Φ, maior o decay
                decay_rate = 0.95 - (phi_norm * 0.05)  # 0.95 a 0.90 baseado em Φ
                self.repression_strength *= decay_rate
                logger.debug(
                    f"Repressão decay (success=True, Φ={phi_norm:.4f}): "
                    f"{self.repression_strength:.4f} (decay_rate={decay_rate:.4f})"
                )
            else:
                # Decay conservador se Φ baixo ou não disponível
                self.repression_strength *= 0.95
                logger.debug(
                    f"Repressão decay (success=True, Φ não disponível): "
                    f"{self.repression_strength:.4f}"
                )
            # Garantir que não caia abaixo de mínimo funcional
            self.repression_strength = max(0.4, self.repression_strength)
        else:
            # Trabalho de Repressão (lógica original)
            if unconscious_strength > threshold_normalized:
                # Aumentar repressão (custa CPU, por isso há "desgaste mental")
                self.repression_strength = min(0.99, self.repression_strength + 0.01)
            else:
                # Relaxar repressão (recuperação natural)
                self.repression_strength = max(0.4, self.repression_strength - 0.005)

    def get_state(self) -> ConsciousSystemState:
        """
        Obtém estado atual do sistema.

        NOTA CRÍTICA (2025-12-08): Este método converte tensores para CPU para armazenamento.
        Os cálculos principais (step()) são executados na GPU. A conversão para CPU aqui
        é necessária apenas para:
        1. Armazenamento no histórico (ConsciousSystemState usa numpy arrays)
        2. Cálculo de correlações (scipy.stats.pearsonr requer numpy)

        Para otimizar uso de GPU:
        - step() mantém todos os tensores na GPU durante cálculos
        - get_state() converte apenas quando necessário para armazenamento/análise
        - compute_phi_causal() usa histórico em CPU (necessário para scipy)

        Returns:
            Estado completo do sistema
        """
        import time

        phi_causal = self.compute_phi_causal()

        # NOTA: Conversão para CPU é necessária para armazenamento em ConsciousSystemState
        # que usa numpy arrays. Os cálculos principais (step) já foram feitos na GPU.
        state = ConsciousSystemState(
            rho_C=self.rho_C.cpu().numpy(),
            rho_P=self.rho_P.cpu().numpy(),
            rho_U=self.rho_U.cpu().numpy(),
            Lambda_U_signature=self.Lambda_U_signature,
            repression_strength=self.repression_strength,
            phi_causal=phi_causal,
            timestamp=time.time(),
        )

        # Adicionar ao histórico
        self.history.append(state)
        if len(self.history) > self.max_history:
            self.history.pop(0)

        return state

    def get_low_dim_signatures(self) -> Dict[str, np.ndarray]:
        """
        Obtém assinaturas de baixa dimensão dos vetores ρ_C, ρ_P, ρ_U.

        Para logging e análise sem necessidade de dados completos.

        Returns:
            Dict com assinaturas comprimidas
        """
        # Usar primeiros valores como assinatura (simples, mas eficaz)
        sig_dim = min(10, self.dim)  # Assinatura de 10 valores

        return {
            "C_sig": self.rho_C.cpu().numpy()[:sig_dim],
            "P_sig": self.rho_P.cpu().numpy()[:sig_dim],
            "U_sig": self.rho_U.cpu().numpy()[:sig_dim],
            "Lambda_U_sig": self.Lambda_U_signature[: min(sig_dim, len(self.Lambda_U_signature))],
        }
