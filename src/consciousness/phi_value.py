"""
PhiValue - Value Object para Φ (Phi) com tipagem explícita de unidade.

Este módulo implementa um Value Object que garante que Φ seja sempre tratado
em nats (unidade de informação), evitando confusão dimensional.

Baseado em:
- IIT 3.0/4.0 (Tononi, G., & Koch, C., 2015)
- Padrão PyPhi (subsystem.phi vs subsystem.normalized_phi)

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Protocolo: Livewire FASE 1
"""

from dataclasses import dataclass
from typing import Optional

from src.consciousness.phi_constants import (
    PHI_THRESHOLD,
    denormalize_phi,
    normalize_phi,
)


@dataclass(frozen=True)
class PhiValue:
    """
    Value Object para Φ (Phi) em nats.

    Garante que Φ seja sempre tratado em nats (unidade de informação),
    evitando confusão dimensional entre nats e normalizado [0,1].

    Attributes:
        nats: Valor de Φ em nats (unidade de informação)
        source: Origem do valor (opcional, para rastreabilidade)
    """

    nats: float
    source: Optional[str] = None

    def __post_init__(self) -> None:
        """Valida que nats está em range razoável."""
        if self.nats < 0.0:
            raise ValueError(f"PhiValue.nats deve ser >= 0, recebido: {self.nats}")
        # Não limitar superiormente - Φ pode ser > 1.0 em redes complexas
        # (IIT 3.0/4.0: não tem teto fixo)

    @property
    def normalized(self) -> float:
        """
        Retorna Φ normalizado [0, 1] para visualização/funções de ativação.

        NÃO usar para cálculos de integração - sempre usar .nats para isso.

        Usa normalização sigmoidal suave (não linear abrupta) conforme Protocolo Livewire.
        """
        return normalize_phi(self.nats)

    @property
    def as_normalized_sigmoid(self) -> float:
        """
        Retorna Φ normalizado usando sigmóide suave (Protocolo Livewire).

        Fórmula: 1 / (1 + exp(-K * (value_nats - M)))
        - K = 20.0 (constante de inclinação, ajustado conforme proposta)
        - M = 0.05 (ponto médio - limiar típico de consciência humana basal)

        Usar para funções de ativação que requerem suavidade.
        Baseado em ativação neuronal (Protocolo Livewire - VARREDURA_COMPLEMENTAR_SENIOR).
        """
        import math

        K = 20.0  # Declividade (ajustado de 10 para 20 conforme proposta)
        M = 0.05  # Ponto médio (limiar típico de consciência humana basal)
        return 1.0 / (1.0 + math.exp(-K * (self.nats - M)))

    @property
    def is_conscious(self) -> bool:
        """
        Verifica se Φ está acima do limiar de consciência.

        Returns:
            True se Φ >= PHI_THRESHOLD (0.01 nats)
        """
        return self.nats >= PHI_THRESHOLD

    @property
    def is_transitional(self) -> bool:
        """
        Verifica se Φ está em estado transicional.

        Returns:
            True se 0.001 <= Φ < 0.01 nats
        """
        return 0.001 <= self.nats < PHI_THRESHOLD

    @property
    def is_non_conscious(self) -> bool:
        """
        Verifica se Φ está abaixo do limiar de consciência.

        Returns:
            True se Φ < 0.001 nats
        """
        return self.nats < 0.001

    def __float__(self) -> float:
        """
        Permite conversão implícita para float (retorna nats).

        WARNING: Use explicitamente .nats ou .normalized para clareza.
        """
        return self.nats

    def __str__(self) -> str:
        """Representação string com unidade explícita."""
        source_str = f" (source: {self.source})" if self.source else ""
        return f"PhiValue({self.nats:.6f} nats{source_str})"

    def __repr__(self) -> str:
        """Representação para debug."""
        return f"PhiValue(nats={self.nats:.6f}, source={self.source!r})"

    @classmethod
    def from_nats(cls, nats: float, source: Optional[str] = None) -> "PhiValue":
        """
        Cria PhiValue a partir de valor em nats.

        Args:
            nats: Valor de Φ em nats
            source: Origem do valor (opcional)

        Returns:
            PhiValue
        """
        return cls(nats=nats, source=source)

    @classmethod
    def from_normalized(cls, normalized: float, source: Optional[str] = None) -> "PhiValue":
        """
        Cria PhiValue a partir de valor normalizado [0, 1].

        Args:
            normalized: Valor de Φ normalizado [0, 1]
            source: Origem do valor (opcional)

        Returns:
            PhiValue em nats

        WARNING: Use apenas quando souber que o valor está normalizado.
        """
        nats = denormalize_phi(normalized)
        return cls(nats=nats, source=source)

    @classmethod
    def zero(cls, source: Optional[str] = None) -> "PhiValue":
        """
        Cria PhiValue zero (sistema desintegrado).

        Args:
            source: Origem do valor (opcional)

        Returns:
            PhiValue com nats=0.0
        """
        return cls(nats=0.0, source=source)

    def __add__(self, other: "PhiValue") -> "PhiValue":
        """Soma dois PhiValues (retorna novo objeto)."""
        if not isinstance(other, PhiValue):
            raise TypeError(f"Cannot add PhiValue with {type(other)}")
        return PhiValue(nats=self.nats + other.nats, source=f"{self.source}+{other.source}")

    def __sub__(self, other: "PhiValue") -> "PhiValue":
        """Subtrai dois PhiValues (retorna novo objeto)."""
        if not isinstance(other, PhiValue):
            raise TypeError(f"Cannot subtract PhiValue with {type(other)}")
        return PhiValue(
            nats=max(0.0, self.nats - other.nats),
            source=f"{self.source}-{other.source}",
        )

    def __mul__(self, scalar: float) -> "PhiValue":
        """Multiplica PhiValue por escalar (retorna novo objeto)."""
        if not isinstance(scalar, (int, float)):
            raise TypeError(f"Cannot multiply PhiValue with {type(scalar)}")
        return PhiValue(nats=self.nats * scalar, source=self.source)

    def __truediv__(self, scalar: float) -> "PhiValue":
        """Divide PhiValue por escalar (retorna novo objeto)."""
        if not isinstance(scalar, (int, float)):
            raise TypeError(f"Cannot divide PhiValue with {type(scalar)}")
        if scalar == 0:
            raise ValueError("Cannot divide PhiValue by zero")
        return PhiValue(nats=self.nats / scalar, source=self.source)

    def __lt__(self, other: "PhiValue") -> bool:
        """Compara se self < other."""
        if not isinstance(other, PhiValue):
            raise TypeError(f"Cannot compare PhiValue with {type(other)}")
        return self.nats < other.nats

    def __le__(self, other: "PhiValue") -> bool:
        """Compara se self <= other."""
        if not isinstance(other, PhiValue):
            raise TypeError(f"Cannot compare PhiValue with {type(other)}")
        return self.nats <= other.nats

    def __gt__(self, other: "PhiValue") -> bool:
        """Compara se self > other."""
        if not isinstance(other, PhiValue):
            raise TypeError(f"Cannot compare PhiValue with {type(other)}")
        return self.nats > other.nats

    def __ge__(self, other: "PhiValue") -> bool:
        """Compara se self >= other."""
        if not isinstance(other, PhiValue):
            raise TypeError(f"Cannot compare PhiValue with {type(other)}")
        return self.nats >= other.nats


__all__ = ["PhiValue"]
