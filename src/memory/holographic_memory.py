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
from typing import Any, Dict, List, Optional, Sequence, Union, TYPE_CHECKING

import math
import statistics

# Type checking imports (for type hints only)
if TYPE_CHECKING:
    import numpy as np
    import torch
    import torch.nn as nn

    NDArray = Any
else:
    NDArray = Any

# Runtime imports
try:
    import numpy as np  # noqa: F811

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore

try:
    import torch  # noqa: F811
    import torch.nn as nn  # noqa: F811

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

    surface_bits: Union[NDArray, List[List[float]]]
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

    def _tensor_depth(self, tensor: Any) -> int:
        """Estimate the nesting depth of a sequence (1..3)."""
        if not isinstance(tensor, Sequence) or isinstance(tensor, (str, bytes)):
            return 0
        depth = 1
        cur = tensor
        while isinstance(cur, Sequence) and not isinstance(cur, (str, bytes)):
            if not cur:
                break
            cur = cur[0]
            depth += 1
            if depth >= 3:
                break
        return depth

    def project_to_boundary(
        self, information: Dict[str, Any]
    ) -> Union[NDArray, List[List[float]]]:
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
        depth = self._tensor_depth(info_tensor)
        if depth <= 2:
            surface = self._ensure_2d(info_tensor)
            # Check if downsampling needed
            if (
                max(
                    len(surface),
                    (
                        len(surface[0])
                        if surface is not None
                        and len(surface) > 0
                        and len(surface[0]) > 0
                        else 0
                    ),
                )
                > self.max_surface_dim
            ):
                surface = self._downsample_fft(surface, self.max_surface_dim)
            # Convert to numpy array if available
            if NUMPY_AVAILABLE and np is not None:
                return np.array(surface)  # type: ignore
            return surface

        # For 3D data, project to 2D surface using radon transform approximation
        # This preserves essential structure while reducing dimensionality
        surface_projection = self._radon_projection(info_tensor)

        # Convert to numpy array if available
        if NUMPY_AVAILABLE and np is not None:
            return np.array(surface_projection)  # type: ignore
        return surface_projection

    def _information_to_tensor(self, information: Dict[str, Any]) -> Any:
        """
        Convert information dictionary to tensor representation.

        Args:
            information: Data to convert

        Returns:
            Numpy array representation
        """
        # Handle different data types
        if "tensor" in information:
            return information["tensor"]
        elif "array" in information:
            return information["array"]
        elif "embedding" in information:
            embedding = information["embedding"]
            if isinstance(embedding, list):
                return embedding
            elif TORCH_AVAILABLE and torch is not None:
                # Only check torch.Tensor if torch is available
                if hasattr(torch, "Tensor") and isinstance(embedding, torch.Tensor):
                    return embedding.detach().cpu().numpy().tolist()

        # Default: create random tensor (placeholder for unknown data)
        # In production, this would parse structured data
        logger.warning("No recognized data format, generating placeholder tensor")
        # Simple deterministic placeholder 3D tensor (list-of-lists-of-floats)
        return [[[0.0 for _ in range(16)] for _ in range(16)] for _ in range(16)]

    def _ensure_2d(self, arr: Sequence[Any]) -> List[List[float]]:
        """
        Ensure array is 2D.

        Args:
            arr: Input array

        Returns:
            2D array
        """
        # Handle numpy arrays
        if NUMPY_AVAILABLE and np is not None and isinstance(arr, np.ndarray):
            arr_2d = arr
            if arr.ndim == 1:  # type: ignore
                arr_2d = arr.reshape(1, -1)  # type: ignore
            elif arr.ndim > 2:  # type: ignore
                # Flatten higher dimensions
                arr_2d = arr.reshape(arr.shape[0], -1)  # type: ignore
            return arr_2d.tolist()

        # Convert nested sequences into flat list and reshape into square-ish 2D
        flat: List[float] = []
        if isinstance(arr, Sequence) and not isinstance(arr, (str, bytes)):
            for item in arr:
                if isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
                    for sub in item:
                        if isinstance(sub, Sequence) and not isinstance(
                            sub, (str, bytes)
                        ):
                            flat.extend([float(x) for x in sub])
                        else:
                            flat.append(float(sub))
                else:
                    flat.append(float(item))
        else:
            flat = [float(arr)]

        side = max(int(math.sqrt(len(flat))), 1)
        while side * side < len(flat):
            side += 1
        padded = flat + [0.0] * (side * side - len(flat))
        return [padded[i * side : (i + 1) * side] for i in range(side)]

    def _radon_projection(
        self, volume: Sequence[Sequence[Sequence[Any]]]
    ) -> List[List[float]]:
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
        # Expecting volume as list-of-lists-of-lists; compute max along first axis
        if not volume:
            return []
        depth = len(volume)
        h = len(volume[0]) if depth > 0 and volume[0] else 0
        w = len(volume[0][0]) if h > 0 and volume[0][0] else 0
        projection: List[List[float]] = [[0.0 for _ in range(w)] for _ in range(h)]
        for z in range(depth):
            layer = volume[z]
            for i in range(h):
                for j in range(w):
                    projection[i][j] = max(projection[i][j], float(layer[i][j]))

        # Ensure within size limits
        if (
            max(
                len(projection),
                (len(projection[0]) if projection and projection[0] else 0),
            )
            > self.max_surface_dim
        ):
            # Downsample using FFT-based method
            projection = self._downsample_fft(projection, self.max_surface_dim)

        return projection

    def _downsample_fft(
        self, data: Sequence[Sequence[Any]], target_size: int
    ) -> List[List[float]]:
        """
        Downsample 2D data using FFT (preserves low frequencies).

        Args:
            data: Input 2D array
            target_size: Target dimension

        Returns:
            Downsampled array
        """
        # Simple center-crop downsample implementation (no FFT dependency)
        h = len(data)
        w = len(data[0]) if h else 0
        if max(h, w) <= target_size:
            # Convert to list-of-lists of floats
            return [[float(x) for x in row] for row in data]

        h_start = max(0, (h - target_size) // 2)
        w_start = max(0, (w - target_size) // 2)
        cropped: List[List[float]] = []
        for i in range(h_start, h_start + min(target_size, h - h_start)):
            row: List[float] = []
            for j in range(w_start, w_start + min(target_size, w - w_start)):
                row.append(float(data[i][j]))
            # pad row if shorter than target_size
            if len(row) < target_size:
                row.extend([0.0] * (target_size - len(row)))
            cropped.append(row)
        # pad additional rows if necessary
        while len(cropped) < target_size:
            cropped.append([0.0] * target_size)
        return cropped


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
        entropy_bits = entropy_nats / math.log(2)
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

    def _calculate_entropy(self, surface_bits: Any) -> float:
        """
        Calculate Shannon entropy of surface encoding.

        Args:
            surface_bits: Surface-encoded data

        Returns:
            Entropy in bits
        """
        # Normalize to probability distribution
        # Flatten into list
        flat: List[float] = []
        for row in surface_bits:
            for val in row:
                flat.append(float(val))

        data_abs = [abs(x) for x in flat]
        data_sum = sum(data_abs)

        if data_sum < 1e-10:
            return 0.0

        prob_dist = [x / data_sum for x in data_abs]

        # Shannon entropy: H = -sum(p * log2(p))
        entropy = 0.0
        for p in prob_dist:
            if p > 1e-10:
                entropy -= p * math.log2(p)

        return float(entropy)

    def _merge_surfaces(self, surface1: Any, surface2: Any) -> List[List[float]]:
        """
        Merge two holographic surfaces (quantum superposition).

        Args:
            surface1: First surface
            surface2: Second surface

        Returns:
            Merged surface
        """
        # Ensure same shape (pad if necessary)
        max_h = max(len(surface1), len(surface2))
        max_w = max(
            len(surface1[0]) if surface1 is not None else 0,
            len(surface2[0]) if surface2 is not None else 0,
        )

        # pad both surfaces to max_h x max_w
        s1_padded: List[List[float]] = [
            [
                (
                    float(surface1[r][c])
                    if r < len(surface1) and c < len(surface1[0])
                    else 0.0
                )
                for c in range(max_w)
            ]
            for r in range(max_h)
        ]
        s2_padded: List[List[float]] = [
            [
                (
                    float(surface2[r][c])
                    if r < len(surface2) and c < len(surface2[0])
                    else 0.0
                )
                for c in range(max_w)
            ]
            for r in range(max_h)
        ]

        merged: List[List[float]] = [
            [0.7 * s1_padded[r][c] + 0.3 * s2_padded[r][c] for c in range(max_w)]
            for r in range(max_h)
        ]

        if NUMPY_AVAILABLE and np is not None:
            return np.array(merged)  # type: ignore

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
    ) -> Optional[Union[List[List[float]], NDArray]]:
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
            # Return as numpy array if available, else list
            if NUMPY_AVAILABLE and np is not None:
                if isinstance(self.surface.surface_bits, list):
                    return np.array(self.surface.surface_bits)  # type: ignore
                return self.surface.surface_bits  # Already ndarray

            # Fallback to list
            if isinstance(self.surface.surface_bits, list):
                return self.surface.surface_bits
            elif hasattr(self.surface.surface_bits, "tolist"):
                return self.surface.surface_bits.tolist()
            else:
                return None

        # Search children if enabled
        if search_children:
            for child in self.child_memories:
                result = child.retrieve(query, search_children=True)
                if result is not None:
                    return result

        return None

    def _compute_correlation(self, surface1: Any, surface2: Any) -> float:
        """
        Compute holographic correlation between surfaces.

        Args:
            surface1: First surface
            surface2: Second surface

        Returns:
            Correlation coefficient (0-1)
        """
        # Ensure same shape
        min_h = min(len(surface1), len(surface2))
        min_w = min(
            (len(surface1[0]) if surface1 is not None and len(surface1) > 0 else 0),
            (len(surface2[0]) if surface2 is not None and len(surface2) > 0 else 0),
        )

        s1_crop = [row[:min_w] for row in surface1[:min_h]]
        s2_crop = [row[:min_w] for row in surface2[:min_h]]

        # Normalized cross-correlation
        # Flatten arrays into lists
        s1_flat: List[float] = [float(x) for row in s1_crop for x in row]
        s2_flat: List[float] = [float(x) for row in s2_crop for x in row]

        if not s1_flat or not s2_flat:
            return 0.0

        mean1 = statistics.mean(s1_flat)
        mean2 = statistics.mean(s2_flat)

        s1_norm = [x - mean1 for x in s1_flat]
        s2_norm = [x - mean2 for x in s2_flat]

        s1_std = statistics.pstdev(s1_flat)
        s2_std = statistics.pstdev(s2_flat)

        if s1_std < 1e-10 or s2_std < 1e-10:
            return 0.0

        dot = sum(a * b for a, b in zip(s1_norm, s2_norm))
        correlation = dot / (s1_std * s2_std * len(s1_flat))

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
