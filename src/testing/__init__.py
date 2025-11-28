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

"""Testing utilities for OmniMind."""

from .chaos_engineering import (
    ChaosExperiment,
    ChaosMonkey,
    FailureType,
    chaos_aware,
    chaos_monkey,
    create_api_timeout_experiment,
    create_database_latency_experiment,
    create_llm_failure_experiment,
    create_memory_exhaustion_experiment,
    enable_chaos,
    inject_chaos,
    register_default_experiments,
)

__all__ = [
    "ChaosExperiment",
    "ChaosMonkey",
    "FailureType",
    "chaos_aware",
    "chaos_monkey",
    "create_api_timeout_experiment",
    "create_database_latency_experiment",
    "create_llm_failure_experiment",
    "create_memory_exhaustion_experiment",
    "enable_chaos",
    "inject_chaos",
    "register_default_experiments",
]
