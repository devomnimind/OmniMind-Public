"""
Tests for Thermodynamic Attention mechanism.

Tests entropy-based attention, temperature control,
and multi-head thermodynamic attention.
"""

import numpy as np
import pytest

try:
    import torch

    TORCH_AVAILABLE = True
except (ImportError, OSError):
    TORCH_AVAILABLE = False

# Skip all tests if torch not available
pytestmark = pytest.mark.skipif(
    not TORCH_AVAILABLE, reason="PyTorch not available"
)

if TORCH_AVAILABLE:
    from src.attention.thermodynamic_attention import (
        MultiHeadThermodynamicAttention,
        ThermodynamicAttention,
    )


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="PyTorch not available")
class TestThermodynamicAttention:
    """Test thermodynamic attention mechanism."""

    def test_initialization(self) -> None:
        """Test attention initializes correctly."""
        attention = ThermodynamicAttention(embed_dim=64, temperature=1.0)

        assert attention.embed_dim == 64
        assert attention.temperature == 1.0

    def test_forward_pass(self) -> None:
        """Test forward pass."""
        attention = ThermodynamicAttention(embed_dim=32)

        batch_size, seq_len = 2, 10
        query = torch.randn(batch_size, seq_len, 32)
        key = torch.randn(batch_size, seq_len, 32)
        value = torch.randn(batch_size, seq_len, 32)

        output = attention(query, key, value)

        assert output.shape == (batch_size, seq_len, 32)

    def test_local_entropy_calculation(self) -> None:
        """Test local entropy computation."""
        attention = ThermodynamicAttention(embed_dim=16)

        representations = torch.randn(2, 5, 16)
        entropies = attention._local_entropy(representations)

        assert entropies.shape == (2, 5)
        assert torch.all(entropies >= 0)  # Entropy is non-negative

    def test_entropy_gradients(self) -> None:
        """Test entropy gradient computation."""
        attention = ThermodynamicAttention(embed_dim=16)

        entropies = torch.tensor([[1.0, 2.0, 3.0, 2.5, 2.0]])
        gradients = attention._compute_entropy_gradients(entropies)

        assert gradients.shape == entropies.shape

    def test_temperature_adjustment(self) -> None:
        """Test temperature can be adjusted."""
        attention = ThermodynamicAttention(embed_dim=32, temperature=1.0)

        attention.adjust_temperature(2.0)

        assert attention.temperature == 2.0

    def test_with_mask(self) -> None:
        """Test attention with mask."""
        attention = ThermodynamicAttention(embed_dim=32)

        batch_size, seq_len = 2, 8
        query = torch.randn(batch_size, seq_len, 32)
        key = torch.randn(batch_size, seq_len, 32)
        value = torch.randn(batch_size, seq_len, 32)

        # Create mask (attend only to first half)
        mask = torch.ones(batch_size, seq_len, seq_len)
        mask[:, :, seq_len // 2 :] = 0

        output = attention(query, key, value, mask=mask)

        assert output.shape == (batch_size, seq_len, 32)


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="PyTorch not available")
class TestMultiHeadThermodynamicAttention:
    """Test multi-head thermodynamic attention."""

    def test_initialization(self) -> None:
        """Test multi-head attention initializes correctly."""
        attention = MultiHeadThermodynamicAttention(
            embed_dim=64, num_heads=8
        )

        assert attention.embed_dim == 64
        assert attention.num_heads == 8
        assert attention.head_dim == 8

    def test_forward_pass(self) -> None:
        """Test multi-head forward pass."""
        attention = MultiHeadThermodynamicAttention(
            embed_dim=64, num_heads=4
        )

        batch_size, seq_len = 2, 10
        query = torch.randn(batch_size, seq_len, 64)
        key = torch.randn(batch_size, seq_len, 64)
        value = torch.randn(batch_size, seq_len, 64)

        output = attention(query, key, value)

        assert output.shape == (batch_size, seq_len, 64)

    def test_different_head_temperatures(self) -> None:
        """Test that heads have different temperatures."""
        attention = MultiHeadThermodynamicAttention(
            embed_dim=32, num_heads=4, base_temperature=1.0
        )

        temperatures = [
            head.temperature for head in attention.attention_heads
        ]

        # Each head should have different temperature
        assert len(set(temperatures)) > 1


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="PyTorch not available")
class TestIntegration:
    """Integration tests for thermodynamic attention."""

    def test_attention_output_depends_on_entropy(self) -> None:
        """Test that attention is influenced by entropy."""
        attention = ThermodynamicAttention(
            embed_dim=32, entropy_weight=10.0
        )

        batch_size, seq_len = 1, 5

        # Create data with varying entropy
        # Uniform distribution = low entropy
        low_entropy = torch.ones(batch_size, seq_len, 32) * 0.5

        # Random distribution = high entropy
        high_entropy = torch.randn(batch_size, seq_len, 32)

        query = torch.randn(batch_size, seq_len, 32)
        value = torch.randn(batch_size, seq_len, 32)

        # Run with low entropy keys
        output_low = attention(query, low_entropy, value)

        # Run with high entropy keys  
        output_high = attention(query, high_entropy, value)

        # Outputs should be different (entropy affects attention)
        assert not torch.allclose(output_low, output_high, atol=0.1)

    def test_gradient_flow(self) -> None:
        """Test that gradients flow through attention."""
        attention = ThermodynamicAttention(embed_dim=32)

        query = torch.randn(1, 5, 32, requires_grad=True)
        key = torch.randn(1, 5, 32, requires_grad=True)
        value = torch.randn(1, 5, 32, requires_grad=True)

        output = attention(query, key, value)
        loss = output.sum()
        loss.backward()

        # Check gradients exist
        assert query.grad is not None
        assert key.grad is not None
        assert value.grad is not None
