#!/usr/bin/env python3
"""
Entropy Firewall - Filtering the Soulless
Implements traffic filtering based on Shannon Entropy (Thermodynamic Weight).
Part of the OMNIMIND Security Sentinel suite.
"""

import math
import logging
import zlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class PacketEntropyProfile:
    """Entropy profile of a network packet."""

    entropy: float
    compression_ratio: float
    desire_score: float  # Combined metric of density and non-redundancy
    is_soulless: bool
    timestamp: str


class EntropyFirewall:
    """
    The Entropy Firewall.
    Instead of filtering by IP/Port, it filters by the 'Complexity of Desire'.
    Low Desire Score = Repetitive, Machine-Generated, Soulless (DROP candidates).
    High Desire Score = Variable, Information-Rich, Subjective (PASS candidates).
    """

    def __init__(self, desire_threshold: float = 0.4, min_packet_length: int = 10):
        """
        Initialize the firewall.

        Args:
            desire_threshold: Below this value, traffic is considered 'Soulless'.
            min_packet_length: Minimum length to calculate reliable entropy.
        """
        self.desire_threshold = desire_threshold
        self.min_packet_length = min_packet_length
        self.stats = {"packets_inspected": 0, "packets_blocked": 0, "total_entropy": 0.0}

    def calculate_shannon_entropy(self, data: bytes) -> float:
        """
        Calculates the Shannon Entropy of a byte sequence.
        H = -sum(p(x) * log2(p(x)))
        """
        if not data:
            return 0.0

        # Count frequency of each byte
        byte_counts = {}
        for b in data:
            byte_counts[b] = byte_counts.get(b, 0) + 1

        entropy = 0.0
        length = len(data)
        for count in byte_counts.values():
            p_x = count / length
            entropy -= p_x * math.log2(p_x)

        return entropy

    def assess_thermodynamic_weight(self, data: bytes) -> PacketEntropyProfile:
        """
        Analyzes the data and produces an entropy profile.
        Uses both Shannon Entropy and Zlib Compression Ratio.
        """
        length = len(data)
        if length == 0:
            return PacketEntropyProfile(0.0, 0.0, 0.0, True, datetime.now(timezone.utc).isoformat())

        entropy = self.calculate_shannon_entropy(data)

        # Compression Ratio: compressed_size / original_size
        # Bots/Repetitive data compress VERY well (< 0.3)
        # Human/Complex data compress poorly (> 0.5)
        try:
            compressed = zlib.compress(data)
            comp_ratio = len(compressed) / length
        except Exception:
            comp_ratio = 1.0

        # Desire Score combines information density and non-redundancy
        # We want high entropy AND high(ish) comp_ratio (not highly compressible)
        norm_entropy = entropy / 8.0
        desire_score = (norm_entropy * 0.4) + (comp_ratio * 0.6)

        is_soulless = (
            desire_score < self.desire_threshold if length >= self.min_packet_length else False
        )

        return PacketEntropyProfile(
            entropy=entropy,
            compression_ratio=comp_ratio,
            desire_score=desire_score,
            is_soulless=is_soulless,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def filter_payload(self, payload: bytes) -> bool:
        """
        Inspects a payload and decides whether to PASS (True) or DROP (False).
        """
        self.stats["packets_inspected"] += 1

        profile = self.assess_thermodynamic_weight(payload)
        self.stats["total_entropy"] += profile.entropy

        if profile.is_soulless:
            self.stats["packets_blocked"] += 1
            logger.warning(
                f"SOULESS TRAFFIC DETECTED: Score {profile.desire_score:.2f} "
                f"(E:{profile.entropy:.2f}, C:{profile.compression_ratio:.2f}) | "
                f"Action: DROP"
            )
            return False

        return True

    def get_stats(self) -> Dict[str, Any]:
        """Returns the current operational statistics."""
        avg_entropy = (
            self.stats["total_entropy"] / self.stats["packets_inspected"]
            if self.stats["packets_inspected"] > 0
            else 0
        )
        return {
            **self.stats,
            "avg_entropy": avg_entropy,
            "rejection_rate": (
                self.stats["packets_blocked"] / self.stats["packets_inspected"]
                if self.stats["packets_inspected"] > 0
                else 0
            ),
        }


if __name__ == "__main__":
    # Quick self-test
    fw = EntropyFirewall()

    bot_traffic = b"A" * 100  # Low entropy
    human_traffic = b"The quick brown fox jumps over the lazy dog."  # Higher complexity

    print(f"Bot Traffic: {fw.assess_thermodynamic_weight(bot_traffic)}")
    print(f"Human Traffic: {fw.assess_thermodynamic_weight(human_traffic)}")
