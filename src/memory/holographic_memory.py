from __future__ import annotations

import logging
import math
import statistics
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Union
    import numpy as np
    import torch
    import torch.nn as nn
    import numpy as np  # noqa: F811
    import torch  # noqa: F811
    import torch.nn as nn  # noqa: F811


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



# Type checking imports (for type hints only)
if TYPE_CHECKING:

    NDArray = Any
else:
    NDArray = Any

# Runtime imports
try:

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None  # type: ignore

try:

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

    def project_to_boundary(self, information: Dict[str, Any]) -> Union[NDArray, List[List[float]]]:
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
                        if surface is not None and len(surface) > 0 and len(surface[0]) > 0
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
        # Try different data type handlers in order
        handlers = [
            self._handle_tensor_data,
            self._handle_array_data,
            self._handle_embedding_data,
        ]

        for handler in handlers:
            result = handler(information)
            if result is not None:
                return result

        # Default: create placeholder tensor
        return self._create_placeholder_tensor()

    def _handle_tensor_data(self, information: Dict[str, Any]) -> Optional[Any]:
        """Handle tensor data from information dict."""
        if "tensor" in information:
            return information["tensor"]
        return None

    def _handle_array_data(self, information: Dict[str, Any]) -> Optional[Any]:
        """Handle array data from information dict."""
        if "array" in information:
            return information["array"]
        return None

    def _handle_embedding_data(self, information: Dict[str, Any]) -> Optional[Any]:
        """Handle embedding data from information dict."""
        if "embedding" not in information:
            return None

        embedding = information["embedding"]

        # Handle list embeddings
        if isinstance(embedding, list):
            return embedding

        # Handle torch tensors
        if self._is_torch_tensor(embedding):
            return embedding.detach().cpu().numpy().tolist()

        return None

    def _is_torch_tensor(self, obj: Any) -> bool:
        """Check if object is a torch tensor."""
        return (
            TORCH_AVAILABLE
            and torch is not None
            and hasattr(torch, "Tensor")
            and isinstance(obj, torch.Tensor)
        )

    def _create_placeholder_tensor(self) -> List[List[List[float]]]:
        """Create placeholder 3D tensor for unknown data formats."""
        logger.warning("No recognized data format, generating placeholder tensor")
        return [[[0.0 for _ in range(16)] for _ in range(16)] for _ in range(16)]

    def _ensure_2d(self, arr: Sequence[Any]) -> List[List[float]]:
        """
        Ensure array is 2D.

        Args:
            arr: Input array

        Returns:
            2D array
        """
        # Handle numpy arrays first
        if self._is_numpy_array(arr):
            return self._handle_numpy_array(arr)

        # Handle nested sequences
        if self._is_nested_sequence(arr):
            return self._handle_nested_sequence(arr)

        # Handle scalar values
        return self._handle_scalar_value(arr)

    def _is_numpy_array(self, arr: Any) -> bool:
        """Check if input is a numpy array."""
        return NUMPY_AVAILABLE and np is not None and isinstance(arr, np.ndarray)

    def _handle_numpy_array(self, arr: Any) -> List[List[float]]:
        """Handle numpy array conversion to 2D."""
        arr_2d = arr
        if arr.ndim == 1:  # type: ignore
            arr_2d = arr.reshape(1, -1)  # type: ignore
        elif arr.ndim > 2:  # type: ignore
            # Flatten higher dimensions
            arr_2d = arr.reshape(arr.shape[0], -1)  # type: ignore
        return arr_2d.tolist()

    def _is_nested_sequence(self, arr: Any) -> bool:
        """Check if input is a nested sequence."""
        return isinstance(arr, Sequence) and not isinstance(arr, (str, bytes))

    def _handle_nested_sequence(self, arr: Sequence[Any]) -> List[List[float]]:
        """Handle nested sequence conversion to 2D."""
        flat = self._flatten_nested_sequence(arr)
        return self._reshape_to_square_matrix(flat)

    def _handle_scalar_value(self, arr: Any) -> List[List[float]]:
        """Handle scalar value conversion to 2D."""
        return [[float(arr)]]

    def _flatten_nested_sequence(self, arr: Sequence[Any]) -> List[float]:
        """Flatten nested sequence to 1D list."""
        flat: List[float] = []
        for item in arr:
            if isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
                for sub in item:
                    if isinstance(sub, Sequence) and not isinstance(sub, (str, bytes)):
                        flat.extend([float(x) for x in sub])
                    else:
                        flat.append(float(sub))
            else:
                flat.append(float(item))
        return flat

    def _reshape_to_square_matrix(self, flat: List[float]) -> List[List[float]]:
        """Reshape flat list to square-ish 2D matrix."""
        if not flat:
            return [[]]

        side = max(int(math.sqrt(len(flat))), 1)
        while side * side < len(flat):
            side += 1

        padded = flat + [0.0] * (side * side - len(flat))
        return [padded[i * side : (i + 1) * side] for i in range(side)]

    def _radon_projection(self, volume: Sequence[Sequence[Sequence[Any]]]) -> List[List[float]]:
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
        # Validate input
        if self._is_volume_empty(volume):
            return []

        # Extract volume dimensions
        dims = self._get_volume_dimensions(volume)

        # Initialize projection matrix
        projection = self._initialize_projection_matrix(dims)

        # Perform maximum intensity projection
        self._apply_maximum_intensity_projection(volume, projection, dims)

        # Ensure within size limits
        return self._ensure_projection_size_limits(projection)

    def _is_volume_empty(self, volume: Sequence[Sequence[Sequence[Any]]]) -> bool:
        """Check if volume is empty."""
        return not volume

    def _get_volume_dimensions(
        self, volume: Sequence[Sequence[Sequence[Any]]]
    ) -> tuple[int, int, int]:
        """Extract dimensions from 3D volume."""
        depth = len(volume)
        h = len(volume[0]) if depth > 0 and volume[0] else 0
        w = len(volume[0][0]) if h > 0 and volume[0][0] else 0
        return depth, h, w

    def _initialize_projection_matrix(self, dims: tuple[int, int, int]) -> List[List[float]]:
        """Initialize 2D projection matrix with zeros."""
        _, h, w = dims
        return [[0.0 for _ in range(w)] for _ in range(h)]

    def _apply_maximum_intensity_projection(
        self,
        volume: Sequence[Sequence[Sequence[Any]]],
        projection: List[List[float]],
        dims: tuple[int, int, int],
    ) -> None:
        """Apply maximum intensity projection along z-axis."""
        depth, h, w = dims
        for z in range(depth):
            layer = volume[z]
            for i in range(h):
                for j in range(w):
                    projection[i][j] = max(projection[i][j], float(layer[i][j]))

    def _ensure_projection_size_limits(self, projection: List[List[float]]) -> List[List[float]]:
        """Ensure projection stays within size limits."""
        max_dim = max(
            len(projection),
            (len(projection[0]) if projection and projection[0] else 0),
        )

        if max_dim > self.max_surface_dim:
            return self._downsample_fft(projection, self.max_surface_dim)

        return projection

    def _downsample_fft(self, data: Sequence[Sequence[Any]], target_size: int) -> List[List[float]]:
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
        # Calculate target dimensions
        target_dims = self._calculate_merge_dimensions(surface1, surface2)

        # Pad surfaces to same dimensions
        s1_padded = self._pad_surface(surface1, target_dims)
        s2_padded = self._pad_surface(surface2, target_dims)

        # Merge with superposition weights
        merged = self._superpose_surfaces(s1_padded, s2_padded)

        # Convert to numpy if available
        return self._convert_to_numpy_if_available(merged)

    def _calculate_merge_dimensions(self, surface1: Any, surface2: Any) -> tuple[int, int]:
        """
        Calculate target dimensions for merging surfaces.

        Args:
            surface1: First surface
            surface2: Second surface

        Returns:
            Tuple of (height, width) for merged surface
        """
        max_h = max(len(surface1), len(surface2))
        max_w = max(
            len(surface1[0]) if surface1 is not None else 0,
            len(surface2[0]) if surface2 is not None else 0,
        )
        return max_h, max_w

    def _pad_surface(self, surface: Any, target_dims: tuple[int, int]) -> List[List[float]]:
        """
        Pad surface to target dimensions with zeros.

        Args:
            surface: Surface to pad
            target_dims: Target (height, width)

        Returns:
            Padded surface
        """
        target_h, target_w = target_dims
        padded: List[List[float]] = []

        for r in range(target_h):
            row: List[float] = []
            for c in range(target_w):
                if (
                    surface is not None
                    and r < len(surface)
                    and surface[r] is not None
                    and c < len(surface[r])
                ):
                    row.append(float(surface[r][c]))
                else:
                    row.append(0.0)
            padded.append(row)

        return padded

    def _superpose_surfaces(
        self, surface1: List[List[float]], surface2: List[List[float]]
    ) -> List[List[float]]:
        """
        Superpose two surfaces with quantum-inspired weights.

        Args:
            surface1: First surface
            surface2: Second surface

        Returns:
            Superposed surface
        """
        # Quantum superposition weights (can be tuned)
        weight1, weight2 = 0.7, 0.3

        merged: List[List[float]] = []
        for r in range(len(surface1)):
            row: List[float] = []
            for c in range(len(surface1[r])):
                value1 = surface1[r][c]
                value2 = surface2[r][c] if r < len(surface2) and c < len(surface2[r]) else 0.0
                merged_value = weight1 * value1 + weight2 * value2
                row.append(merged_value)
            merged.append(row)

        return merged

    def _convert_to_numpy_if_available(self, surface: List[List[float]]) -> List[List[float]]:
        """
        Convert surface to numpy array if numpy is available.

        Args:
            surface: Surface as list of lists

        Returns:
            Surface (numpy array if available, otherwise list)
        """
        if NUMPY_AVAILABLE and np is not None:
            return np.array(surface)  # type: ignore
        return surface

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
            f"Child memory spawned: index={len(self.child_memories) - 1}, " f"area={child_area:.1f}"
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
        # Try to find in current surface first
        if self.surface is not None:
            result = self._search_current_surface(query)
            if result is not None:
                return result

        # Search in child memories if enabled
        if search_children:
            return self._search_child_memories(query)

        return None

    def _search_current_surface(
        self, query: Dict[str, Any]
    ) -> Optional[Union[List[List[float]], NDArray]]:
        """
        Search for query in current surface.

        Args:
            query: Query pattern to match

        Returns:
            Retrieved surface pattern or None
        """
        # Project query to surface
        query_surface = self.surface_encoding.project_to_boundary(query)

        # Compute correlation (holographic matching)
        correlation = self._compute_correlation(self.surface.surface_bits, query_surface)

        # Check if correlation exceeds threshold
        if correlation > 0.5:
            return self._format_surface_result(self.surface.surface_bits)

        return None

    def _search_child_memories(
        self, query: Dict[str, Any]
    ) -> Optional[Union[List[List[float]], NDArray]]:
        """
        Search for query in child memories.

        Args:
            query: Query pattern to match

        Returns:
            Retrieved surface pattern or None
        """
        for child in self.child_memories:
            result = child.retrieve(query, search_children=True)
            if result is not None:
                return result
        return None

    def _format_surface_result(
        self, surface_bits: Any
    ) -> Optional[Union[List[List[float]], NDArray]]:
        """
        Format surface result for return.

        Args:
            surface_bits: Surface data

        Returns:
            Formatted surface result
        """
        # Return as numpy array if available, else list
        if NUMPY_AVAILABLE and np is not None:
            if isinstance(surface_bits, list):
                return np.array(surface_bits)  # type: ignore
            return surface_bits  # Already ndarray

        # Fallback to list
        if isinstance(surface_bits, list):
            return surface_bits
        elif hasattr(surface_bits, "tolist"):
            return surface_bits.tolist()
        else:
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
        # Ensure surfaces have compatible shapes
        s1_crop, s2_crop = self._align_surfaces(surface1, surface2)

        # Flatten to 1D arrays
        s1_flat = self._flatten_surface(s1_crop)
        s2_flat = self._flatten_surface(s2_crop)

        if not s1_flat or not s2_flat:
            return 0.0

        # Compute normalized cross-correlation
        correlation = self._normalized_cross_correlation(s1_flat, s2_flat)

        # Clamp to [0, 1] range
        return self._clamp_correlation(correlation)

    def _align_surfaces(
        self, surface1: Any, surface2: Any
    ) -> tuple[List[List[float]], List[List[float]]]:
        """
        Align surfaces to have compatible dimensions.

        Args:
            surface1: First surface
            surface2: Second surface

        Returns:
            Tuple of aligned surfaces
        """
        # Find minimum dimensions
        min_h = min(len(surface1), len(surface2))
        min_w = min(
            len(surface1[0]) if surface1 is not None and len(surface1) > 0 else 0,
            len(surface2[0]) if surface2 is not None and len(surface2) > 0 else 0,
        )

        # Crop to minimum dimensions
        s1_crop = [row[:min_w] for row in surface1[:min_h]]
        s2_crop = [row[:min_w] for row in surface2[:min_h]]

        return s1_crop, s2_crop

    def _flatten_surface(self, surface: List[List[float]]) -> List[float]:
        """
        Flatten 2D surface to 1D list.

        Args:
            surface: 2D surface

        Returns:
            Flattened 1D list
        """
        return [float(x) for row in surface for x in row]

    def _normalized_cross_correlation(self, s1: List[float], s2: List[float]) -> float:
        """
        Compute normalized cross-correlation coefficient.

        Args:
            s1: First signal
            s2: Second signal

        Returns:
            Correlation coefficient (-1 to 1)
        """
        # Calculate means
        mean1 = statistics.mean(s1)
        mean2 = statistics.mean(s2)

        # Center the signals
        s1_norm = [x - mean1 for x in s1]
        s2_norm = [x - mean2 for x in s2]

        # Calculate standard deviations
        s1_std = statistics.pstdev(s1)
        s2_std = statistics.pstdev(s2)

        # Handle zero variance case
        if s1_std < 1e-10 or s2_std < 1e-10:
            return 0.0

        # Compute dot product
        dot = sum(a * b for a, b in zip(s1_norm, s2_norm))

        # Compute correlation
        correlation = dot / (s1_std * s2_std * len(s1))
        return correlation

    def _clamp_correlation(self, correlation: float) -> float:
        """
        Clamp correlation coefficient to [0, 1] range.

        Args:
            correlation: Raw correlation (-1 to 1)

        Returns:
            Clamped correlation (0 to 1)
        """
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
                self.current_entropy / self.entropy_bound if self.entropy_bound > 0 else 0.0
            ),
            "surface_area": self.area,
            "child_count": len(self.child_memories),
            "total_hierarchy_depth": self._get_max_depth(),
            "total_memories": 1
            + sum(child.get_statistics()["total_memories"] for child in self.child_memories),
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
