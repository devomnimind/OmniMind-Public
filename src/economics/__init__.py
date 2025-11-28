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
Economic Autonomy and Marketplace Module

Implements legal economic automation for autonomous agents, including:
- Tool publication to marketplaces
- Revenue management with escrow
- Human approval workflows
- Compliance and legal framework
"""

from .marketplace_agent import (
    MarketplaceAgent,
    MarketplacePlatform,
    PublicationRequest,
    RevenueDistribution,
)

__all__ = [
    "MarketplaceAgent",
    "MarketplacePlatform",
    "PublicationRequest",
    "RevenueDistribution",
]
