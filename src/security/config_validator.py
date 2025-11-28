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
Advanced Configuration Validation System for OmniMind.

Provides comprehensive configuration validation with:
- JSON Schema validation
- Dependency checking
- Configuration suggestions
- Auto-correction of invalid configs
- Environment-specific validations
- Migration utilities
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Type

logger = logging.getLogger(__name__)

TypeInfo = Type[Any] | tuple[Type[Any], ...]


class ConfigEnvironment(str, Enum):
    """Configuration environment types."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class ValidationSeverity(str, Enum):
    """Validation issue severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Configuration validation issue."""

    path: str
    severity: ValidationSeverity
    message: str
    suggestion: Optional[str] = None
    auto_fix: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "severity": self.severity.value,
            "message": self.message,
            "suggestion": self.suggestion,
            "auto_fix": self.auto_fix,
        }


@dataclass
class ValidationResult:
    """Configuration validation result."""

    valid: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)
    auto_fixes: Dict[str, Any] = field(default_factory=dict)
    dependencies_satisfied: bool = True
    environment_compatible: bool = True

    def add_issue(
        self,
        path: str,
        severity: ValidationSeverity,
        message: str,
        suggestion: Optional[str] = None,
        auto_fix: Optional[Any] = None,
    ) -> None:
        """Add validation issue."""
        issue = ValidationIssue(
            path=path,
            severity=severity,
            message=message,
            suggestion=suggestion,
            auto_fix=auto_fix,
        )
        self.issues.append(issue)

        if auto_fix is not None:
            self.auto_fixes[path] = auto_fix

        if severity == ValidationSeverity.ERROR:
            self.valid = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "valid": self.valid,
            "issues": [i.to_dict() for i in self.issues],
            "auto_fixes": self.auto_fixes,
            "dependencies_satisfied": self.dependencies_satisfied,
            "environment_compatible": self.environment_compatible,
            "error_count": sum(1 for i in self.issues if i.severity == ValidationSeverity.ERROR),
            "warning_count": sum(
                1 for i in self.issues if i.severity == ValidationSeverity.WARNING
            ),
        }


class ConfigurationValidator:
    """Advanced configuration validator with schema validation and auto-correction."""

    def __init__(
        self,
        schema_dir: Path = Path("config/schemas"),
        environment: ConfigEnvironment = ConfigEnvironment.DEVELOPMENT,
    ):
        """
        Initialize configuration validator.

        Args:
            schema_dir: Directory containing JSON schemas
            environment: Current environment
        """
        self.schema_dir = schema_dir
        self.environment = environment
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self.dependencies: Dict[str, Set[str]] = {}

        self._load_schemas()
        logger.info(f"Configuration validator initialized for {environment.value}")

    def _load_schemas(self) -> None:
        """Load JSON schemas from directory."""
        if not self.schema_dir.exists():
            logger.warning(f"Schema directory not found: {self.schema_dir}")
            return

        for schema_file in self.schema_dir.glob("*.json"):
            try:
                with schema_file.open() as f:
                    schema = json.load(f)
                    schema_name = schema_file.stem
                    self.schemas[schema_name] = schema
                    logger.debug(f"Loaded schema: {schema_name}")
            except Exception as e:
                logger.error(f"Failed to load schema {schema_file}: {e}")

    def validate_config(
        self,
        config: Dict[str, Any],
        schema_name: str = "omnimind",
        check_dependencies: bool = True,
        check_environment: bool = True,
    ) -> ValidationResult:
        """
        Validate configuration against schema.

        Args:
            config: Configuration dictionary
            schema_name: Name of schema to validate against
            check_dependencies: Check configuration dependencies
            check_environment: Check environment compatibility

        Returns:
            Validation result with issues and suggestions
        """
        result = ValidationResult()

        # Schema validation
        if schema_name in self.schemas:
            self._validate_schema(config, self.schemas[schema_name], result)
        else:
            result.add_issue(
                path="",
                severity=ValidationSeverity.WARNING,
                message=f"Schema '{schema_name}' not found, skipping schema validation",
            )

        # Dependency validation
        if check_dependencies:
            self._validate_dependencies(config, result)

        # Environment-specific validation
        if check_environment:
            self._validate_environment(config, result)

        # Value validation (ranges, formats, etc.)
        self._validate_values(config, result)

        return result

    def _validate_schema(
        self,
        config: Dict[str, Any],
        schema: Dict[str, Any],
        result: ValidationResult,
        path: str = "",
    ) -> None:
        """Validate configuration against JSON schema."""
        # Check required properties
        required = schema.get("required", [])
        for prop in required:
            if prop not in config:
                result.add_issue(
                    path=f"{path}.{prop}" if path else prop,
                    severity=ValidationSeverity.ERROR,
                    message=f"Required property '{prop}' is missing",
                    suggestion=f"Add '{prop}' to configuration",
                    auto_fix=self._get_default_value(schema, prop),
                )

        # Check property types
        properties = schema.get("properties", {})
        for key, value in config.items():
            current_path = f"{path}.{key}" if path else key

            if key not in properties:
                result.add_issue(
                    path=current_path,
                    severity=ValidationSeverity.WARNING,
                    message=f"Unknown property '{key}'",
                    suggestion=f"Remove '{key}' or add to schema",
                )
                continue

            prop_schema = properties[key]
            expected_type = prop_schema.get("type")

            # Type validation
            if expected_type and not self._check_type(value, expected_type):
                result.add_issue(
                    path=current_path,
                    severity=ValidationSeverity.ERROR,
                    message=(
                        f"Invalid type for '{key}': expected {expected_type}, "
                        f"got {type(value).__name__}"
                    ),
                    suggestion=f"Change '{key}' to type {expected_type}",
                    auto_fix=self._convert_type(value, expected_type),
                )

            # Nested object validation
            if expected_type == "object" and isinstance(value, dict):
                self._validate_schema(value, prop_schema, result, current_path)

    def _validate_dependencies(self, config: Dict[str, Any], result: ValidationResult) -> None:
        """Validate configuration dependencies."""
        # Check if required features are enabled when dependencies are present
        dependencies = {
            "ssl_enabled": ["ssl_cert_path", "ssl_key_path"],
            "backup_enabled": ["backup_location"],
            "monitoring_enabled": ["metrics_port"],
            "websocket_enabled": ["websocket_port"],
        }

        for feature, required_keys in dependencies.items():
            if config.get(feature, False):
                for req_key in required_keys:
                    if req_key not in config:
                        result.add_issue(
                            path=req_key,
                            severity=ValidationSeverity.ERROR,
                            message=f"'{req_key}' is required when '{feature}' is enabled",
                            suggestion=f"Add '{req_key}' configuration or disable '{feature}'",
                        )
                        result.dependencies_satisfied = False

        # Check conflicting options
        conflicts = [
            (
                "debug_mode",
                "production_mode",
                "Cannot enable both debug and production mode",
            ),
            (
                "ssl_enabled",
                "allow_http",
                "SSL enabled but HTTP is allowed - security risk",
            ),
        ]

        for key1, key2, message in conflicts:
            if config.get(key1, False) and config.get(key2, False):
                result.add_issue(
                    path=f"{key1},{key2}",
                    severity=ValidationSeverity.WARNING,
                    message=message,
                    suggestion=f"Disable either '{key1}' or '{key2}'",
                )

    def _validate_environment(self, config: Dict[str, Any], result: ValidationResult) -> None:
        """Validate environment-specific requirements."""
        # Production environment checks
        if self.environment == ConfigEnvironment.PRODUCTION:
            # SSL must be enabled in production
            if not config.get("ssl_enabled", False):
                result.add_issue(
                    path="ssl_enabled",
                    severity=ValidationSeverity.ERROR,
                    message="SSL must be enabled in production",
                    suggestion="Set 'ssl_enabled' to true",
                    auto_fix=True,
                )
                result.environment_compatible = False

            # Debug mode should be disabled
            if config.get("debug_mode", False):
                result.add_issue(
                    path="debug_mode",
                    severity=ValidationSeverity.WARNING,
                    message="Debug mode should be disabled in production",
                    suggestion="Set 'debug_mode' to false",
                    auto_fix=False,
                )

            # Backup should be enabled
            if not config.get("backup_enabled", False):
                result.add_issue(
                    path="backup_enabled",
                    severity=ValidationSeverity.WARNING,
                    message="Backup should be enabled in production",
                    suggestion="Enable automated backups for disaster recovery",
                    auto_fix=True,
                )

        # Development environment checks
        elif self.environment == ConfigEnvironment.DEVELOPMENT:
            # Allow self-signed certificates
            if config.get("ssl_enabled") and not config.get("allow_self_signed"):
                result.add_issue(
                    path="allow_self_signed",
                    severity=ValidationSeverity.INFO,
                    message="Consider allowing self-signed certificates in development",
                    suggestion="Set 'allow_self_signed' to true for easier development",
                    auto_fix=True,
                )

    def _validate_values(self, config: Dict[str, Any], result: ValidationResult) -> None:
        """Validate specific configuration values."""
        # Port ranges
        port_configs = ["port", "websocket_port", "metrics_port"]
        for port_key in port_configs:
            if port_key in config:
                port = config[port_key]
                if not isinstance(port, int) or port < 1024 or port > 65535:
                    result.add_issue(
                        path=port_key,
                        severity=ValidationSeverity.ERROR,
                        message=f"Invalid port number: {port}",
                        suggestion="Use a port between 1024 and 65535",
                        auto_fix=8000 if port_key == "port" else 8001,
                    )

        # File paths existence
        path_configs = ["ssl_cert_path", "ssl_key_path", "backup_location"]
        for path_key in path_configs:
            if path_key in config and config.get("ssl_enabled", False):
                path_value = config[path_key]
                if path_value and not Path(path_value).exists():
                    result.add_issue(
                        path=path_key,
                        severity=ValidationSeverity.WARNING,
                        message=f"Path does not exist: {path_value}",
                        suggestion="Create the directory or update the path",
                    )

        # URL validation
        if "base_url" in config:
            url = config["base_url"]
            if not (url.startswith("http://") or url.startswith("https://")):
                result.add_issue(
                    path="base_url",
                    severity=ValidationSeverity.ERROR,
                    message="Invalid URL format",
                    suggestion="URL must start with http:// or https://",
                    auto_fix=f"http://{url}",
                )

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_map: dict[str, TypeInfo] = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        expected_python_type: Optional[TypeInfo] = type_map.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        return True

    def _convert_type(self, value: Any, target_type: str) -> Any:
        """Attempt to convert value to target type."""
        try:
            if target_type == "string":
                return str(value)
            elif target_type == "integer":
                return int(value)
            elif target_type == "number":
                return float(value)
            elif target_type == "boolean":
                if isinstance(value, str):
                    return value.lower() in ("true", "1", "yes")
                return bool(value)
        except (ValueError, TypeError):
            pass
        return None

    def _get_default_value(self, schema: Dict[str, Any], prop: str) -> Optional[Any]:
        """Get default value for a property from schema."""
        properties = schema.get("properties", {})
        if prop in properties:
            return properties[prop].get("default")
        return None

    def apply_auto_fixes(
        self, config: Dict[str, Any], validation_result: ValidationResult
    ) -> Dict[str, Any]:
        """
        Apply auto-fixes to configuration.

        Args:
            config: Original configuration
            validation_result: Validation result with auto-fixes

        Returns:
            Fixed configuration
        """
        fixed_config = config.copy()

        for path, fix_value in validation_result.auto_fixes.items():
            if fix_value is not None:
                # Handle nested paths
                keys = path.split(".")
                current = fixed_config

                for key in keys[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]

                current[keys[-1]] = fix_value
                logger.info(f"Auto-fixed config: {path} = {fix_value}")

        return fixed_config

    def suggest_configuration(
        self, partial_config: Dict[str, Any], schema_name: str = "omnimind"
    ) -> List[str]:
        """
        Generate configuration suggestions based on partial config.

        Args:
            partial_config: Incomplete configuration
            schema_name: Schema to use for suggestions

        Returns:
            List of suggested configuration keys
        """
        suggestions: List[str] = []

        if schema_name not in self.schemas:
            return suggestions

        schema = self.schemas[schema_name]
        properties = schema.get("properties", {})

        # Suggest required properties that are missing
        required = schema.get("required", [])
        for prop in required:
            if prop not in partial_config:
                prop_schema = properties.get(prop, {})
                description = prop_schema.get("description", "")
                suggestions.append(f"{prop} (required): {description}")

        # Suggest optional but recommended properties
        for prop, prop_schema in properties.items():
            if prop not in partial_config and prop not in required:
                if prop_schema.get("recommended", False):
                    description = prop_schema.get("description", "")
                    suggestions.append(f"{prop} (recommended): {description}")

        return suggestions

    def migrate_config(
        self,
        old_config: Dict[str, Any],
        from_version: str,
        to_version: str,
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        Migrate configuration from one version to another.

        Args:
            old_config: Configuration in old version
            from_version: Source version
            to_version: Target version

        Returns:
            Tuple of (migrated_config, migration_notes)
        """
        new_config = old_config.copy()
        migration_notes = []

        # Define migration rules
        MigrationRule = tuple[str, Optional[str], str]
        migrations: dict[tuple[str, str], list[MigrationRule]] = {
            ("1.0", "2.0"): [
                ("daemon_port", "port", "Renamed 'daemon_port' to 'port'"),
                ("enable_ssl", "ssl_enabled", "Renamed 'enable_ssl' to 'ssl_enabled'"),
            ],
            ("2.0", "3.0"): [
                (
                    "websocket_url",
                    None,
                    "Removed 'websocket_url' (now auto-configured)",
                ),
            ],
        }

        migration_key = (from_version, to_version)
        if migration_key in migrations:
            for old_key, new_key, note in migrations[migration_key]:
                if old_key in new_config:
                    if new_key:
                        new_config[new_key] = new_config.pop(old_key)
                    else:
                        del new_config[old_key]
                    migration_notes.append(note)

        return new_config, migration_notes

    def export_validation_report(
        self, validation_result: ValidationResult, output_path: Path
    ) -> None:
        """
        Export validation report to file.

        Args:
            validation_result: Validation result
            output_path: Output file path
        """
        report = {
            "timestamp": os.environ.get("BUILD_TIMESTAMP", "unknown"),
            "environment": self.environment.value,
            "result": validation_result.to_dict(),
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Validation report exported to {output_path}")

    def run_health_checks(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run pre-deployment health checks.

        Args:
            config: Configuration dictionary

        Returns:
            Health check results
        """
        logger.info("Running pre-deployment health checks...")

        checks: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {},
        }

        # Check 1: Port availability
        port_check = self._check_port_availability(config)
        checks["checks"]["port_availability"] = port_check
        if not port_check["passed"]:
            checks["overall_status"] = "unhealthy"

        # Check 2: File paths
        path_check = self._check_file_paths(config)
        checks["checks"]["file_paths"] = path_check
        if not path_check["passed"]:
            checks["overall_status"] = "warning"

        # Check 3: Dependencies
        dep_check = self._check_dependencies()
        checks["checks"]["dependencies"] = dep_check
        if not dep_check["passed"]:
            checks["overall_status"] = "unhealthy"

        # Check 4: Disk space
        disk_check = self._check_disk_space()
        checks["checks"]["disk_space"] = disk_check
        if not disk_check["passed"]:
            checks["overall_status"] = "warning"

        # Check 5: Memory
        memory_check = self._check_memory()
        checks["checks"]["memory"] = memory_check
        if not memory_check["passed"]:
            checks["overall_status"] = "warning"

        logger.info(f"Health check completed: {checks['overall_status']}")

        return checks

    def _check_port_availability(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check if configured ports are available."""
        import socket

        result: Dict[str, Any] = {"passed": True, "details": [], "errors": []}

        ports_to_check = []
        if "port" in config:
            ports_to_check.append(("main", config["port"]))
        if "websocket_port" in config:
            ports_to_check.append(("websocket", config["websocket_port"]))
        if "metrics_port" in config:
            ports_to_check.append(("metrics", config["metrics_port"]))

        for name, port in ports_to_check:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result_code = s.connect_ex(("localhost", port))
                    if result_code == 0:
                        result["errors"].append(f"Port {port} ({name}) is already in use")
                        result["passed"] = False
                    else:
                        result["details"].append(f"Port {port} ({name}) is available")
            except Exception as e:
                result["errors"].append(f"Failed to check port {port}: {e}")
                result["passed"] = False

        return result

    def _check_file_paths(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check if configured file paths exist and are accessible."""
        result: Dict[str, Any] = {"passed": True, "details": [], "warnings": []}

        path_configs = [
            "ssl_cert_path",
            "ssl_key_path",
            "backup_location",
            "log_directory",
        ]

        for key in path_configs:
            if key in config:
                path = Path(config[key])
                if not path.exists():
                    # Create directories if they don't exist
                    if key in ["backup_location", "log_directory"]:
                        try:
                            path.mkdir(parents=True, exist_ok=True)
                            result["details"].append(f"Created directory: {path}")
                        except Exception as e:
                            result["warnings"].append(f"Could not create {key}: {path} - {e}")
                    else:
                        result["warnings"].append(f"{key} does not exist: {path}")
                else:
                    result["details"].append(f"{key} exists: {path}")

        return result

    def _check_dependencies(self) -> Dict[str, Any]:
        """Check if required Python dependencies are installed."""
        result: Dict[str, Any] = {"passed": True, "details": [], "errors": []}

        required_packages = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "structlog",
            "psutil",
        ]

        for package in required_packages:
            try:
                __import__(package)
                result["details"].append(f"{package} is installed")
            except ImportError:
                result["errors"].append(f"{package} is not installed")
                result["passed"] = False

        return result

    def _check_disk_space(self, min_gb: int = 5) -> Dict[str, Any]:
        """Check available disk space."""
        import shutil

        result: Dict[str, Any] = {"passed": True, "details": [], "warnings": []}

        try:
            total, used, free = shutil.disk_usage("/")
            free_gb = free / (1024**3)

            result["details"].append(
                f"Free disk space: {free_gb:.2f} GB / {total / (1024**3):.2f} GB"
            )

            if free_gb < min_gb:
                result["warnings"].append(
                    f"Low disk space: {free_gb:.2f} GB (minimum: {min_gb} GB)"
                )
                result["passed"] = False

        except Exception as e:
            result["errors"] = [f"Failed to check disk space: {e}"]
            result["passed"] = False

        return result

    def _check_memory(self, min_gb: int = 2) -> Dict[str, Any]:
        """Check available memory."""
        import psutil

        result: Dict[str, Any] = {"passed": True, "details": [], "warnings": []}

        try:
            mem = psutil.virtual_memory()
            available_gb = mem.available / (1024**3)

            result["details"].append(
                f"Available memory: {available_gb:.2f} GB / {mem.total / (1024**3):.2f} GB"
            )

            if available_gb < min_gb:
                result["warnings"].append(
                    f"Low memory: {available_gb:.2f} GB (minimum: {min_gb} GB)"
                )
                result["passed"] = False

        except Exception as e:
            result["errors"] = [f"Failed to check memory: {e}"]
            result["passed"] = False

        return result
