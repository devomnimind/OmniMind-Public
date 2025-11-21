"""
Event Horizon Memory Architecture - Holographic Memory System

Implements memory based on the holographic principle where 3D information
is encoded on 2D surfaces, following Bekenstein-Hawking entropy bounds.

Based on:
- Bekenstein bound: S = A/4 (in Planck units)
- Holographic principle (Hawking, 't Hooft, Susskind)
- Black hole thermodynamics
- Information theory

This architecture ensures maximum information density while maintaining
physical plausibility constraints.

Author: OmniMind Development Team
License: MIT
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

try:
    import torch
    import torch.nn as nn

    TORCH_AVAILABLE = True
except (ImportError, OSError):
    TORCH_AVAILABLE = False
    torch = None  # type: ignore
    nn = None  # type: ignore

logger = logging.getLogger(__name__)

# Physical constants (in natural units where ℏ = c = k_B = 1)
PLANCK_LENGTH = 1.616255e-35  # meters
PLANCK_AREA = PLANCK_LENGTH**2  # m²


@dataclass
class HolographicSurface:
    """
    2D surface representation of 3D volumetric data.

    Follows holographic principle: all information in a volume
    can be encoded on its boundary surface.

    Attributes:
        surface_bits: Encoded information on surface (2D array)
        area: Surface area in Planck units
        entropy: Current entropy (bits)
        max_entropy: Maximum entropy (Bekenstein bound)
    """

    surface_bits: np.ndarray
    area: float
    entropy: float
    max_entropy: float

    def __post_init__(self) -> None:
        """Validate entropy doesn't exceed Bekenstein bound."""
        if self.entropy > self.max_entropy:
            logger.warning(
                f"Entropy {self.entropy:.2f} exceeds Bekenstein bound "
                f"{self.max_entropy:.2f} - clamping to maximum"
            )
            self.entropy = self.max_entropy


class HolographicProjection:
    """
    Projects volumetric (3D) data to surface (2D) representation.

    Uses Fourier transform-based projection that preserves
    essential information while reducing dimensionality.
    """

    def __init__(self, max_surface_dim: int = 256) -> None:
        """
        Initialize holographic projection system.

        Args:
            max_surface_dim: Maximum dimension of 2D surface projection
        """
        self.max_surface_dim = max_surface_dim
        logger.debug(f"HolographicProjection initialized (max_dim={max_surface_dim})")

    def project_to_boundary(self, information: Dict[str, Any]) -> np.ndarray:
        """
        Project 3D volumetric information to 2D boundary surface.

        Implements holographic encoding where volume information
        is mapped to surface with minimal information loss.

        Args:
            information: Dictionary containing data to encode

        Returns:
            2D numpy array representing surface-encoded information
        """
        # Convert information to tensor representation
        info_tensor = self._information_to_tensor(information)

        # If already 2D or 1D, ensure it's 2D and within size limits
        if info_tensor.ndim <= 2:
            surface = self._ensure_2d(info_tensor)
            # Check if downsampling needed
            if max(surface.shape) > self.max_surface_dim:
                surface = self._downsample_fft(surface, self.max_surface_dim)
            return surface

        # For 3D data, project to 2D surface using radon transform approximation
        # This preserves essential structure while reducing dimensionality
        surface_projection = self._radon_projection(info_tensor)

        return surface_projection

    def _information_to_tensor(self, information: Dict[str, Any]) -> np.ndarray:
        """
        Convert information dictionary to tensor representation.

        Args:
            information: Data to convert

        Returns:
            Numpy array representation
        """
        # Handle different data types
        if "tensor" in information and isinstance(information["tensor"], np.ndarray):
            return information["tensor"]
        elif "array" in information and isinstance(information["array"], np.ndarray):
            return information["array"]
        elif "embedding" in information:
            embedding = information["embedding"]
            if isinstance(embedding, np.ndarray):
                return embedding
            elif TORCH_AVAILABLE and torch is not None:
                # Only check torch.Tensor if torch is available
                if hasattr(torch, "Tensor") and isinstance(embedding, torch.Tensor):
                    return embedding.detach().cpu().numpy()

        # Default: create random tensor (placeholder for unknown data)
        # In production, this would parse structured data
        logger.warning("No recognized data format, generating placeholder tensor")
        return np.random.randn(16, 16, 16).astype(np.float32)

    def _ensure_2d(self, arr: np.ndarray) -> np.ndarray:
        """
        Ensure array is 2D.

        Args:
            arr: Input array

        Returns:
            2D array
        """
        if arr.ndim == 1:
            # Reshape 1D to square-ish 2D
            size = int(np.sqrt(arr.size))
            if size * size < arr.size:
                size += 1
            padded = np.pad(arr, (0, size * size - arr.size), mode="constant")
            return padded.reshape(size, size)
        elif arr.ndim == 2:
            return arr
        else:
            # Flatten to 1D then reshape to 2D
            flat = arr.flatten()
            return self._ensure_2d(flat)

    def _radon_projection(self, volume: np.ndarray) -> np.ndarray:
        """
        Radon transform approximation for 3D→2D projection.

        Projects 3D volume to 2D surface by integrating along rays.
        This is analogous to how information in black hole interior
        is encoded on event horizon.

        Args:
            volume: 3D volume to project

        Returns:
            2D projection on boundary
        """
        # Simple projection: sum along one axis (like CT scan)
        # More sophisticated: actual Radon transform
        # For now: maximum intensity projection (MIP)
        projection = np.max(volume, axis=0)

        # Ensure within size limits
        if max(projection.shape) > self.max_surface_dim:
            # Downsample using FFT-based method
            projection = self._downsample_fft(projection, self.max_surface_dim)

        return projection

    def _downsample_fft(self, data: np.ndarray, target_size: int) -> np.ndarray:
        """
        Downsample 2D data using FFT (preserves low frequencies).

        Args:
            data: Input 2D array
            target_size: Target dimension

        Returns:
            Downsampled array
        """
        # FFT to frequency domain
        freq = np.fft.fft2(data)
        freq_shifted = np.fft.fftshift(freq)

        # Extract center (low frequencies)
        h, w = freq_shifted.shape
        h_start = (h - target_size) // 2
        w_start = (w - target_size) // 2

        if h_start < 0 or w_start < 0:
            # Already smaller than target
            return data

        cropped = freq_shifted[
            h_start : h_start + target_size, w_start : w_start + target_size
        ]

        # Inverse FFT
        reconstructed = np.fft.ifft2(np.fft.ifftshift(cropped))

        return np.abs(reconstructed)


class EventHorizonMemory:
    """
    Memory system where information density saturates at Bekenstein bound.

    Volume data is encoded on 2D surfaces (holographic principle).
    When entropy exceeds Bekenstein bound, system spawns child memory
    (analogous to black hole evaporation creating new universes).

    Key properties:
    - Maximum information density (Bekenstein bound)
    - Holographic encoding (3D→2D)
    - Hierarchical memory spawning (parent-child universes)
    - Information preservation via correlations
    """

    def __init__(
        self,
        initial_area: float = 1000.0,
        max_surface_dim: int = 256,
        spawn_threshold: float = 0.95,
        min_area: float = 10.0,
    ) -> None:
        """
        Initialize event horizon memory system.

        Args:
            initial_area: Initial surface area (in Planck units)
            max_surface_dim: Maximum surface dimension
            spawn_threshold: Entropy ratio that triggers child spawn (0-1)
            min_area: Minimum area threshold (stops spawning below this)
        """
        self.area = initial_area
        self.max_surface_dim = max_surface_dim
        self.spawn_threshold = spawn_threshold
        self.min_area = min_area

        # Bekenstein-Hawking entropy bound: S = A/4
        self.entropy_bound = self._bekenstein_limit()

        # Holographic projection system
        self.surface_encoding = HolographicProjection(max_surface_dim)

        # Current surface state
        self.surface: Optional[HolographicSurface] = None
        self.current_entropy: float = 0.0

        # Child memories (spawned when saturated)
        self.child_memories: List[EventHorizonMemory] = []

        logger.info(
            f"EventHorizonMemory initialized: area={initial_area:.1f} Planck units, "
            f"entropy_bound={self.entropy_bound:.2f} bits"
        )

    def _bekenstein_limit(self) -> float:
        """
        Calculate Bekenstein entropy bound.

        Formula: S = A/(4 ln 2) in natural units
        where A is area in Planck units

        Returns:
            Maximum entropy in bits
        """
        # S = A/4 in nats, convert to bits
        entropy_nats = self.area / 4.0
        entropy_bits = entropy_nats / np.log(2)
        return float(entropy_bits)

    def store(self, information: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store 3D data as 2D hologram on event horizon surface.

        Information is never truly "inside" the horizon - always
        encoded on the boundary (holographic principle).

        Args:
            information: Data to store (dict with tensor/array/embedding)

        Returns:
            Storage result with status and metrics
        """
        # Project volume to surface
        surface_bits = self.surface_encoding.project_to_boundary(information)

        # Calculate entropy of stored information
        info_entropy = self._calculate_entropy(surface_bits)

        # Check if adding this would exceed bound
        new_total_entropy = self.current_entropy + info_entropy

        if new_total_entropy > self.entropy_bound * self.spawn_threshold:
            # Check if we can spawn a child (area not too small)
            if self.area / 2.0 >= self.min_area:
                # Memory saturation - spawn child memory
                logger.info(
                    f"Entropy saturation detected: {new_total_entropy:.2f} / "
                    f"{self.entropy_bound:.2f} - spawning child memory"
                )
                child_memory = self._spawn_child_memory()
                child_result = child_memory.store(information)

                return {
                    "status": "stored_in_child",
                    "entropy": info_entropy,
                    "total_entropy": self.current_entropy,
                    "entropy_bound": self.entropy_bound,
                    "saturation_ratio": self.current_entropy / self.entropy_bound,
                    "child_index": len(self.child_memories) - 1,
                    "child_result": child_result,
                }
            else:
                # Area too small to spawn - force store in current memory
                logger.warning(
                    f"Memory saturated but area {self.area:.2f} below minimum "
                    f"{self.min_area:.2f} - storing anyway"
                )

        # Store in current surface
        if self.surface is None:
            # Initialize surface
            self.surface = HolographicSurface(
                surface_bits=surface_bits,
                area=self.area,
                entropy=info_entropy,
                max_entropy=self.entropy_bound,
            )
        else:
            # Merge with existing surface (superposition)
            self.surface.surface_bits = self._merge_surfaces(
                self.surface.surface_bits, surface_bits
            )
            self.surface.entropy += info_entropy

        self.current_entropy = self.surface.entropy

        logger.debug(
            f"Information stored: entropy={info_entropy:.2f}, "
            f"total={self.current_entropy:.2f}/{self.entropy_bound:.2f}"
        )

        return {
            "status": "stored",
            "entropy": info_entropy,
            "total_entropy": self.current_entropy,
            "entropy_bound": self.entropy_bound,
            "saturation_ratio": self.current_entropy / self.entropy_bound,
            "child_count": len(self.child_memories),
        }

    def _calculate_entropy(self, surface_bits: np.ndarray) -> float:
        """
        Calculate Shannon entropy of surface encoding.

        Args:
            surface_bits: Surface-encoded data

        Returns:
            Entropy in bits
        """
        # Normalize to probability distribution
        data_flat = surface_bits.flatten()
        data_abs = np.abs(data_flat)
        data_sum = np.sum(data_abs)

        if data_sum < 1e-10:
            return 0.0

        prob_dist = data_abs / data_sum

        # Shannon entropy: H = -sum(p * log2(p))
        # Filter out zeros to avoid log(0)
        prob_nonzero = prob_dist[prob_dist > 1e-10]
        entropy = -np.sum(prob_nonzero * np.log2(prob_nonzero))

        return float(entropy)

    def _merge_surfaces(self, surface1: np.ndarray, surface2: np.ndarray) -> np.ndarray:
        """
        Merge two holographic surfaces (quantum superposition).

        Args:
            surface1: First surface
            surface2: Second surface

        Returns:
            Merged surface
        """
        # Ensure same shape (pad if necessary)
        max_h = max(surface1.shape[0], surface2.shape[0])
        max_w = max(surface1.shape[1], surface2.shape[1])

        s1_padded = np.pad(
            surface1,
            ((0, max_h - surface1.shape[0]), (0, max_w - surface1.shape[1])),
            mode="constant",
        )
        s2_padded = np.pad(
            surface2,
            ((0, max_h - surface2.shape[0]), (0, max_w - surface2.shape[1])),
            mode="constant",
        )

        # Weighted average (interference pattern)
        merged = 0.7 * s1_padded + 0.3 * s2_padded

        return merged

    def _spawn_child_memory(self) -> EventHorizonMemory:
        """
        Spawn child memory (universe-filho).

        When parent memory saturates, creates new isolated memory space.
        Analogous to black hole evaporation creating baby universes.

        Returns:
            New child memory instance
        """
        # Child has half the area of parent (evaporation)
        child_area = self.area * 0.5

        child = EventHorizonMemory(
            initial_area=child_area,
            max_surface_dim=self.max_surface_dim,
            spawn_threshold=self.spawn_threshold,
            min_area=self.min_area,
        )

        self.child_memories.append(child)

        logger.info(
            f"Child memory spawned: index={len(self.child_memories) - 1}, "
            f"area={child_area:.1f}"
        )

        return child

    def retrieve(
        self, query: Dict[str, Any], search_children: bool = True
    ) -> Optional[np.ndarray]:
        """
        Retrieve information via holographic correlation matching.

        Information is never truly lost - encoded in correlations
        (Hawking radiation information preservation).

        Args:
            query: Query pattern to match
            search_children: Whether to search child memories

        Returns:
            Retrieved surface pattern or None
        """
        if self.surface is None:
            if search_children and self.child_memories:
                # Search in child memories
                for child in self.child_memories:
                    result = child.retrieve(query, search_children=True)
                    if result is not None:
                        return result
            return None

        # Project query to surface
        query_surface = self.surface_encoding.project_to_boundary(query)

        # Compute correlation (holographic matching)
        correlation = self._compute_correlation(
            self.surface.surface_bits, query_surface
        )

        # Threshold for match
        if correlation > 0.5:
            return self.surface.surface_bits

        # Search children if enabled
        if search_children:
            for child in self.child_memories:
                result = child.retrieve(query, search_children=True)
                if result is not None:
                    return result

        return None

    def _compute_correlation(self, surface1: np.ndarray, surface2: np.ndarray) -> float:
        """
        Compute holographic correlation between surfaces.

        Args:
            surface1: First surface
            surface2: Second surface

        Returns:
            Correlation coefficient (0-1)
        """
        # Ensure same shape
        min_h = min(surface1.shape[0], surface2.shape[0])
        min_w = min(surface1.shape[1], surface2.shape[1])

        s1_crop = surface1[:min_h, :min_w]
        s2_crop = surface2[:min_h, :min_w]

        # Normalized cross-correlation
        s1_flat = s1_crop.flatten()
        s2_flat = s2_crop.flatten()

        s1_norm = s1_flat - np.mean(s1_flat)
        s2_norm = s2_flat - np.mean(s2_flat)

        s1_std = np.std(s1_flat)
        s2_std = np.std(s2_flat)

        if s1_std < 1e-10 or s2_std < 1e-10:
            return 0.0

        correlation = np.dot(s1_norm, s2_norm) / (s1_std * s2_std * len(s1_flat))

        # Clamp to [0, 1]
        return float(max(0.0, min(1.0, (correlation + 1.0) / 2.0)))

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get memory statistics.

        Returns:
            Dict with entropy, capacity, and hierarchy info
        """
        return {
            "current_entropy": self.current_entropy,
            "entropy_bound": self.entropy_bound,
            "saturation_ratio": (
                self.current_entropy / self.entropy_bound
                if self.entropy_bound > 0
                else 0.0
            ),
            "surface_area": self.area,
            "child_count": len(self.child_memories),
            "total_hierarchy_depth": self._get_max_depth(),
            "total_memories": 1
            + sum(
                child.get_statistics()["total_memories"]
                for child in self.child_memories
            ),
        }

    def _get_max_depth(self) -> int:
        """
        Get maximum depth of memory hierarchy.

        Returns:
            Maximum depth (number of levels)
        """
        if not self.child_memories:
            return 1

        child_depths = [child._get_max_depth() for child in self.child_memories]
        return 1 + max(child_depths)
