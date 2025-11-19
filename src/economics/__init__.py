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
