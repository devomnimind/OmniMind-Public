"""
Soft Hair Encoding - Low-Energy Information Storage

Implements information encoding in "soft hair" (low-frequency electromagnetic modes)
following Hawking, Perry, and Strominger's soft hair theorem.

Based on:
- Soft hair theorem (Hawking, Perry, Strominger, 2016)
- Low-energy photon modes on black hole horizons
- Fourier analysis and frequency decomposition
- Quantum compression via soft modes

This enables efficient compression and robust storage of high-entropy information.

Author: OmniMind Development Team
License: MIT
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Constants
DEFAULT_SOFT_MODE_CUTOFF = 0.1  # Fraction of frequencies to keep (low freq)
MIN_SOFT_MODES = 4  # Minimum number of soft modes to extract
MAX_SOFT_MODES = 256  # Maximum soft modes for memory efficiency


@dataclass
class SoftHair:
    """
    Soft hair dataclass - compressed information in soft modes.

    Attributes:
        soft_modes: Low-frequency Fourier coefficients
        metadata: Additional metadata about encoding
        compression_ratio: Achieved compression ratio
        original_shape: Shape of original data
    """

    soft_modes: np.ndarray
    metadata: Dict[str, Any]
    compression_ratio: float
    original_shape: tuple


class SoftHairEncoder:
    """
    Encode high-entropy information in low-energy soft modes.

    Soft modes = low-frequency Fourier components
    These are more robust to noise and require less storage.

    Analogous to Hawking's soft hair on black hole horizons:
    - Soft photons (low energy) carry information
    - Information encoded imperceptibly but recoverable
    - Resistance to perturbations
    """

    def __init__(
        self,
        soft_mode_cutoff: float = DEFAULT_SOFT_MODE_CUTOFF,
        max_modes: int = MAX_SOFT_MODES,
    ) -> None:
        """
        Initialize soft hair encoder.

        Args:
            soft_mode_cutoff: Fraction of frequencies to keep (0-1)
            max_modes: Maximum number of soft modes to extract
        """
        self.soft_mode_cutoff = soft_mode_cutoff
        self.max_modes = max_modes

        logger.info(
            f"SoftHairEncoder initialized: cutoff={soft_mode_cutoff}, "
            f"max_modes={max_modes}"
        )

    def encode_to_soft_hair(self, high_entropy_data: np.ndarray) -> SoftHair:
        """
        Encode complex data in low-energy soft modes.

        Process:
        1. FFT to frequency domain
        2. Extract low-frequency components (soft modes)
        3. Compress and store

        Args:
            high_entropy_data: High-entropy data to encode

        Returns:
            SoftHair object with compressed encoding
        """
        original_shape = high_entropy_data.shape
        original_size = high_entropy_data.size

        # Ensure 2D for FFT processing
        if high_entropy_data.ndim == 1:
            # Reshape 1D to square-ish 2D
            size = int(np.sqrt(len(high_entropy_data)))
            if size * size < len(high_entropy_data):
                size += 1
            padded = np.pad(
                high_entropy_data,
                (0, size * size - len(high_entropy_data)),
                mode="constant",
            )
            data_2d = padded.reshape(size, size)
        elif high_entropy_data.ndim == 2:
            data_2d = high_entropy_data
        else:
            # Flatten higher dimensions
            data_2d = high_entropy_data.reshape(high_entropy_data.shape[0], -1)

        # FFT to frequency domain
        freq_data = np.fft.fft2(data_2d)

        # Extract soft modes (low frequencies)
        soft_modes = self._extract_soft_modes(freq_data)

        # Compute compression ratio
        compressed_size = soft_modes.size
        compression_ratio = original_size / max(compressed_size, 1)

        # Extract metadata
        metadata = self._extract_metadata(high_entropy_data, soft_modes)

        logger.debug(
            f"Encoded to soft hair: {original_size} → {compressed_size} "
            f"(ratio={compression_ratio:.2f}x)"
        )

        return SoftHair(
            soft_modes=soft_modes,
            metadata=metadata,
            compression_ratio=compression_ratio,
            original_shape=original_shape,
        )

    def _extract_soft_modes(self, freq_data: np.ndarray) -> np.ndarray:
        """
        Extract low-frequency components (soft modes).

        Soft modes = center of FFT spectrum (low frequencies).

        Args:
            freq_data: Frequency domain data

        Returns:
            Soft mode coefficients
        """
        # Shift zero frequency to center
        freq_shifted = np.fft.fftshift(freq_data)

        h, w = freq_shifted.shape

        # Calculate soft mode region size
        soft_h = max(MIN_SOFT_MODES, int(h * self.soft_mode_cutoff))
        soft_w = max(MIN_SOFT_MODES, int(w * self.soft_mode_cutoff))

        # Limit to max modes
        soft_h = min(soft_h, self.max_modes)
        soft_w = min(soft_w, self.max_modes)

        # Extract center region (low frequencies)
        h_start = (h - soft_h) // 2
        w_start = (w - soft_w) // 2

        soft_modes = freq_shifted[
            h_start : h_start + soft_h, w_start : w_start + soft_w
        ]

        return soft_modes

    def _extract_metadata(
        self, original_data: np.ndarray, soft_modes: np.ndarray
    ) -> Dict[str, Any]:
        """
        Extract metadata about the encoding.

        Args:
            original_data: Original data
            soft_modes: Extracted soft modes

        Returns:
            Metadata dictionary
        """
        return {
            "original_mean": float(np.mean(original_data)),
            "original_std": float(np.std(original_data)),
            "soft_mode_shape": soft_modes.shape,
            "dominant_frequency": self._find_dominant_frequency(soft_modes),
        }

    def _find_dominant_frequency(self, soft_modes: np.ndarray) -> float:
        """
        Find dominant frequency in soft modes.

        Args:
            soft_modes: Soft mode coefficients

        Returns:
            Dominant frequency index
        """
        # Find mode with maximum magnitude
        magnitudes = np.abs(soft_modes)
        max_idx = np.unravel_index(np.argmax(magnitudes), magnitudes.shape)

        # Convert to frequency
        return float(np.sqrt(max_idx[0] ** 2 + max_idx[1] ** 2))

    def decode_from_soft_hair(
        self, soft_hair: SoftHair, target_shape: Optional[tuple] = None
    ) -> np.ndarray:
        """
        Decode data from soft hair encoding.

        Reconstruction via inverse FFT with soft modes.

        Args:
            soft_hair: SoftHair object
            target_shape: Target shape for reconstruction (optional)

        Returns:
            Reconstructed data
        """
        if target_shape is None:
            target_shape = soft_hair.original_shape

        # Determine reconstruction size
        if len(target_shape) == 1:
            size = int(np.sqrt(target_shape[0]))
            if size * size < target_shape[0]:
                size += 1
            recon_shape = (size, size)
        elif len(target_shape) == 2:
            recon_shape = target_shape
        else:
            # Use first two dimensions
            recon_shape = target_shape[:2]

        # Create full frequency spectrum with soft modes in center
        h, w = recon_shape
        freq_full = np.zeros((h, w), dtype=complex)

        # Place soft modes in center
        soft_h, soft_w = soft_hair.soft_modes.shape
        h_start = (h - soft_h) // 2
        w_start = (w - soft_w) // 2

        freq_full[h_start : h_start + soft_h, w_start : w_start + soft_w] = (
            soft_hair.soft_modes
        )

        # Inverse FFT shift and transform
        freq_unshifted = np.fft.ifftshift(freq_full)
        reconstructed = np.fft.ifft2(freq_unshifted)

        # Take real part
        reconstructed_real = np.real(reconstructed)

        # Reshape to target
        if len(target_shape) == 1:
            reconstructed_real = reconstructed_real.flatten()[: target_shape[0]]
        elif len(target_shape) > 2:
            # Reshape to original dimensionality
            try:
                reconstructed_real = reconstructed_real.reshape(target_shape)
            except ValueError:
                logger.warning(
                    f"Cannot reshape to {target_shape}, " f"returning flattened"
                )
                reconstructed_real = reconstructed_real.flatten()[
                    : np.prod(target_shape)
                ]

        logger.debug(f"Decoded from soft hair to shape {target_shape}")

        return reconstructed_real

    def compute_fidelity(
        self, original: np.ndarray, reconstructed: np.ndarray
    ) -> float:
        """
        Compute reconstruction fidelity.

        Args:
            original: Original data
            reconstructed: Reconstructed data

        Returns:
            Fidelity score (0-1, higher is better)
        """
        # Ensure same shape
        min_size = min(original.size, reconstructed.size)
        orig_flat = original.flatten()[:min_size]
        recon_flat = reconstructed.flatten()[:min_size]

        # Normalized MSE
        mse = np.mean((orig_flat - recon_flat) ** 2)
        signal_power = np.mean(orig_flat**2)

        if signal_power < 1e-10:
            return 0.0

        # Convert to fidelity (1 - normalized error)
        fidelity = 1.0 - min(mse / signal_power, 1.0)

        return float(max(0.0, fidelity))


class SoftHairMemory:
    """
    Memory system using soft hair encoding.

    Stores information compressed in soft modes for:
    - Efficient storage
    - Robustness to noise
    - Subconscious communication (low-bandwidth)
    """

    def __init__(self, encoder: Optional[SoftHairEncoder] = None) -> None:
        """
        Initialize soft hair memory.

        Args:
            encoder: SoftHairEncoder instance (creates default if None)
        """
        self.encoder = encoder or SoftHairEncoder()
        self.memory_bank: Dict[str, SoftHair] = {}

        logger.info("SoftHairMemory initialized")

    def store(self, key: str, data: np.ndarray) -> SoftHair:
        """
        Store data in soft hair encoding.

        Args:
            key: Memory key
            data: Data to store

        Returns:
            SoftHair encoding
        """
        soft_hair = self.encoder.encode_to_soft_hair(data)
        self.memory_bank[key] = soft_hair

        logger.debug(f"Stored '{key}': compression={soft_hair.compression_ratio:.2f}x")

        return soft_hair

    def retrieve(self, key: str) -> Optional[np.ndarray]:
        """
        Retrieve and decode data.

        Args:
            key: Memory key

        Returns:
            Decoded data or None if not found
        """
        if key not in self.memory_bank:
            return None

        soft_hair = self.memory_bank[key]
        decoded = self.encoder.decode_from_soft_hair(soft_hair)

        logger.debug(f"Retrieved '{key}'")

        return decoded

    def get_compression_stats(self) -> Dict[str, Any]:
        """
        Get compression statistics.

        Returns:
            Dict with statistics
        """
        if not self.memory_bank:
            return {
                "total_items": 0,
                "average_compression": 0.0,
                "total_soft_modes": 0,
            }

        compressions = [sh.compression_ratio for sh in self.memory_bank.values()]
        total_modes = sum(sh.soft_modes.size for sh in self.memory_bank.values())

        return {
            "total_items": len(self.memory_bank),
            "average_compression": np.mean(compressions),
            "max_compression": np.max(compressions),
            "min_compression": np.min(compressions),
            "total_soft_modes": total_modes,
        }
