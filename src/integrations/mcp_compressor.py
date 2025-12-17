"""
MCP Server for text compression - reduces message size by mode.
Port: 4331
"""

import logging
from typing import Any, Dict, Optional

from src.audit.immutable_audit import get_audit_system
from src.integrations.mcp_server import MCPConfig, MCPServer

logger = logging.getLogger(__name__)


class CompressorMCPServer(MCPServer):
    """MCP Server for compressing text messages."""

    MODES = ["summary", "outline", "spec", "chunk"]

    def __init__(self, config: Optional[MCPConfig] = None):
        super().__init__(config or self._default_config())
        self.audit_system = get_audit_system()

        # Register methods
        self._methods.update(
            {
                "compress_text": self.compress_text,
                "estimate_compression": self.estimate_compression,
                "get_modes": self.get_modes,
            }
        )

    @staticmethod
    def _default_config() -> MCPConfig:
        return MCPConfig(host="127.0.0.1", port=4331)

    def compress_text(
        self, text: str, mode: str = "summary", target_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Compress text using specified mode.

        Args:
            text: Text to compress
            mode: Compression mode (summary, outline, spec, chunk)
            target_length: Target length in characters

        Returns:
            Dict with compressed_text, compression_ratio, and metadata
        """
        try:
            if mode not in self.MODES:
                return {
                    "status": "error",
                    "error": f"Invalid mode: {mode}. Use one of: {self.MODES}",
                }

            original_length = len(text)
            target_length = target_length or original_length // 2

            if mode == "summary":
                compressed = self._compress_summary(text, target_length)
            elif mode == "outline":
                compressed = self._compress_outline(text, target_length)
            elif mode == "spec":
                compressed = self._compress_spec(text, target_length)
            else:  # chunk
                compressed = self._compress_chunk(text, target_length)

            compressed_length = len(compressed)
            compression_ratio = compressed_length / original_length if original_length > 0 else 1.0

            # Audit logging
            if hasattr(self, "audit_system"):
                self.audit_system.log_action(
                    action="text_compressed",
                    details={
                        "mode": mode,
                        "original_length": original_length,
                        "compressed_length": compressed_length,
                        "compression_ratio": compression_ratio,
                    },
                    category="compressor_mcp",
                )

            return {
                "status": "success",
                "compressed_text": compressed,
                "compression_ratio": compression_ratio,
                "statistics": {
                    "original_length": original_length,
                    "compressed_length": compressed_length,
                    "reduction_percentage": (1 - compression_ratio) * 100,
                    "mode_used": mode,
                },
            }

        except Exception as e:
            logger.error(f"Compression error: {e}")
            return {"status": "error", "error": str(e), "compressed_text": text}

    def _compress_summary(self, text: str, target_length: int) -> str:
        """Extract summary of text."""
        lines = text.split("\n")
        summary_lines = []
        current_length = 0

        for line in lines:
            if line.strip():  # Skip empty lines
                if current_length + len(line) <= target_length:
                    summary_lines.append(line)
                    current_length += len(line)
                else:
                    break

        result = "\n".join(summary_lines)
        if len(result) < len(text):
            result += "\n[...]"

        return result

    def _compress_outline(self, text: str, target_length: int) -> str:
        """Extract outline (headers only)."""
        lines = text.split("\n")
        outline_lines = []

        for line in lines:
            # Keep lines that start with # (markdown headers)
            if line.strip().startswith("#"):
                outline_lines.append(line)

        if not outline_lines:
            # If no headers, return first few lines
            outline_lines = lines[:3]

        return "\n".join(outline_lines)

    def _compress_spec(self, text: str, target_length: int) -> str:
        """Extract specification-like format (structured data)."""
        lines = text.split("\n")
        spec_lines = []

        for line in lines:
            # Keep lines with colons or equals (key-value pairs)
            if ":" in line or "=" in line:
                spec_lines.append(line.strip())

        if not spec_lines:
            spec_lines = lines[:5]

        return "\n".join(spec_lines[:10])  # Limit to 10 lines

    def _compress_chunk(self, text: str, target_length: int) -> str:
        """Compress by selecting most important chunks."""
        # Simple approach: take first and last chunks
        if len(text) <= target_length:
            return text

        first_part = text[: target_length // 2]
        last_part = text[-(target_length // 4) :]

        return first_part + "\n[... compressed ...]\n" + last_part

    def estimate_compression(self, text: str, target_ratio: float = 0.5) -> Dict[str, Any]:
        """Estimate compression results without actually compressing."""
        original_size = len(text)
        estimated_compressed = int(original_size * target_ratio)

        # Recommend mode based on text characteristics
        if "\n" in text:
            recommended_mode = "outline"
        elif ":" in text or "=" in text:
            recommended_mode = "spec"
        else:
            recommended_mode = "summary"

        return {
            "status": "success",
            "original_size": original_size,
            "estimated_compressed": estimated_compressed,
            "target_ratio": target_ratio,
            "recommended_mode": recommended_mode,
            "potential_savings_percent": (1 - target_ratio) * 100,
        }

    def get_modes(self) -> Dict[str, Any]:
        """Get available compression modes."""
        return {
            "status": "success",
            "available_modes": self.MODES,
            "modes_description": {
                "summary": "Extract key lines based on target length",
                "outline": "Extract headers/structure only",
                "spec": "Extract structured data (key-value pairs)",
                "chunk": "Keep beginning and end, compress middle",
            },
        }


if __name__ == "__main__":
    server = CompressorMCPServer()
    # run() method not available in base MCPServer yet
