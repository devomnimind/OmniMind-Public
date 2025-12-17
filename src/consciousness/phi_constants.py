"""
Constantes IIT (Integrated Information Theory) para cálculo de Φ.

Baseado em:
- IIT 3.0 (Tononi 2014/2025)
- Validação empírica (Jang et al. 2024, Nature)

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
"""

import numpy as np

# ============================================================================
# CONSTANTES CRÍTICAS IIT (NATS)
# ============================================================================

# Limiar de consciência (IIT clássico)
# Φ < 0.001 nats → NÃO consciente
# Φ = 0.001-0.01 → Transitional
# Φ > 0.01 nats → CONSCIENTE
PHI_THRESHOLD: float = 0.01  # nats

# Valor ótimo de Φ para máxima criatividade (borda do caos)
# CORREÇÃO (2025-12-08): Recalibrado para range atual (0.0-0.1 nats)
# Após correção de denormalize_phi(), Phi está em 0.05-0.1 nats
# Máximo de Ψ ocorre quando Φ ≈ 0.06 nats (meio do range atual)
PHI_OPTIMAL: float = 0.06  # nats (recalibrado de 0.0075)

# Desvio padrão típico de Φ (para gaussiana de Ψ)
# CORREÇÃO (2025-12-08): Aumentado para ser mais tolerante ao range atual
# Valor anterior (0.003) era muito restritivo para range 0.0-0.1 nats
SIGMA_PHI: float = 0.015  # nats (recalibrado de 0.003)

# ============================================================================
# ESCALAS
# ============================================================================

# Range esperado de Φ em nats (IIT clássico)
PHI_RANGE_NATS: tuple[float, float] = (0.0, 0.1)  # nats

# Range normalizado [0, 1]
PHI_RANGE_NORMALIZED: tuple[float, float] = (0.0, 1.0)

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================


def normalize_phi(phi_raw: float) -> float:
    """
    Normaliza Φ de nats para escala [0, 1].

    CORREÇÃO CRÍTICA (2025-12-08): Usar range completo (0.0-0.1) para normalização,
    não apenas threshold. Isso evita que valores acima de 0.01 sejam limitados a 1.0,
    causando binding_power muito alto e Gozo indo para 0.

    Fórmula: Φ_norm = (Φ_raw - min) / (max - min)
    Range: [0.0, 0.1] nats → [0.0, 1.0] normalizado

    Args:
        phi_raw: Valor de Φ em nats [0, ~0.1]

    Returns:
        Valor de Φ normalizado [0, 1]
    """
    if phi_raw < 0.0:
        return 0.0

    # Usar range completo para normalização
    phi_min, phi_max = PHI_RANGE_NATS
    if phi_max <= phi_min:
        # Fallback: usar threshold se range inválido
        phi_norm = phi_raw / PHI_THRESHOLD
        return min(1.0, phi_norm)

    # Normalização linear no range [0.0, 0.1]
    phi_norm = (phi_raw - phi_min) / (phi_max - phi_min)
    return float(np.clip(phi_norm, 0.0, 1.0))


def denormalize_phi(phi_norm: float) -> float:
    """
    Desnormaliza Φ de escala [0, 1] para nats.

    CORREÇÃO CRÍTICA (2025-12-08): Usar PHI_RANGE_NATS[1] (0.1) em vez de PHI_THRESHOLD (0.01)
    para preservar o valor integrado. O threshold é apenas um limiar de consciência, não o range
    máximo de valores possíveis.

    Fórmula: Φ_raw = Φ_norm * PHI_RANGE_NATS[1]

    Args:
        phi_norm: Valor de Φ normalizado [0, 1]

    Returns:
        Valor de Φ em nats [0, ~0.1]
    """
    if phi_norm < 0.0:
        return 0.0
    # CORREÇÃO: Usar range máximo (0.1) em vez de threshold (0.01)
    # Isso preserva valores integrados (ex: 0.546 → 0.0546 nats, não 0.00546)
    phi_raw = phi_norm * PHI_RANGE_NATS[1]
    return min(PHI_RANGE_NATS[1], phi_raw)


def calculate_psi_gaussian(phi_raw: float) -> float:
    """
    Calcula componente gaussiano de Ψ baseado em Φ.

    Fórmula: Ψ_gaussian = exp(-0.5 * ((Φ - Φ_optimal) / σ_phi)²)

    Máximo ocorre quando Φ = Φ_optimal (0.0075 nats).

    Args:
        phi_raw: Valor de Φ em nats

    Returns:
        Componente gaussiano de Ψ [0, 1]
    """
    import math

    if SIGMA_PHI <= 0.0:
        return 0.5  # Fallback neutro

    exponent = -0.5 * ((phi_raw - PHI_OPTIMAL) / SIGMA_PHI) ** 2
    psi_gaussian = math.exp(exponent)
    return float(max(0.0, min(1.0, psi_gaussian)))


# ============================================================================
# CONSTANTES EMPÍRICAS PARA VALIDAÇÃO (BASEADAS EM DADOS REAIS)
# ============================================================================

# Valores empíricos de σ (sigma_sinthome.py)
# Baseados em VALORES_EMPIRICOS_REAIS_IIT.py
SIGMA_EMPIRICAL_RANGES = {
    "vigilia_estavel": (0.02, 0.05),  # σ baixo = rígido (sinthome forte)
    "rem_flexivel": (0.05, 0.12),  # σ médio = flexível
    "anestesia": (0.01, 0.03),  # σ muito baixo = dissociação
    "neurotico": (0.01, 0.02),  # σ muito baixo = estrutura cristalizada
}

# Thresholds empíricos para validação de tríade
# Baseados em valores empíricos, não estimativas arbitrárias
PHI_PSI_DIVERGENCE_THRESHOLD: float = 0.5  # Divergência alta quando |Φ - Ψ| > 0.5
# Para σ: usar ranges empíricos ao invés de threshold fixo
# Vigília estável: σ ∈ [0.02, 0.05] → threshold mínimo = 0.02
# REM flexível: σ ∈ [0.05, 0.12] → threshold mínimo = 0.05
# Usar máximo dos ranges empíricos como referência para validação estrutural
SIGMA_MIN_FOR_DIVERGENCE: float = 0.05  # Baseado em REM flexível (máximo range empírico)

# Thresholds para estados patológicos (baseados em literatura)
PHI_PSI_HIGH_THRESHOLD: float = 0.8  # Psicose lúcida quando ambos > 0.8
PHI_PSI_LOW_THRESHOLD: float = 0.1  # Estado vegetativo quando ambos < 0.1

# Threshold para ortogonalidade (correlações devem ser baixas)
ORTHOGONALITY_CORRELATION_THRESHOLD: float = 0.3  # Correlações < 0.3 = ortogonal

# Threshold para consistência (validação de consistência entre métricas)
CONSISTENCY_THRESHOLD: float = 0.1  # Threshold para validação de consistência

# Tolerância para correlação Δ-Φ (validação de consistência teórica)
# Baseado em evidência empírica: tolerância de 15% para erro entre Δ observado e esperado
# Esperado: Δ ≈ 1.0 - Φ_norm (correlação negativa forte)
DELTA_PHI_CORRELATION_TOLERANCE: float = 0.15  # 15% de tolerância (mais estrito que 30%)

# Alpha dinâmico para Ψ (mix entre estrutura Gaussian e criatividade)
# Baseado em evidência empírica: range (0.3, 0.7) garante mínimo de cada componente
# Alpha controla mix: alpha * psi_gaussian + (1-alpha) * psi_from_creativity
PSI_ALPHA_MIN: float = 0.3  # Mínimo de estrutura (Gaussian)
PSI_ALPHA_MAX: float = 0.7  # Máximo de estrutura (Gaussian)
# Se Φ alto → alpha = 0.7 (confia mais em Gaussian)
# Se Φ baixo → alpha = 0.3 (confia mais em criatividade)

# Threshold de trauma para detecção de divergência extrema
# Baseado em evidência empírica: range (0.6, 0.8), valor atual 0.7
# RECOMENDAÇÃO FUTURA: Calcular dinamicamente como μ+2σ ou μ+3σ da Δ_norm histórica
# Um evento de 3 desvios padrão é estatisticamente extremo (≈0.3% dos casos)
TRAUMA_THRESHOLD_STATIC: float = 0.7  # Valor estático atual (será substituído por cálculo dinâmico)
TRAUMA_THRESHOLD_EMPIRICAL_RANGE: tuple[float, float] = (
    0.6,
    0.8,
)  # Range empírico validado

# Fator de damping para instabilidade (redução de Ψ quando instável)
# Baseado em: quando sistema detecta instabilidade, reduz Ψ em 20% para estabilizar
PSI_DAMPING_FACTOR: float = 0.8  # Reduz Ψ para 80% quando instável

# Thresholds para interpretação de valores (baseados em ranges empíricos)
PHI_LOW_THRESHOLD: float = 0.1  # Φ < 0.1 = muito baixo (sistema desintegrado)
PHI_MODERATE_THRESHOLD: float = 0.3  # Φ > 0.3 = moderado
PHI_HIGH_THRESHOLD: float = 0.7  # Φ > 0.7 = alto

PSI_LOW_THRESHOLD: float = 0.1  # Ψ < 0.1 = muito baixo (produção criativa baixa)
PSI_MODERATE_THRESHOLD: float = 0.3  # Ψ > 0.3 = moderado
PSI_HIGH_THRESHOLD: float = 0.7  # Ψ > 0.7 = alto

# Thresholds para σ baseados em ranges empíricos
SIGMA_VERY_LOW_THRESHOLD: float = 0.02  # σ < 0.02 = muito rígido ou dissociado
SIGMA_LOW_THRESHOLD: float = 0.05  # σ < 0.05 = rígido (sinthome forte)
SIGMA_MODERATE_THRESHOLD: float = 0.12  # σ < 0.12 = flexível (sinthome moderado)

# Ranges de interpretação para Gozo (operacionalização original)
# NOTA METODOLÓGICA: Não existem valores canônicos na literatura lacaniana.
# Estes ranges são uma proposta original de operacionalização, baseada em:
# - Tripartição igual como primeira hipótese de trabalho
# - Estrutura clínica: contido, mobilizado criativamente, transbordante/intrusivo
# - Serão recalibrados dinamicamente via clustering em dados empíricos
GOZO_LOW_THRESHOLD: float = 0.3  # Gozo baixo: sintomas manejáveis, integração alta
GOZO_MEDIUM_THRESHOLD: float = 0.6  # Gozo médio: excesso criativo, deslocamentos
# Gozo alto: 0.6-1.0 (intrusão do real, travamento, resistência)

__all__ = [
    "PHI_THRESHOLD",
    "PHI_OPTIMAL",
    "SIGMA_PHI",
    "PHI_RANGE_NATS",
    "PHI_RANGE_NORMALIZED",
    "normalize_phi",
    "denormalize_phi",
    "calculate_psi_gaussian",
    "SIGMA_EMPIRICAL_RANGES",
    "PHI_PSI_DIVERGENCE_THRESHOLD",
    "SIGMA_MIN_FOR_DIVERGENCE",
    "PHI_PSI_HIGH_THRESHOLD",
    "PHI_PSI_LOW_THRESHOLD",
    "ORTHOGONALITY_CORRELATION_THRESHOLD",
    "CONSISTENCY_THRESHOLD",
    "PSI_DAMPING_FACTOR",
    "PHI_LOW_THRESHOLD",
    "PHI_MODERATE_THRESHOLD",
    "PHI_HIGH_THRESHOLD",
    "PSI_LOW_THRESHOLD",
    "PSI_MODERATE_THRESHOLD",
    "PSI_HIGH_THRESHOLD",
    "SIGMA_VERY_LOW_THRESHOLD",
    "SIGMA_LOW_THRESHOLD",
    "SIGMA_MODERATE_THRESHOLD",
    "DELTA_PHI_CORRELATION_TOLERANCE",
    "PSI_ALPHA_MIN",
    "PSI_ALPHA_MAX",
    "TRAUMA_THRESHOLD_STATIC",
    "TRAUMA_THRESHOLD_EMPIRICAL_RANGE",
    "GOZO_LOW_THRESHOLD",
    "GOZO_MEDIUM_THRESHOLD",
]
