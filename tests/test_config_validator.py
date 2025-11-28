from __future__ import annotations

import json
from pathlib import Path
import pytest
from src.security.config_validator import (
    import json


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
Tests for Advanced Configuration Validator.
"""




    ConfigEnvironment,
    ConfigurationValidator,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
)


@pytest.fixture
def temp_schema_dir(tmp_path: Path) -> Path:
    """Create temporary schema directory."""
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()

    # Create a sample schema
    sample_schema = {
        "type": "object",
        "required": ["port"],
        "properties": {
            "port": {"type": "integer", "minimum": 1024, "maximum": 65535},
            "debug_mode": {"type": "boolean"},
            "base_url": {"type": "string", "pattern": "^https?://"},
        },
    }

    schema_file = schema_dir / "omnimind.json"
    with schema_file.open("w") as f:
        json.dump(sample_schema, f)

    return schema_dir


@pytest.fixture
def validator(temp_schema_dir: Path) -> ConfigurationValidator:
    """Create configuration validator instance."""
    return ConfigurationValidator(
        schema_dir=temp_schema_dir,
        environment=ConfigEnvironment.DEVELOPMENT,
    )


def test_validator_initialization(validator: ConfigurationValidator, temp_schema_dir: Path) -> None:
    """Test validator initializes correctly."""
    assert validator.schema_dir == temp_schema_dir
    assert validator.environment == ConfigEnvironment.DEVELOPMENT


def test_validate_config_basic(validator: ConfigurationValidator) -> None:
    """Test basic configuration validation."""
    config = {
        "port": 8000,
        "debug_mode": True,
    }

    result = validator.validate_config(config, check_dependencies=False)

    # Should have no errors for basic config
    assert result.valid or len(result.issues) == 0


def test_validate_port_range(validator: ConfigurationValidator) -> None:
    """Test port validation."""
    # Invalid port (too low)
    config = {"port": 100}
    result = validator.validate_config(config, check_dependencies=False)

    port_errors = [i for i in result.issues if i.path == "port"]
    assert len(port_errors) > 0
    assert any(i.severity == ValidationSeverity.ERROR for i in port_errors)

    # Valid port
    config = {"port": 8000}
    result = validator.validate_config(config, check_dependencies=False)

    port_errors = [i for i in result.issues if i.path == "port"]
    port_error_count = sum(1 for i in port_errors if i.severity == ValidationSeverity.ERROR)
    assert port_error_count == 0


def test_validate_url_format(validator: ConfigurationValidator) -> None:
    """Test URL validation."""
    # Invalid URL (no protocol)
    config = {"base_url": "localhost:8000"}
    result = validator.validate_config(config, check_dependencies=False)

    url_errors = [i for i in result.issues if i.path == "base_url"]
    assert len(url_errors) > 0
    assert any(i.auto_fix is not None for i in url_errors)

    # Valid URL
    config = {"base_url": "http://localhost:8000"}
    result = validator.validate_config(config, check_dependencies=False)

    url_errors = [i for i in result.issues if i.path == "base_url"]
    url_error_count = sum(1 for i in url_errors if i.severity == ValidationSeverity.ERROR)
    assert url_error_count == 0


def test_validate_dependencies(validator: ConfigurationValidator) -> None:
    """Test dependency validation."""
    # SSL enabled but missing required keys
    config = {
        "ssl_enabled": True,
        # Missing: ssl_cert_path, ssl_key_path
    }

    result = validator.validate_config(config)

    assert result.dependencies_satisfied is False
    cert_errors = [i for i in result.issues if "ssl_cert_path" in i.path]
    key_errors = [i for i in result.issues if "ssl_key_path" in i.path]

    assert len(cert_errors) > 0
    assert len(key_errors) > 0


def test_production_environment_validation(temp_schema_dir: Path) -> None:
    """Test production environment validation."""
    validator = ConfigurationValidator(
        schema_dir=temp_schema_dir,
        environment=ConfigEnvironment.PRODUCTION,
    )

    # SSL should be required in production
    config = {
        "ssl_enabled": False,
        "debug_mode": True,  # Should warn in production
    }

    result = validator.validate_config(config, check_dependencies=False)

    assert result.environment_compatible is False

    ssl_errors = [i for i in result.issues if i.path == "ssl_enabled"]
    debug_warnings = [i for i in result.issues if i.path == "debug_mode"]

    assert len(ssl_errors) > 0
    assert any(i.severity == ValidationSeverity.ERROR for i in ssl_errors)
    assert len(debug_warnings) > 0


def test_auto_fix_application(validator: ConfigurationValidator) -> None:
    """Test auto-fix application."""
    config = {
        "port": 100,  # Invalid port
        "base_url": "localhost:8000",  # Invalid URL
    }

    result = validator.validate_config(config, check_dependencies=False)

    # Check auto-fixes are available
    assert len(result.auto_fixes) > 0

    # Apply auto-fixes
    fixed_config = validator.apply_auto_fixes(config, result)

    # Verify fixes were applied
    assert fixed_config["port"] in [8000, 8001]  # Valid port
    assert fixed_config["base_url"].startswith("http://")


def test_configuration_suggestions(validator: ConfigurationValidator) -> None:
    """Test configuration suggestions."""
    partial_config = {
        "port": 8000,
    }

    suggestions = validator.suggest_configuration(partial_config)

    # Should suggest some configurations
    assert isinstance(suggestions, list)


def test_config_migration(validator: ConfigurationValidator) -> None:
    """Test configuration migration."""
    old_config = {
        "daemon_port": 8000,
        "enable_ssl": True,
    }

    new_config, notes = validator.migrate_config(
        old_config,
        from_version="1.0",
        to_version="2.0",
    )

    # Check migrations were applied
    assert "port" in new_config
    assert "ssl_enabled" in new_config
    assert "daemon_port" not in new_config
    assert "enable_ssl" not in new_config

    # Check migration notes
    assert len(notes) > 0


def test_validation_result_to_dict(validator: ConfigurationValidator) -> None:
    """Test validation result serialization."""
    config = {"port": 100}
    result = validator.validate_config(config, check_dependencies=False)

    result_dict = result.to_dict()

    assert "valid" in result_dict
    assert "issues" in result_dict
    assert "auto_fixes" in result_dict
    assert "error_count" in result_dict
    assert "warning_count" in result_dict


def test_validation_issue_to_dict() -> None:
    """Test validation issue serialization."""

    issue = ValidationIssue(
        path="port",
        severity=ValidationSeverity.ERROR,
        message="Invalid port",
        suggestion="Use port 8000",
        auto_fix=8000,
    )

    issue_dict = issue.to_dict()

    assert issue_dict["path"] == "port"
    assert issue_dict["severity"] == "error"
    assert issue_dict["message"] == "Invalid port"
    assert issue_dict["suggestion"] == "Use port 8000"
    assert issue_dict["auto_fix"] == 8000


def test_export_validation_report(validator: ConfigurationValidator, tmp_path: Path) -> None:
    """Test validation report export."""
    config = {"port": 100}
    result = validator.validate_config(config, check_dependencies=False)

    output_path = tmp_path / "validation_report.json"
    validator.export_validation_report(result, output_path)

    assert output_path.exists()

    # Verify report contents

    with output_path.open() as f:
        report = json.load(f)

    assert "timestamp" in report
    assert "environment" in report
    assert "result" in report


def test_conflicting_options(validator: ConfigurationValidator) -> None:
    """Test conflicting configuration options."""
    config = {
        "debug_mode": True,
        "production_mode": True,  # Conflicting with debug_mode
    }

    result = validator.validate_config(config)

    # Should have warnings about conflicting options
    conflict_warnings = [
        i
        for i in result.issues
        if i.severity == ValidationSeverity.WARNING
        and ("debug_mode" in i.path or "production_mode" in i.path)
    ]

    assert len(conflict_warnings) > 0


def test_type_conversion(validator: ConfigurationValidator) -> None:
    """Test type conversion in auto-fixes."""
    # Test string to int conversion
    assert validator._convert_type("8000", "integer") == 8000

    # Test string to bool conversion
    assert validator._convert_type("true", "boolean") is True
    assert validator._convert_type("false", "boolean") is False

    # Test number to string conversion
    assert validator._convert_type(8000, "string") == "8000"


def test_development_environment_validation(temp_schema_dir: Path) -> None:
    """Test development environment specific validation."""
    validator = ConfigurationValidator(
        schema_dir=temp_schema_dir,
        environment=ConfigEnvironment.DEVELOPMENT,
    )

    config = {
        "ssl_enabled": True,
        "allow_self_signed": False,
    }

    result = validator.validate_config(config, check_dependencies=False)

    # Should suggest allowing self-signed certs in dev
    self_signed_issues = [i for i in result.issues if "allow_self_signed" in i.path]

    assert len(self_signed_issues) > 0


def test_schema_loading_nonexistent_dir(tmp_path: Path) -> None:
    """Test schema loading with nonexistent directory."""
    nonexistent_dir = tmp_path / "nonexistent"

    validator = ConfigurationValidator(
        schema_dir=nonexistent_dir,
        environment=ConfigEnvironment.TEST,
    )

    # Should handle missing schema directory gracefully
    assert len(validator.schemas) == 0


def test_schema_loading_invalid_json(tmp_path: Path) -> None:
    """Test schema loading with invalid JSON."""
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()

    # Create invalid JSON file
    invalid_file = schema_dir / "invalid.json"
    invalid_file.write_text("{ invalid json }")

    validator = ConfigurationValidator(
        schema_dir=schema_dir,
        environment=ConfigEnvironment.DEVELOPMENT,
    )

    # Should skip invalid schema
    assert "invalid" not in validator.schemas


def test_validate_schema_required_properties(validator: ConfigurationValidator) -> None:
    """Test schema validation for required properties."""
    # Missing required property 'port'
    config = {
        "debug_mode": True,
    }

    result = validator.validate_config(config, check_dependencies=False, check_environment=False)

    # Should have error for missing required property
    port_errors = [
        i for i in result.issues if "port" in i.path and i.severity == ValidationSeverity.ERROR
    ]
    assert len(port_errors) > 0
    assert not result.valid


def test_validate_schema_unknown_properties(validator: ConfigurationValidator) -> None:
    """Test schema validation for unknown properties."""
    config = {
        "port": 8000,
        "unknown_property": "value",
    }

    result = validator.validate_config(config, check_dependencies=False, check_environment=False)

    # Should have warning for unknown property
    unknown_warnings = [i for i in result.issues if "unknown_property" in i.path]
    assert len(unknown_warnings) > 0


def test_validate_schema_type_mismatch(validator: ConfigurationValidator) -> None:
    """Test schema validation for type mismatches."""
    config = {
        "port": "not_a_number",  # Should be integer
        "debug_mode": "yes",  # Should be boolean
    }

    result = validator.validate_config(config, check_dependencies=False, check_environment=False)

    # Should have errors for type mismatches
    type_errors = [i for i in result.issues if i.severity == ValidationSeverity.ERROR]
    assert len(type_errors) > 0


def test_check_type_method(validator: ConfigurationValidator) -> None:
    """Test _check_type method."""
    # Integer checks
    assert validator._check_type(123, "integer") is True
    assert validator._check_type("123", "integer") is False

    # String checks
    assert validator._check_type("test", "string") is True
    assert validator._check_type(123, "string") is False

    # Boolean checks
    assert validator._check_type(True, "boolean") is True
    assert validator._check_type("true", "boolean") is False

    # Array checks
    assert validator._check_type([1, 2, 3], "array") is True
    assert validator._check_type("not array", "array") is False

    # Object checks
    assert validator._check_type({"key": "value"}, "object") is True
    assert validator._check_type("not object", "object") is False


def test_convert_type_method(validator: ConfigurationValidator) -> None:
    """Test _convert_type method."""
    # String to integer
    assert validator._convert_type("123", "integer") == 123

    # String to boolean
    assert validator._convert_type("true", "boolean") is True
    assert validator._convert_type("false", "boolean") is False
    assert validator._convert_type("1", "boolean") is True
    assert validator._convert_type("0", "boolean") is False

    # Number to string
    assert validator._convert_type(123, "string") == "123"

    # Invalid conversion returns None
    result = validator._convert_type("not_a_number", "integer")
    assert result is None


def test_get_default_value_method(validator: ConfigurationValidator) -> None:
    """Test _get_default_value method."""
    schema = {"properties": {"port": {"type": "integer", "default": 8000}}}

    default = validator._get_default_value(schema, "port")
    assert default == 8000

    # Property without default
    default = validator._get_default_value(schema, "nonexistent")
    assert default is None


def test_health_checks(validator: ConfigurationValidator) -> None:
    """Test health checks method."""
    config = {
        "port": 8000,
        "debug_mode": True,
    }

    health_result = validator.run_health_checks(config)

    assert isinstance(health_result, dict)
    assert "checks" in health_result
    assert "overall_status" in health_result


def test_check_port_availability(validator: ConfigurationValidator) -> None:
    """Test port availability check."""
    config = {
        "port": 8000,
    }

    result = validator._check_port_availability(config)

    assert isinstance(result, dict)
    assert "passed" in result
    assert "details" in result


def test_check_file_paths(validator: ConfigurationValidator, tmp_path: Path) -> None:
    """Test file path checks."""
    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")

    config = {
        "ssl_cert_path": str(test_file),
        "ssl_key_path": str(tmp_path / "nonexistent.key"),
    }

    result = validator._check_file_paths(config)

    assert isinstance(result, dict)
    assert "passed" in result
    assert "details" in result


def test_validate_config_no_schema(temp_schema_dir: Path) -> None:
    """Test validation when schema is not found."""
    validator = ConfigurationValidator(
        schema_dir=temp_schema_dir,
        environment=ConfigEnvironment.TEST,
    )

    config = {"port": 8000}

    result = validator.validate_config(
        config,
        schema_name="nonexistent_schema",
        check_dependencies=False,
        check_environment=False,
    )

    # Should have warning about missing schema
    schema_warnings = [
        i
        for i in result.issues
        if "Schema" in i.message and i.severity == ValidationSeverity.WARNING
    ]
    assert len(schema_warnings) > 0


def test_validation_result_add_issue() -> None:
    """Test ValidationResult add_issue method."""
    result = ValidationResult()

    # Add error issue
    result.add_issue(
        path="test.path",
        severity=ValidationSeverity.ERROR,
        message="Test error",
        suggestion="Fix this",
        auto_fix="fixed_value",
    )

    assert len(result.issues) == 1
    assert not result.valid  # Should be invalid after error
    assert "test.path" in result.auto_fixes
    assert result.auto_fixes["test.path"] == "fixed_value"

    # Add warning issue
    result.add_issue(
        path="test.warning", severity=ValidationSeverity.WARNING, message="Test warning"
    )

    assert len(result.issues) == 2
    # valid should still be False (error already added)


def test_validation_result_to_dict_full() -> None:
    """Test ValidationResult to_dict method."""
    result = ValidationResult()

    result.add_issue(path="error_path", severity=ValidationSeverity.ERROR, message="Error message")

    result.add_issue(
        path="warning_path",
        severity=ValidationSeverity.WARNING,
        message="Warning message",
    )

    result.add_issue(path="info_path", severity=ValidationSeverity.INFO, message="Info message")

    result_dict = result.to_dict()

    assert result_dict["valid"] is False
    assert result_dict["error_count"] == 1
    assert result_dict["warning_count"] == 1
    assert len(result_dict["issues"]) == 3


def test_staging_environment(temp_schema_dir: Path) -> None:
    """Test staging environment validation."""
    validator = ConfigurationValidator(
        schema_dir=temp_schema_dir,
        environment=ConfigEnvironment.STAGING,
    )

    config = {
        "port": 8000,
        "debug_mode": False,
    }

    result = validator.validate_config(config)

    # Staging should have specific requirements
    assert isinstance(result, ValidationResult)


def test_test_environment(temp_schema_dir: Path) -> None:
    """Test test environment validation."""
    validator = ConfigurationValidator(
        schema_dir=temp_schema_dir,
        environment=ConfigEnvironment.TEST,
    )

    config = {
        "port": 8000,
    }

    result = validator.validate_config(config)

    assert isinstance(result, ValidationResult)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
