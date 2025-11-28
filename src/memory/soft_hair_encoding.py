from __future__ import annotations

import cmath
import logging
import math
import statistics
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple


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
Soft Hair Encoding - Low-Energy Information Storage

Implements soft hair encoding focused on typed helpers rather than heavy numeric
libraries so MyPy can reason about the entire compression pipeline.
"""


logger = logging.getLogger(__name__)

# Constants
DEFAULT_SOFT_MODE_CUTOFF = 0.1  # Fraction of frequencies to keep (low freq)
MIN_SOFT_MODES = 4  # Minimum number of soft modes to extract
MAX_SOFT_MODES = 256  # Maximum soft modes for memory efficiency


@dataclass
class SoftHair:
    soft_modes: List[List[complex]]
    metadata: Dict[str, Any]
    compression_ratio: float
    original_shape: Tuple[int, ...]


class SoftHairEncoder:
    def __init__(
        self,
        soft_mode_cutoff: float = DEFAULT_SOFT_MODE_CUTOFF,
        max_modes: int = MAX_SOFT_MODES,
    ) -> None:
        self.soft_mode_cutoff = soft_mode_cutoff
        self.max_modes = max_modes
        logger.info(
            f"SoftHairEncoder initialized: cutoff={soft_mode_cutoff}, max_modes={max_modes}"
        )

    def encode_to_soft_hair(self, high_entropy_data: Sequence[Any]) -> SoftHair:
        flat_data = self._flatten(high_entropy_data)
        original_shape = self._infer_shape(high_entropy_data)
        data_2d = self._prepare_2d_grid(flat_data)
        freq = self._fft2d(data_2d)
        shifted = self._fftshift(freq)
        soft_modes = self._extract_soft_modes(shifted)
        compressed_size = sum(len(row) for row in soft_modes)
        compression_ratio = len(flat_data) / max(compressed_size, 1)
        metadata = self._extract_metadata(flat_data, soft_modes)
        return SoftHair(
            soft_modes=soft_modes,
            metadata=metadata,
            compression_ratio=compression_ratio,
            original_shape=original_shape,
        )

    def _flatten(self, data: Sequence[Any]) -> List[complex]:
        if hasattr(data, "flatten"):
            return [complex(x) for x in data.flatten()]

        flattened: List[complex] = []
        for item in data:
            if (isinstance(item, Sequence) or hasattr(item, "__iter__")) and not isinstance(
                item, (str, bytes)
            ):
                flattened.extend(self._flatten(item))
            else:
                flattened.append(complex(item))
        return flattened

    def _infer_shape(self, data: Sequence[Any]) -> Tuple[int, ...]:
        if hasattr(data, "shape"):
            return tuple(data.shape)

        shape: List[int] = []
        cursor: Any = data
        while (isinstance(cursor, Sequence) or hasattr(cursor, "__iter__")) and not isinstance(
            cursor, (str, bytes)
        ):
            if hasattr(cursor, "__len__"):
                shape.append(len(cursor))
            else:
                break

            if not cursor:
                break
            try:
                first = cursor[0]
                cursor = first
            except (IndexError, TypeError):
                break

        return tuple(shape) if shape else (len(data),)

    def _prepare_2d_grid(self, flat_data: List[complex]) -> List[List[complex]]:
        side = max(int(math.sqrt(len(flat_data))), 1)
        while side * side < len(flat_data):
            side += 1
        padded = flat_data + [0j] * (side * side - len(flat_data))
        return [padded[row * side : (row + 1) * side] for row in range(side)]

    def _fft2d(self, grid: List[List[complex]]) -> List[List[complex]]:
        rows = len(grid)
        cols = len(grid[0]) if rows else 0
        if not rows or not cols:
            return []
        result: List[List[complex]] = [[0j for _ in range(cols)] for _ in range(rows)]
        for u in range(rows):
            for v in range(cols):
                total = 0 + 0j
                for x in range(rows):
                    for y in range(cols):
                        exponent = -2 * math.pi * ((u * x) / rows + (v * y) / cols)
                        total += grid[x][y] * cmath.exp(exponent * 1j)
                result[u][v] = total
        return result

    def _ifft2d(self, grid: List[List[complex]]) -> List[List[complex]]:
        rows = len(grid)
        cols = len(grid[0]) if rows else 0
        if not rows or not cols:
            return []
        factor = rows * cols
        result: List[List[complex]] = [[0j for _ in range(cols)] for _ in range(rows)]
        for x in range(rows):
            for y in range(cols):
                total = 0 + 0j
                for u in range(rows):
                    for v in range(cols):
                        exponent = 2 * math.pi * ((u * x) / rows + (v * y) / cols)
                        total += grid[u][v] * cmath.exp(exponent * 1j)
                result[x][y] = total / factor
        return result

    def _roll(
        self,
        grid: List[List[complex]],
        shift_rows: int,
        shift_cols: int,
    ) -> List[List[complex]]:
        rows = len(grid)
        cols = len(grid[0]) if rows else 0
        if not rows or not cols:
            return []
        shifted: List[List[complex]] = [[0j for _ in range(cols)] for _ in range(rows)]
        for i in range(rows):
            for j in range(cols):
                new_i = (i + shift_rows) % rows
                new_j = (j + shift_cols) % cols
                shifted[new_i][new_j] = grid[i][j]
        return shifted

    def _fftshift(self, grid: List[List[complex]]) -> List[List[complex]]:
        rows = len(grid)
        cols = len(grid[0]) if rows else 0
        if not rows or not cols:
            return grid
        return self._roll(grid, rows // 2, cols // 2)

    def _ifftshift(self, grid: List[List[complex]]) -> List[List[complex]]:
        rows = len(grid)
        cols = len(grid[0]) if rows else 0
        if not rows or not cols:
            return grid
        return self._roll(grid, -rows // 2, -cols // 2)

    def _extract_soft_modes(self, freq_data: List[List[complex]]) -> List[List[complex]]:
        rows = len(freq_data)
        cols = len(freq_data[0]) if rows else 0
        if not rows or not cols:
            return []
        soft_h = max(MIN_SOFT_MODES, int(rows * self.soft_mode_cutoff))
        soft_w = max(MIN_SOFT_MODES, int(cols * self.soft_mode_cutoff))
        soft_h = min(soft_h, self.max_modes)
        soft_w = min(soft_w, self.max_modes)
        h_start = (rows - soft_h) // 2
        w_start = (cols - soft_w) // 2
        return [row[w_start : w_start + soft_w] for row in freq_data[h_start : h_start + soft_h]]

    def _extract_metadata(
        self, flattened: List[complex], soft_modes: List[List[complex]]
    ) -> Dict[str, Any]:
        magnitudes = [abs(value) for value in flattened]
        mean_value = float(statistics.mean(magnitudes)) if magnitudes else 0.0
        std_value = float(statistics.stdev(magnitudes)) if len(magnitudes) > 1 else 0.0
        mode_shape = (
            len(soft_modes),
            len(soft_modes[0]) if soft_modes and soft_modes[0] else 0,
        )
        return {
            "original_mean": mean_value,
            "original_std": std_value,
            "soft_mode_shape": mode_shape,
            "dominant_frequency": self._find_dominant_frequency(soft_modes),
        }

    def _find_dominant_frequency(self, soft_modes: List[List[complex]]) -> float:
        max_mag = 0.0
        max_idx: Tuple[int, int] = (0, 0)
        for i, row in enumerate(soft_modes):
            for j, coeff in enumerate(row):
                magnitude = abs(coeff)
                if magnitude > max_mag:
                    max_mag = magnitude
                    max_idx = (i, j)
        return float(math.hypot(*max_idx))

    def decode_from_soft_hair(
        self, soft_hair: SoftHair, target_shape: Optional[Tuple[int, ...]] = None
    ) -> Sequence[Any]:
        if target_shape is None:
            target_shape = soft_hair.original_shape
        if not target_shape:
            return []
        if len(target_shape) == 1:
            size = int(math.sqrt(target_shape[0]))
            if size * size < target_shape[0]:
                size += 1
            recon_shape = (size, size)
        elif len(target_shape) >= 2:
            first = target_shape[0]
            second = target_shape[1]
            recon_shape = (first, second)
        else:
            recon_shape = (1, 1)
        h, w = recon_shape
        if not h or not w:
            return []
        freq_full: List[List[complex]] = [[0j for _ in range(w)] for _ in range(h)]
        soft_h = len(soft_hair.soft_modes)
        soft_w = len(soft_hair.soft_modes[0]) if soft_h else 0
        h_start = (h - soft_h) // 2 if soft_h else 0
        w_start = (w - soft_w) // 2 if soft_w else 0
        for r, row in enumerate(soft_hair.soft_modes):
            for c, value in enumerate(row):
                freq_full[h_start + r][w_start + c] = value
        freq_unshifted = self._ifftshift(freq_full)
        reconstructed = self._ifft2d(freq_unshifted)
        real_flat = [cell.real for row in reconstructed for cell in row]
        if len(target_shape) == 1:
            return real_flat[: target_shape[0]]
        if len(target_shape) >= 2:
            return self._reshape_nested(real_flat, target_shape)
        return real_flat

    def _reshape_nested(self, flat: List[float], shape: Tuple[int, ...]) -> List[Any]:
        if not shape:
            return []
        total = math.prod(shape)
        padded = flat + [0.0] * max(0, total - len(flat))
        iterator: Iterator[float] = iter(padded)

        def build(current_shape: Tuple[int, ...]) -> List[Any]:
            if len(current_shape) == 1:
                return [next(iterator) for _ in range(current_shape[0])]
            return [build(current_shape[1:]) for _ in range(current_shape[0])]

        return build(shape)

    def compute_fidelity(
        self,
        original: Sequence[Any],
        reconstructed: Sequence[Any],
    ) -> float:
        # Flatten inputs to handle 2D/3D arrays
        flat_orig_complex = self._flatten(original)
        flat_recon_complex = self._flatten(reconstructed)

        # Use real part for fidelity (assuming real signals)
        orig_flat = [c.real for c in flat_orig_complex]
        recon_flat = [c.real for c in flat_recon_complex]

        min_size = min(len(orig_flat), len(recon_flat))
        if min_size == 0:
            return 0.0
        diffs = [(orig_flat[i] - recon_flat[i]) ** 2 for i in range(min_size)]
        mse = sum(diffs) / min_size
        signal_power = sum(orig_flat[i] ** 2 for i in range(min_size)) / min_size
        if signal_power < 1e-10:
            return 0.0
        fidelity = 1.0 - min(mse / signal_power, 1.0)
        return float(max(0.0, fidelity))


class SoftHairMemory:
    def __init__(self, encoder: Optional[SoftHairEncoder] = None) -> None:
        self.encoder = encoder or SoftHairEncoder()
        self.memory_bank: Dict[str, SoftHair] = {}
        logger.info("SoftHairMemory initialized")

    def store(self, key: str, data: Sequence[Any]) -> SoftHair:
        soft_hair = self.encoder.encode_to_soft_hair(data)
        self.memory_bank[key] = soft_hair
        logger.debug(f"Stored '{key}': compression={soft_hair.compression_ratio:.2f}x")
        return soft_hair

    def retrieve(self, key: str) -> Optional[Sequence[Any]]:
        soft_hair = self.memory_bank.get(key)
        if not soft_hair:
            return None
        decoded = self.encoder.decode_from_soft_hair(soft_hair)
        logger.debug(f"Retrieved '{key}'")
        return decoded

    def get_compression_stats(self) -> Dict[str, Any]:
        if not self.memory_bank:
            return {
                "total_items": 0,
                "average_compression": 0.0,
                "total_soft_modes": 0,
            }
        ratios = [sh.compression_ratio for sh in self.memory_bank.values()]
        total_modes = sum(
            len(sh.soft_modes) * (len(sh.soft_modes[0]) if sh.soft_modes else 0)
            for sh in self.memory_bank.values()
        )
        average_ratio = sum(ratios) / len(ratios)
        return {
            "total_items": len(self.memory_bank),
            "average_compression": average_ratio,
            "max_compression": max(ratios),
            "min_compression": min(ratios),
            "total_soft_modes": total_modes,
        }
