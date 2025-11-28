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

import pytest

from src.security.dlp import DLPValidator, DLPViolation, DLPViolationError


def test_dlp_blocks_secrets() -> None:
    validator: DLPValidator = DLPValidator()
    with pytest.raises(DLPViolationError) as exc_info:
        validator.enforce("api_key=ABCDEF1234567890")
    violation: DLPViolation = exc_info.value.violation
    assert violation.rule == "credentials"
    assert violation.action == "block"
    assert "api_key" in violation.snippet


def test_dlp_alerts_internal_network() -> None:
    validator: DLPValidator = DLPValidator()
    violation = validator.validate("O endereço interno é 192.168.1.10")
    assert violation is not None
    assert violation.rule == "internal_network"
    assert violation.action == "alert"
