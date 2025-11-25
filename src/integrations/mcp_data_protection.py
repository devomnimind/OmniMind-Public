"""
Sistema de Proteção de Dados para MCPs.

Implementa proteção abrangente de dados sensíveis antes de enviar para MCPs,
incluindo detecção, proteção (hash/criptografia/máscara), sanitização e auditoria.

Baseado nos requisitos de segurança LGPD e zero vazamento de dados.
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Tuple

from cryptography.fernet import Fernet

from src.audit.immutable_audit import get_audit_system
from src.security.dlp import DLPValidator, DLPViolation

logger = logging.getLogger(__name__)


@dataclass
class SensitivePattern:
    """Padrão para detectar dados sensíveis."""

    name: str
    pattern: str
    severity: str  # "critical", "high", "medium", "low"
    action: str  # "hash", "encrypt", "mask", "remove"
    description: str = ""
    compiled: Optional[Pattern[str]] = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Compila o padrão regex."""
        self.compiled = re.compile(self.pattern, re.IGNORECASE | re.MULTILINE)


@dataclass
class ProtectionResult:
    """Resultado da proteção de dados."""

    original_size: int
    protected_size: int
    detections: List[Dict[str, Any]] = field(default_factory=list)
    actions_taken: List[str] = field(default_factory=list)
    sanitized: bool = False
    safe: bool = True
    violations: List[DLPViolation] = field(default_factory=list)


class DataProtectionError(Exception):
    """Erro na proteção de dados."""

    pass


class MCPDataProtection:
    """
    Sistema de proteção de dados para MCPs.

    Protege dados sensíveis antes de enviar para MCPs, Cursor ou qualquer
    plataforma externa. Implementa:

    1. Detecção de dados sensíveis (regex, campos predeterminados)
    2. Proteção (hash irreversível, criptografia, máscara parcial)
    3. Sanitização (remoção de metadados, paths absolutos)
    4. Auditoria completa de todas ações
    """

    # Padrões padrão para detecção de dados sensíveis
    DEFAULT_PATTERNS = [
        SensitivePattern(
            name="api_key",
            pattern=r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{10,})['\"]?",
            severity="critical",
            action="hash",
            description="API keys e tokens de autenticação",
        ),
        SensitivePattern(
            name="secret_key",
            pattern=r"(?i)(secret[_-]?key|secret)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{10,})['\"]?",
            severity="critical",
            action="hash",
            description="Secret keys",
        ),
        SensitivePattern(
            name="password",
            pattern=r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?([^\s'\"]{6,})['\"]?",
            severity="critical",
            action="hash",
            description="Passwords",
        ),
        SensitivePattern(
            name="token",
            pattern=r"(?i)(token|bearer)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{20,})['\"]?",
            severity="critical",
            action="hash",
            description="Authentication tokens",
        ),
        SensitivePattern(
            name="aws_key",
            pattern=r"(?i)(AKIA[0-9A-Z]{16})",
            severity="critical",
            action="hash",
            description="AWS Access Keys",
        ),
        SensitivePattern(
            name="private_key",
            pattern=r"-----BEGIN\s+(RSA\s+)?PRIVATE KEY-----",
            severity="critical",
            action="remove",
            description="Private keys (RSA, etc)",
        ),
        SensitivePattern(
            name="jwt_token",
            pattern=r"eyJ[a-zA-Z0-9_\-]*\.eyJ[a-zA-Z0-9_\-]*\.[a-zA-Z0-9_\-]*",
            severity="high",
            action="hash",
            description="JWT tokens",
        ),
        SensitivePattern(
            name="email",
            pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            severity="medium",
            action="mask",
            description="Email addresses",
        ),
        SensitivePattern(
            name="ipv4_private",
            pattern=(
                r"\b(10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
                r"|172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}"
                r"|192\.168\.\d{1,3}\.\d{1,3})\b"
            ),
            severity="medium",
            action="mask",
            description="Private IPv4 addresses",
        ),
        SensitivePattern(
            name="credit_card",
            pattern=r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
            severity="critical",
            action="hash",
            description="Credit card numbers",
        ),
        SensitivePattern(
            name="phone_br",
            pattern=r"\b(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}[-\s]?\d{4}\b",
            severity="medium",
            action="mask",
            description="Brazilian phone numbers",
        ),
    ]

    # Campos sensíveis predeterminados
    SENSITIVE_FIELDS = {
        "password",
        "secret",
        "token",
        "api_key",
        "apikey",
        "private_key",
        "access_token",
        "refresh_token",
        "session_id",
        "cookie",
        "authorization",
        "x-api-key",
        "credentials",
    }

    # Metadados a remover na sanitização
    METADATA_TO_REMOVE = {
        "__pycache__",
        ".git",
        ".env",
        "node_modules",
        ".venv",
        "venv",
        "__version__",
        "__author__",
        "__file__",
    }

    def __init__(
        self,
        encryption_key: Optional[bytes] = None,
        enable_cache: bool = True,
        enable_audit: bool = True,
    ) -> None:
        """
        Inicializa o sistema de proteção de dados.

        Args:
            encryption_key: Chave de criptografia Fernet. Se None, gera uma nova.
            enable_cache: Habilita cache de resultados.
            enable_audit: Habilita auditoria de ações.
        """
        self.patterns = self.DEFAULT_PATTERNS.copy()
        self.dlp_validator = DLPValidator()
        self.audit_system = get_audit_system() if enable_audit else None
        self.enable_audit = enable_audit
        self.enable_cache = enable_cache

        # Criptografia
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)

        # Cache para evitar reprocessamento
        self._hash_cache: Dict[str, str] = {} if enable_cache else {}
        self._detection_cache: Dict[str, List[Dict[str, Any]]] = {} if enable_cache else {}

        # Estatísticas
        self.stats = {
            "total_detections": 0,
            "hashed": 0,
            "encrypted": 0,
            "masked": 0,
            "removed": 0,
            "sanitized": 0,
        }

        logger.info("MCPDataProtection inicializado com %d padrões", len(self.patterns))

    def add_pattern(self, pattern: SensitivePattern) -> None:
        """Adiciona um padrão customizado de detecção."""
        self.patterns.append(pattern)
        logger.info("Padrão adicionado: %s", pattern.name)

    def _hash_data(self, data: str) -> str:
        """Hash irreversível SHA-256."""
        if self.enable_cache and data in self._hash_cache:
            return self._hash_cache[data]

        hashed = hashlib.sha256(data.encode()).hexdigest()[:16]

        if self.enable_cache:
            self._hash_cache[data] = hashed

        self.stats["hashed"] += 1
        return f"[HASHED:{hashed}]"

    def _encrypt_data(self, data: str) -> str:
        """Criptografia reversível."""
        encrypted = self.cipher.encrypt(data.encode()).decode()
        self.stats["encrypted"] += 1
        return f"[ENCRYPTED:{encrypted[:32]}...]"

    def _mask_data(self, data: str, keep_chars: int = 3) -> str:
        """Máscara parcial (mantém alguns caracteres)."""
        if len(data) <= keep_chars * 2:
            return "*" * len(data)

        masked = data[:keep_chars] + "*" * (len(data) - keep_chars * 2) + data[-keep_chars:]
        self.stats["masked"] += 1
        return masked

    def detect_sensitive_data(self, content: str) -> List[Dict[str, Any]]:
        """
        Detecta dados sensíveis no conteúdo.

        Args:
            content: Conteúdo a analisar.

        Returns:
            Lista de detecções com detalhes.
        """
        # Cache check
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if self.enable_cache and content_hash in self._detection_cache:
            return self._detection_cache[content_hash]

        detections = []

        for pattern in self.patterns:
            if pattern.compiled is None:
                continue

            matches = pattern.compiled.finditer(content)

            for match in matches:
                detection = {
                    "pattern": pattern.name,
                    "severity": pattern.severity,
                    "action": pattern.action,
                    "position": match.span(),
                    "snippet": match.group(0)[:50],  # Primeiros 50 chars
                    "description": pattern.description,
                }
                detections.append(detection)
                self.stats["total_detections"] += 1

        # Cache result
        if self.enable_cache:
            self._detection_cache[content_hash] = detections

        return detections

    def protect_content(self, content: str) -> Tuple[str, ProtectionResult]:
        """
        Protege dados sensíveis no conteúdo.

        Args:
            content: Conteúdo a proteger.

        Returns:
            Tupla (conteúdo protegido, resultado da proteção).
        """
        original_size = len(content)
        protected = content
        actions_taken = []

        # Aplicar proteções padrão por padrão baseadas em regex
        for pattern in self.patterns:
            if pattern.compiled is None:
                continue

            def replace_match(match: re.Match[str]) -> str:
                """Função de substituição para cada match."""
                full_match = match.group(0)

                if pattern.action == "hash":
                    # Hash do valor sensível (grupo 2 se existe, senão full match)
                    if len(match.groups()) >= 2:
                        sensitive_value = match.group(2)
                    else:
                        sensitive_value = full_match

                    hashed = self._hash_data(sensitive_value)
                    self.stats["hashed"] += 1
                    actions_taken.append(f"Hashed {pattern.name}")

                    # Retornar o match com valor substituído por hash
                    if len(match.groups()) >= 2:
                        return match.group(1) + "=" + hashed
                    return hashed

                elif pattern.action == "encrypt":
                    if len(match.groups()) >= 2:
                        sensitive_value = match.group(2)
                    else:
                        sensitive_value = full_match

                    encrypted = self._encrypt_data(sensitive_value)
                    self.stats["encrypted"] += 1
                    actions_taken.append(f"Encrypted {pattern.name}")

                    if len(match.groups()) >= 2:
                        return match.group(1) + "=" + encrypted
                    return encrypted

                elif pattern.action == "mask":
                    if len(match.groups()) >= 2:
                        sensitive_value = match.group(2)
                    else:
                        sensitive_value = full_match

                    masked = self._mask_data(sensitive_value)
                    self.stats["masked"] += 1
                    actions_taken.append(f"Masked {pattern.name}")

                    if len(match.groups()) >= 2:
                        return match.group(1) + "=" + masked
                    return masked

                elif pattern.action == "remove":
                    self.stats["removed"] += 1
                    actions_taken.append(f"Removed {pattern.name}")
                    return "[REMOVED]"

                return full_match

            # Apply regex substitution
            protected = pattern.compiled.sub(replace_match, protected)

        # Get detections for result
        detections = self.detect_sensitive_data(content)

        # DLP validation
        violations = []
        dlp_violation = self.dlp_validator.validate(protected)
        if dlp_violation:
            violations.append(dlp_violation)

        result = ProtectionResult(
            original_size=original_size,
            protected_size=len(protected),
            detections=detections,
            actions_taken=actions_taken,
            safe=len(violations) == 0,
            violations=violations,
        )

        # Audit
        if self.enable_audit and self.audit_system and detections:
            self.audit_system.log_action(
                action="data_protection",
                details={
                    "detections": len(detections),
                    "actions": actions_taken,
                    "safe": result.safe,
                },
                category="mcp_data_protection",
            )

        return protected, result

    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza dicionário removendo campos sensíveis e metadados.

        Args:
            data: Dicionário a sanitizar.

        Returns:
            Dicionário sanitizado.
        """
        sanitized: Dict[str, Any] = {}

        for key, value in data.items():
            # Remover campos sensíveis
            if key.lower() in self.SENSITIVE_FIELDS:
                sanitized[key] = "[PROTECTED]"
                continue

            # Remover metadados
            if any(meta in key for meta in self.METADATA_TO_REMOVE):
                continue

            # Recursivo para dicts aninhados
            if isinstance(value, dict):
                sanitized[key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self.sanitize_dict(item) if isinstance(item, dict) else item for item in value
                ]
            elif isinstance(value, str):
                # Proteger strings
                protected, _ = self.protect_content(value)
                sanitized[key] = protected
            else:
                sanitized[key] = value

        self.stats["sanitized"] += 1
        return sanitized

    def sanitize_path(self, path: str) -> str:
        """
        Sanitiza paths absolutos para relativos.

        Args:
            path: Path a sanitizar.

        Returns:
            Path sanitizado.
        """
        path_obj = Path(path)

        # Converter para relativo se for absoluto
        if path_obj.is_absolute():
            try:
                # Tentar relativizar ao diretório de trabalho
                cwd = Path.cwd()
                relative = path_obj.relative_to(cwd)
                return str(relative)
            except ValueError:
                # Se não conseguir, pelo menos remover parte do path
                parts = path_obj.parts
                # Manter apenas últimos 3 componentes
                return str(Path(*parts[-3:]))

        return path

    def sanitize_for_mcp(
        self, data: Any, remove_paths: bool = True
    ) -> Tuple[Any, ProtectionResult]:
        """
        Sanitiza dados antes de enviar para MCP.

        Este é o método principal que deve ser usado antes de qualquer
        envio de dados para MCPs, Cursor ou plataformas externas.

        Args:
            data: Dados a sanitizar (str, dict, list, etc).
            remove_paths: Se True, sanitiza paths absolutos.

        Returns:
            Tupla (dados sanitizados, resultado da proteção).
        """
        actions_taken = []

        if isinstance(data, str):
            # Sanitizar paths se solicitado
            if remove_paths and "/" in data:
                data = self.sanitize_path(data)
                actions_taken.append("Path sanitized")

            # Proteger conteúdo
            protected, result = self.protect_content(data)
            result.actions_taken.extend(actions_taken)
            result.sanitized = True
            return protected, result

        elif isinstance(data, dict):
            # Sanitizar dict
            sanitized = self.sanitize_dict(data)

            # Sanitizar paths em valores
            if remove_paths:
                for key, value in sanitized.items():
                    if isinstance(value, str) and "/" in value:
                        sanitized[key] = self.sanitize_path(value)

            result = ProtectionResult(
                original_size=len(str(data)),
                protected_size=len(str(sanitized)),
                actions_taken=["Dictionary sanitized"],
                sanitized=True,
            )

            if self.enable_audit and self.audit_system:
                self.audit_system.log_action(
                    action="sanitize_for_mcp",
                    details={"type": "dict", "keys": len(sanitized)},
                    category="mcp_data_protection",
                )

            return sanitized, result

        elif isinstance(data, list):
            # Sanitizar lista
            sanitized_list: List[Any] = []
            for item in data:
                sanitized_item, _ = self.sanitize_for_mcp(item, remove_paths)
                sanitized_list.append(sanitized_item)

            result = ProtectionResult(
                original_size=len(str(data)),
                protected_size=len(str(sanitized_list)),
                actions_taken=["List sanitized"],
                sanitized=True,
            )

            return sanitized_list, result

        else:
            # Tipos primitivos (int, float, bool, None)
            result = ProtectionResult(
                original_size=len(str(data)),
                protected_size=len(str(data)),
                sanitized=True,
            )
            return data, result

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso."""
        return {
            "total_detections": self.stats["total_detections"],
            "actions": {
                "hashed": self.stats["hashed"],
                "encrypted": self.stats["encrypted"],
                "masked": self.stats["masked"],
                "removed": self.stats["removed"],
            },
            "sanitized": self.stats["sanitized"],
            "cache_size": len(self._hash_cache) if self.enable_cache else 0,
        }

    def clear_cache(self) -> None:
        """Limpa caches internos."""
        self._hash_cache.clear()
        self._detection_cache.clear()
        logger.info("Cache limpo")


# Instância global para uso conveniente
_global_protection: Optional[MCPDataProtection] = None


def get_data_protection() -> MCPDataProtection:
    """Retorna instância global do sistema de proteção."""
    global _global_protection
    if _global_protection is None:
        _global_protection = MCPDataProtection()
    return _global_protection


def protect_for_mcp(data: Any) -> Tuple[Any, ProtectionResult]:
    """
    Função conveniente para proteger dados antes de enviar para MCP.

    Args:
        data: Dados a proteger.

    Returns:
        Tupla (dados protegidos, resultado).
    """
    protection = get_data_protection()
    return protection.sanitize_for_mcp(data)
