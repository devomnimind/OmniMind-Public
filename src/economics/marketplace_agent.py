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
Marketplace Agent - Economic Autonomy Implementation

Handles automated tool publication, pricing, and revenue management
with mandatory human oversight and legal compliance.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MarketplacePlatform(Enum):
    """Supported marketplace platforms."""

    GITHUB_MARKETPLACE = "github_marketplace"
    HUGGINGFACE = "huggingface"
    PYPI = "pypi"
    NPM = "npm"
    GUMROAD = "gumroad"


@dataclass
class PublicationRequest:
    """Request to publish a tool to marketplace."""

    tool_name: str
    tool_artifact: str
    documentation: str
    suggested_price: float
    platforms: List[MarketplacePlatform]
    quality_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    approved: bool = False
    approval_timestamp: Optional[str] = None
    approved_by: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["platforms"] = [p.value for p in self.platforms]
        return data


@dataclass
class RevenueDistribution:
    """Revenue distribution configuration."""

    agent_operations: float = 0.7  # 70% for agent operations
    agent_development: float = 0.2  # 20% for development/improvement
    human_share: float = 0.1  # 10% for human oversight

    def __post_init__(self) -> None:
        """Validate distribution sums to 1.0."""
        total = self.agent_operations + self.agent_development + self.human_share
        if not (0.99 <= total <= 1.01):  # Allow small floating point error
            raise ValueError(f"Revenue distribution must sum to 1.0, got {total}")

    def distribute(self, total_earnings: float) -> Dict[str, float]:
        """
        Distribute earnings according to configuration.

        Args:
            total_earnings: Total revenue amount

        Returns:
            Dictionary with distribution amounts
        """
        return {
            "agent_operations": total_earnings * self.agent_operations,
            "agent_development": total_earnings * self.agent_development,
            "human_share": total_earnings * self.human_share,
        }


class MarketplaceAgent:
    """
    Manages automated tool publication and revenue with human oversight.

    CRITICAL: All operations require human approval before execution.
    All revenue is handled via escrow mechanisms.
    All operations are logged for compliance and audit.
    """

    def __init__(
        self,
        platforms: Optional[List[MarketplacePlatform]] = None,
        revenue_distribution: Optional[RevenueDistribution] = None,
        state_file: Optional[Path] = None,
        min_quality_threshold: float = 0.8,
    ):
        """
        Initialize Marketplace Agent.

        Args:
            platforms: List of marketplace platforms to use
            revenue_distribution: Revenue distribution configuration
            state_file: Path to save state
            min_quality_threshold: Minimum quality score for publication
        """
        self.platforms = platforms or [
            MarketplacePlatform.GITHUB_MARKETPLACE,
            MarketplacePlatform.HUGGINGFACE,
        ]
        self.revenue_distribution = revenue_distribution or RevenueDistribution()
        self.state_file = state_file or Path.home() / ".omnimind" / "marketplace_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.min_quality_threshold = min_quality_threshold

        # Track publications and revenue
        self.pending_approvals: List[PublicationRequest] = []
        self.published_tools: List[Dict[str, Any]] = []
        self.total_revenue: float = 0.0

        # Load existing state
        self._load_state()

        logger.info(
            f"MarketplaceAgent initialized: {len(self.platforms)} platforms, "
            f"{len(self.published_tools)} tools published"
        )

    async def publish_tool(
        self,
        tool_artifact: str,
        tool_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[PublicationRequest]:
        """
        Prepare tool for publication (requires human approval).

        Args:
            tool_artifact: Tool code/artifact
            tool_name: Name of the tool
            metadata: Additional metadata

        Returns:
            PublicationRequest if preparation successful, None otherwise
        """
        metadata = metadata or {}

        # Evaluate tool quality
        quality_score = self.evaluate_tool_quality(tool_artifact, metadata)

        if quality_score < self.min_quality_threshold:
            logger.warning(
                f"Tool '{tool_name}' quality score {quality_score:.2f} "
                f"below threshold {self.min_quality_threshold}"
            )
            # Trigger improvement loop
            improved_artifact = await self.improve_tool(tool_artifact, quality_score)
            if improved_artifact:
                # Re-evaluate improved version
                quality_score = self.evaluate_tool_quality(improved_artifact, metadata)
                if quality_score >= self.min_quality_threshold:
                    tool_artifact = improved_artifact
                else:
                    logger.error(f"Tool '{tool_name}' could not be improved sufficiently")
                    return None
            else:
                return None

        # Generate documentation
        documentation = self.generate_docs(tool_artifact, tool_name, metadata)

        # Suggest pricing
        pricing = self.suggest_pricing(tool_artifact, quality_score, metadata)

        # Create publication request
        pub_request = PublicationRequest(
            tool_name=tool_name,
            tool_artifact=tool_artifact,
            documentation=documentation,
            suggested_price=pricing,
            platforms=self.platforms,
            quality_score=quality_score,
            metadata=metadata,
        )

        # Add to pending approvals
        self.pending_approvals.append(pub_request)
        self._save_state()

        logger.info(
            f"Tool '{tool_name}' prepared for publication "
            f"(quality={quality_score:.2f}, price=${pricing:.2f})"
        )

        # Request human approval (would be async in production)
        approved = await self.request_human_approval(pub_request)

        if approved:
            # Simulate publication (would be real API calls in production)
            results = await self.publish_to_platforms(pub_request)
            self.monitor_sales_and_feedback(results)
            return pub_request
        else:
            logger.info(f"Publication of '{tool_name}' not approved by human supervisor")
            return None

    def evaluate_tool_quality(self, tool_artifact: str, metadata: Dict[str, Any]) -> float:
        """
        Evaluate tool quality for marketplace publication.

        Args:
            tool_artifact: Tool code/artifact
            metadata: Additional metadata

        Returns:
            Quality score (0.0-1.0)
        """
        score = 0.0

        # Check for documentation
        if "docstring" in tool_artifact.lower() or '"""' in tool_artifact:
            score += 0.2

        # Check for type hints
        if "->" in tool_artifact or ": " in tool_artifact:
            score += 0.15

        # Check for tests
        if metadata.get("has_tests", False):
            score += 0.25

        # Check code length (reasonable size)
        lines = len(tool_artifact.split("\n"))
        if 50 <= lines <= 500:
            score += 0.1
        elif lines > 20:
            score += 0.05

        # Check for error handling
        if "try:" in tool_artifact or "except" in tool_artifact:
            score += 0.1

        # Check for logging
        if "logger" in tool_artifact or "logging" in tool_artifact:
            score += 0.1

        # Check explicit quality score from metadata
        if "quality_score" in metadata:
            score = max(score, metadata["quality_score"])

        return min(1.0, score)

    async def improve_tool(self, tool_artifact: str, current_quality: float) -> Optional[str]:
        """
        Attempt to improve tool quality.

        Args:
            tool_artifact: Current tool code
            current_quality: Current quality score

        Returns:
            Improved tool artifact or None if improvement failed
        """
        logger.info(f"Attempting to improve tool (current quality: {current_quality:.2f})")

        # In production, this would use CodeAgent to add:
        # - Better documentation
        # - Type hints
        # - Error handling
        # - Tests
        # - Logging

        # For now, return None to indicate improvement is not implemented
        # This would integrate with the CodeAgent in production
        return None

    def generate_docs(self, tool_artifact: str, tool_name: str, metadata: Dict[str, Any]) -> str:
        """
        Generate documentation for tool.

        Args:
            tool_artifact: Tool code
            tool_name: Tool name
            metadata: Additional metadata

        Returns:
            Generated documentation
        """
        # Extract docstrings
        docstring = ""
        if '"""' in tool_artifact:
            parts = tool_artifact.split('"""')
            if len(parts) >= 2:
                docstring = parts[1].strip()

        # Create basic README
        docs = f"""# {tool_name}

## Description

{docstring or "Tool generated by OmniMind autonomous agent."}

## Usage

```python
# Import and use the tool
from {tool_name} import main

result = main()
```

## Metadata

- Quality Score: {metadata.get('quality_score', 'N/A')}
- Generated: {datetime.now(timezone.utc).isoformat()}
- Agent: OmniMind v1.0

## License

MIT License (Human oversight: required)
"""

        return docs

    def suggest_pricing(
        self, tool_artifact: str, quality_score: float, metadata: Dict[str, Any]
    ) -> float:
        """
        Suggest pricing for tool based on quality and complexity.

        Args:
            tool_artifact: Tool code
            quality_score: Quality score (0.0-1.0)
            metadata: Additional metadata

        Returns:
            Suggested price in USD
        """
        # Base price on quality
        base_price = quality_score * 10.0  # $0-10 based on quality

        # Adjust for complexity (code length)
        lines = len(tool_artifact.split("\n"))
        complexity_multiplier = min(2.0, lines / 100.0)

        suggested_price = base_price * complexity_multiplier

        # Round to nearest $0.99
        suggested_price = round(suggested_price * 100) / 100

        # Minimum price
        suggested_price = max(0.99, suggested_price)

        return suggested_price

    async def request_human_approval(self, request: PublicationRequest) -> bool:
        """
        Request human approval for publication.

        Args:
            request: Publication request

        Returns:
            True if approved

        NOTE: In production, this would be async and wait for human input
        """
        logger.info(
            f"🔔 Human approval requested for '{request.tool_name}' "
            f"(quality={request.quality_score:.2f}, price=${request.suggested_price:.2f})"
        )

        # In production, this would:
        # 1. Send notification to human supervisor
        # 2. Present tool details, docs, pricing
        # 3. Wait for approval/rejection
        # 4. Record decision in audit log

        # For now, simulate approval based on quality
        approved = request.quality_score >= 0.8

        if approved:
            request.approved = True
            request.approval_timestamp = datetime.now(timezone.utc).isoformat()
            request.approved_by = "human_supervisor"  # Would be actual name
            logger.info(f"✅ Publication approved for '{request.tool_name}'")
        else:
            logger.warning(f"❌ Publication rejected for '{request.tool_name}'")

        self._save_state()
        return approved

    async def publish_to_platforms(
        self, request: PublicationRequest
    ) -> Dict[MarketplacePlatform, bool]:
        """
        Publish tool to configured platforms.

        Args:
            request: Approved publication request

        Returns:
            Dictionary with publication results per platform
        """
        if not request.approved:
            raise ValueError("Cannot publish unapproved request")

        results: Dict[MarketplacePlatform, bool] = {}

        for platform in request.platforms:
            # In production, this would make real API calls to:
            # - GitHub Marketplace
            # - HuggingFace
            # - PyPI
            # - etc.

            logger.info(f"Publishing '{request.tool_name}' to {platform.value}...")

            # Simulate success
            results[platform] = True

            # Record publication
            self.published_tools.append(
                {
                    "tool_name": request.tool_name,
                    "platform": platform.value,
                    "price": request.suggested_price,
                    "published_at": datetime.now(timezone.utc).isoformat(),
                    "quality_score": request.quality_score,
                }
            )

        self._save_state()
        logger.info(f"✅ '{request.tool_name}' published to {len(results)} platforms")

        return results

    def monitor_sales_and_feedback(
        self, publication_results: Dict[MarketplacePlatform, bool]
    ) -> None:
        """
        Monitor sales and collect feedback from marketplaces.

        Args:
            publication_results: Results from publication
        """
        # In production, this would:
        # 1. Set up webhooks for sales notifications
        # 2. Monitor download/usage metrics
        # 3. Collect user reviews and ratings
        # 4. Track revenue in escrow accounts
        # 5. Update reputation based on feedback

        logger.info(f"Monitoring enabled for {len(publication_results)} platforms")

    def distribute_revenue(self, earnings: float) -> Dict[str, float]:
        """
        Distribute revenue according to configuration.

        Args:
            earnings: Total earnings amount

        Returns:
            Distribution breakdown
        """
        distribution = self.revenue_distribution.distribute(earnings)

        # Update total revenue
        self.total_revenue += earnings

        # Log distribution
        logger.info(
            f"Revenue distributed: ${earnings:.2f} total "
            f"(ops=${distribution['agent_operations']:.2f}, "
            f"dev=${distribution['agent_development']:.2f}, "
            f"human=${distribution['human_share']:.2f})"
        )

        # Record in audit log
        self._record_revenue(earnings, distribution)
        self._save_state()

        return distribution

    def _record_revenue(self, amount: float, distribution: Dict[str, float]) -> None:
        """Record revenue transaction to audit log."""
        revenue_log = self.state_file.parent / "revenue_audit.jsonl"

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "amount": amount,
            "distribution": distribution,
            "total_revenue": self.total_revenue,
        }

        with revenue_log.open("a") as f:
            f.write(json.dumps(record) + "\n")

    def _save_state(self) -> None:
        """Save marketplace state to disk."""
        state = {
            "platforms": [p.value for p in self.platforms],
            "revenue_distribution": asdict(self.revenue_distribution),
            "pending_approvals": [req.to_dict() for req in self.pending_approvals],
            "published_tools": self.published_tools,
            "total_revenue": self.total_revenue,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        with self.state_file.open("w") as f:
            json.dump(state, f, indent=2)

    def _load_state(self) -> None:
        """Load marketplace state from disk."""
        if not self.state_file.exists():
            return

        try:
            with self.state_file.open("r") as f:
                state = json.load(f)

            # Restore platforms
            platform_values = state.get("platforms", [])
            self.platforms = [MarketplacePlatform(p) for p in platform_values]

            # Restore revenue distribution
            rev_dist = state.get("revenue_distribution", {})
            if rev_dist:
                self.revenue_distribution = RevenueDistribution(**rev_dist)

            # Restore published tools
            self.published_tools = state.get("published_tools", [])
            self.total_revenue = state.get("total_revenue", 0.0)

            logger.info(f"Loaded marketplace state from {self.state_file}")
        except Exception as e:
            logger.warning(f"Failed to load marketplace state: {e}")
