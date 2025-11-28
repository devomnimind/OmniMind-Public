"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Thermodynamic Attention Mechanism - Entropy-Based Attention

Implements attention weights determined by local entropy gradients
following the second law of thermodynamics (maximize ΔS).

Based on:
- Second law of thermodynamics (entropy maximization)
- Shannon entropy: H(X) = -Σ p(x) log p(x)
- Information-theoretic attention
- Thermodynamic optimization principles

This enables attention driven by information gain rather than similarity.

Author: OmniMind Development Team
License: MIT
"""

from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING, Any, Optional, cast

if TYPE_CHECKING:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch import Tensor as TorchTensor
else:
    TorchTensor = Any

# Runtime imports
try:
    import torch  # noqa: F811
    import torch.nn as nn  # noqa: F811
    import torch.nn.functional as F  # noqa: F811

    TORCH_AVAILABLE = True
except (ImportError, OSError):
    TORCH_AVAILABLE = False
    torch = None  # type: ignore
    nn = None  # type: ignore
    F = None  # type: ignore

logger = logging.getLogger(__name__)

# Constants
MIN_ENTROPY = 1e-10
DEFAULT_TEMPERATURE = 1.0
ENTROPY_EPSILON = 1e-12


class ThermodynamicAttention(nn.Module if TORCH_AVAILABLE else object):  # type: ignore
    """
    Attention mechanism driven by entropy gradients.

    Instead of computing attention via query-key similarity,
    this mechanism directs attention to regions that maximize
    entropy increase (second law of thermodynamics).

    Key principle: System naturally attends to information-rich regions
    that maximize knowledge gain (ΔS > 0).
    """

    def __init__(
        self,
        embed_dim: int,
        temperature: float = DEFAULT_TEMPERATURE,
        entropy_weight: float = 1.0,
    ) -> None:
        """
        Initialize thermodynamic attention.

        Args:
            embed_dim: Embedding dimension
            temperature: Temperature for softmax (controls exploration)
            entropy_weight: Weight for entropy gradient term
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch not available. ThermodynamicAttention requires torch.")

        super().__init__()

        self.embed_dim = embed_dim
        self.temperature = temperature
        self.entropy_weight = entropy_weight

        # Learnable parameters for entropy computation
        self.entropy_projection = nn.Linear(embed_dim, embed_dim)

        logger.info(f"ThermodynamicAttention initialized: " f"dim={embed_dim}, T={temperature}")

    def forward(
        self,
        query: TorchTensor,
        key: TorchTensor,
        value: TorchTensor,
        mask: Optional[TorchTensor] = None,
    ) -> TorchTensor:
        """
        Forward pass with entropy-based attention.

        Args:
            query: Query tensor [batch, seq_len, embed_dim]
            key: Key tensor [batch, seq_len, embed_dim]
            value: Value tensor [batch, seq_len, embed_dim]
            mask: Optional attention mask

        Returns:
            Output tensor [batch, seq_len, embed_dim]
        """
        batch_size, seq_len, _ = key.shape

        # Compute local entropy for each key position
        entropies = self._local_entropy(key)  # [batch, seq_len]

        # Compute entropy gradients (ΔS direction)
        entropy_gradients = self._compute_entropy_gradients(entropies)  # [batch, seq_len]

        # Standard similarity-based attention scores
        # Scale by 1/sqrt(d_k) for numerical stability
        similarity_scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(self.embed_dim)

        # Combine similarity with entropy gradient
        # Second law: attend to high entropy gradients
        combined_scores = similarity_scores + self.entropy_weight * entropy_gradients.unsqueeze(1)

        # Apply mask if provided
        if mask is not None:
            combined_scores = combined_scores.masked_fill(mask == 0, float("-inf"))

        # Temperature-scaled softmax
        # Higher temperature = more exploration (flatter distribution)
        attention_weights = F.softmax(combined_scores / self.temperature, dim=-1)

        # Apply attention to values
        output = torch.matmul(attention_weights, value)

        return output

    def _local_entropy(self, representations: TorchTensor) -> TorchTensor:
        """
        Compute local Shannon entropy for each position.

        Entropy measures information content:
        H(X) = -Σ p(x) log p(x)

        Args:
            representations: Input representations [batch, seq_len, embed_dim]

        Returns:
            Local entropies [batch, seq_len]
        """
        batch_size, seq_len, embed_dim = representations.shape

        # Project to entropy computation space
        projected = self.entropy_projection(representations)

        # Compute probability distribution per position
        # Use softmax over embedding dimension
        probs = F.softmax(projected, dim=-1)

        # Shannon entropy: H = -Σ p log p
        # Add epsilon to avoid log(0)
        log_probs = torch.log(probs + ENTROPY_EPSILON)
        entropies = -torch.sum(probs * log_probs, dim=-1)

        return entropies

    def _compute_entropy_gradients(self, entropies: TorchTensor) -> TorchTensor:
        """
        Compute gradients of entropy (direction of maximum ΔS).

        Second law: System naturally evolves toward entropy increase.
        We attend to positions with highest entropy gradients.

        Args:
            entropies: Local entropies [batch, seq_len]

        Returns:
            Entropy gradients [batch, seq_len]
        """
        # Compute finite differences (discrete gradient)
        # gradient[i] ≈ (entropy[i+1] - entropy[i-1]) / 2

        batch_size, seq_len = entropies.shape

        if seq_len < 2:
            # Not enough points for gradient
            return torch.zeros_like(entropies)

        # Pad for boundary conditions
        padded = F.pad(entropies, (1, 1), mode="replicate")

        # Central differences
        gradients = (padded[:, 2:] - padded[:, :-2]) / 2.0

        return gradients

    def adjust_temperature(self, new_temperature: float) -> None:
        """
        Adjust temperature (exploration vs exploitation).

        Args:
            new_temperature: New temperature value
        """
        self.temperature = max(new_temperature, MIN_ENTROPY)
        logger.debug(f"Temperature adjusted to {self.temperature:.4f}")


class MultiHeadThermodynamicAttention(nn.Module if TORCH_AVAILABLE else object):  # type: ignore
    """
    Multi-head thermodynamic attention.

    Multiple attention heads with different temperature settings
    for diverse information-seeking behavior.
    """

    def __init__(
        self,
        embed_dim: int,
        num_heads: int = 8,
        base_temperature: float = 1.0,
        dropout: float = 0.1,
    ) -> None:
        """
        Initialize multi-head thermodynamic attention.

        Args:
            embed_dim: Embedding dimension
            num_heads: Number of attention heads
            base_temperature: Base temperature (scaled per head)
            dropout: Dropout rate
        """
        if not TORCH_AVAILABLE:
            raise ImportError(
                "PyTorch not available. MultiHeadThermodynamicAttention " "requires torch."
            )

        super().__init__()

        assert embed_dim % num_heads == 0, "embed_dim must be divisible by num_heads"

        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads

        # Linear projections
        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)

        # Create attention heads with varying temperatures
        self.attention_heads = nn.ModuleList(
            [
                ThermodynamicAttention(
                    embed_dim=self.head_dim,
                    temperature=base_temperature * (1.0 + i * 0.2),
                    entropy_weight=1.0,
                )
                for i in range(num_heads)
            ]
        )

        self.dropout = nn.Dropout(dropout)

        logger.info(
            f"MultiHeadThermodynamicAttention initialized: " f"{num_heads} heads, dim={embed_dim}"
        )

    def forward(
        self,
        query: TorchTensor,
        key: TorchTensor,
        value: TorchTensor,
        mask: Optional[TorchTensor] = None,
    ) -> TorchTensor:
        """
        Multi-head forward pass.

        Args:
            query: Query tensor [batch, seq_len, embed_dim]
            key: Key tensor [batch, seq_len, embed_dim]
            value: Value tensor [batch, seq_len, embed_dim]
            mask: Optional attention mask

        Returns:
            Output tensor [batch, seq_len, embed_dim]
        """
        batch_size, seq_len, _ = query.shape

        # Project Q, K, V
        Q = self.q_proj(query)
        K = self.k_proj(key)
        V = self.v_proj(value)

        # Reshape for multi-head attention
        # [batch, seq_len, embed_dim] -> [batch, num_heads, seq_len, head_dim]
        Q = Q.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        K = K.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        V = V.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)

        # Apply attention for each head
        head_outputs: list[TorchTensor] = []
        for i, attention_head in enumerate(self.attention_heads):
            # Extract head-specific Q, K, V
            Q_head = Q[:, i, :, :]  # [batch, seq_len, head_dim]
            K_head = K[:, i, :, :]
            V_head = V[:, i, :, :]

            # Apply thermodynamic attention
            head_output = attention_head(Q_head, K_head, V_head, mask)
            head_outputs.append(head_output)

        # Concatenate heads
        # [batch, num_heads, seq_len, head_dim] -> [batch, seq_len, embed_dim]
        concat_output = torch.stack(head_outputs, dim=1)
        concat_output = concat_output.transpose(1, 2).contiguous()
        concat_output = concat_output.view(batch_size, seq_len, self.embed_dim)

        # Final projection
        output = self.out_proj(concat_output)
        output = self.dropout(output)

        return cast(TorchTensor, output)
