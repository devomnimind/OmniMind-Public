"""
MCP Server for text sanitization - removes sensitive data.
Port: 4330
"""

import logging
import re
from typing import Any, Dict, List, Optional

from src.audit.immutable_audit import get_audit_system
from src.integrations.mcp_server import MCPConfig, MCPServer

logger = logging.getLogger(__name__)


class SanitizerMCPServer(MCPServer):
    """MCP Server for removing sensitive data from text."""

    def __init__(self, config: Optional[MCPConfig] = None):
        super().__init__(config or self._default_config())
        self.audit_system = get_audit_system()

        # Default sanitization rules
        self.default_rules = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "api_key": (
                r"(?:sk-proj-[A-Za-z0-9\-]{20,}|AKIA[0-9A-Z]{16}|"
                r"ghp_[A-Za-z0-9_]{36}|pk_live_[A-Za-z0-9]{20,})"
            ),
            "password": r"(?:password|passwd|pwd)\s*[:=]\s*([^\s,;\"']+)",
            "phone": (r"\b(\+?1[-.\s]?)?\(?[0-9]{3}\)?" r"[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b"),
            "ip_address": (
                r"\b(?:(?:25[0-5]|2[0-4][0-9]|"
                r"[01]?[0-9][0-9]?)\.){3}"
                r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
            ),
            "url": r"https?://[^\s]+",
        }

        # Register methods
        self._methods.update(
            {
                "sanitize_text": self.sanitize_text,
                "get_rules": self.get_rules,
                "add_custom_pattern": self.add_custom_pattern,
            }
        )

    @staticmethod
    def _default_config() -> MCPConfig:
        return MCPConfig(host="127.0.0.1", port=4330)

    def sanitize_text(self, text: str, rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Sanitize text by removing sensitive data.

        Args:
            text: Text to sanitize
            rules: Configuration dict with:
                - enabled: List of rule names to apply
                - redaction_char: Character to use for redaction (default: *)
                - custom_patterns: List of custom regex patterns

        Returns:
            Dict with sanitized_text, redaction_map, and statistics
        """
        try:
            rules = rules or {}
            enabled_rules = rules.get("enabled", list(self.default_rules.keys()))
            redaction_char = rules.get("redaction_char", "*")
            custom_patterns = rules.get("custom_patterns", [])

            sanitized_text = text
            redaction_map: Dict[str, List[str]] = {}
            items_redacted = 0

            # Apply default rules
            for rule_name in enabled_rules:
                if rule_name in self.default_rules:
                    pattern = self.default_rules[rule_name]
                    matches = list(re.finditer(pattern, text, re.IGNORECASE))

                    if matches:
                        redaction_map[rule_name] = []
                        for match in matches:
                            original = match.group(0)
                            redaction_map[rule_name].append(original)
                            replacement = redaction_char * len(original)
                            sanitized_text = sanitized_text.replace(original, replacement, 1)
                            items_redacted += 1

            # Apply custom patterns
            for pattern_config in custom_patterns:
                pattern_name = pattern_config.get("name", "custom")
                pattern = pattern_config.get("pattern")

                if pattern:
                    matches = list(re.finditer(pattern, text))
                    if matches:
                        if pattern_name not in redaction_map:
                            redaction_map[pattern_name] = []

                        for match in matches:
                            original = match.group(0)
                            redaction_map[pattern_name].append(original)
                            replacement = redaction_char * len(original)
                            sanitized_text = sanitized_text.replace(original, replacement, 1)
                            items_redacted += 1

            # Audit logging (if available)
            if hasattr(self, "audit_system"):
                self.audit_system.log_action(
                    action="text_sanitized",
                    details={
                        "rules_applied": (enabled_rules + [p.get("name") for p in custom_patterns]),
                        "items_redacted": items_redacted,
                        "text_length": len(text),
                    },
                    category="sanitizer_mcp",
                )

            return {
                "status": "success",
                "sanitized_text": sanitized_text,
                "redaction_map": redaction_map,
                "statistics": {
                    "items_redacted": items_redacted,
                    "original_length": len(text),
                    "sanitized_length": len(sanitized_text),
                    "rules_applied": enabled_rules,
                },
            }

        except Exception as e:
            logger.error(f"Sanitization error: {e}")
            if hasattr(self, "audit_system"):
                self.audit_system.log_action(
                    action="sanitization_error",
                    details={"error": str(e)},
                    category="sanitizer_mcp",
                )
            return {"status": "error", "error": str(e), "sanitized_text": text}

    def get_rules(self) -> Dict[str, Any]:
        """Get available sanitization rules."""
        return {
            "status": "success",
            "default_rules": list(self.default_rules.keys()),
            "rules": {name: {"pattern": pattern} for name, pattern in self.default_rules.items()},
        }

    def add_custom_pattern(self, name: str, pattern: str) -> Dict[str, Any]:
        """Add custom regex pattern for sanitization."""
        try:
            # Validate regex
            re.compile(pattern)
            self.default_rules[name] = pattern

            if hasattr(self, "audit_system"):
                self.audit_system.log_action(
                    action="custom_pattern_added",
                    details={"pattern_name": name},
                    category="sanitizer_mcp",
                )

            msg = f"Pattern '{name}' added successfully"
            return {"status": "success", "message": msg}
        except re.error as e:
            return {"status": "error", "error": f"Invalid regex pattern: {e}"}


if __name__ == "__main__":
    server = SanitizerMCPServer()
    # run() method not available in base MCPServer yet
