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
Testes para Economics - Marketplace Agent.

Group 13: System Services - economics/
"""

import tempfile
from pathlib import Path

import pytest

from src.economics.marketplace_agent import (
    MarketplaceAgent,
    MarketplacePlatform,
    PublicationRequest,
    RevenueDistribution,
)


class TestRevenueDistribution:
    """Testa RevenueDistribution configuration."""

    def test_initialization_default(self) -> None:
        """Testa inicialização com valores padrão."""
        dist = RevenueDistribution()

        assert dist.agent_operations == 0.7
        assert dist.agent_development == 0.2
        assert dist.human_share == 0.1

    def test_initialization_custom(self) -> None:
        """Testa inicialização com valores customizados."""
        dist = RevenueDistribution(
            agent_operations=0.6,
            agent_development=0.3,
            human_share=0.1,
        )

        assert dist.agent_operations == 0.6
        assert dist.agent_development == 0.3
        assert dist.human_share == 0.1

    def test_validation_sum_to_one(self) -> None:
        """Testa que distribuição deve somar 1.0."""
        # Valores que somam 1.0 devem funcionar
        dist = RevenueDistribution(
            agent_operations=0.5,
            agent_development=0.3,
            human_share=0.2,
        )
        assert dist is not None

        # Valores que não somam 1.0 devem falhar
        with pytest.raises(ValueError):
            RevenueDistribution(
                agent_operations=0.5,
                agent_development=0.3,
                human_share=0.3,  # Soma = 1.1
            )

    def test_distribute_revenue(self) -> None:
        """Testa distribuição de receita."""
        dist = RevenueDistribution()
        total_earnings = 100.0

        distribution = dist.distribute(total_earnings)

        assert isinstance(distribution, dict)
        assert "agent_operations" in distribution
        assert "agent_development" in distribution
        assert "human_share" in distribution

        # Valores devem somar o total (com tolerância para float)
        total_distributed = sum(distribution.values())
        assert abs(total_distributed - total_earnings) < 0.01

    def test_distribute_various_amounts(self) -> None:
        """Testa distribuição com vários valores."""
        dist = RevenueDistribution()

        for amount in [10.0, 100.0, 1000.0, 0.99]:
            distribution = dist.distribute(amount)
            total_distributed = sum(distribution.values())
            assert abs(total_distributed - amount) < 0.01


class TestPublicationRequest:
    """Testa PublicationRequest dataclass."""

    def test_initialization(self) -> None:
        """Testa inicialização de PublicationRequest."""
        req = PublicationRequest(
            tool_name="test_tool",
            tool_artifact="def test(): pass",
            documentation="# Test Tool",
            suggested_price=9.99,
            platforms=[MarketplacePlatform.GITHUB_MARKETPLACE],
            quality_score=0.85,
        )

        assert req.tool_name == "test_tool"
        assert req.tool_artifact == "def test(): pass"
        assert req.documentation == "# Test Tool"
        assert req.suggested_price == 9.99
        assert req.quality_score == 0.85
        assert req.approved is False
        assert req.approval_timestamp is None

    def test_to_dict(self) -> None:
        """Testa conversão para dicionário."""
        req = PublicationRequest(
            tool_name="test_tool",
            tool_artifact="code",
            documentation="docs",
            suggested_price=5.0,
            platforms=[
                MarketplacePlatform.GITHUB_MARKETPLACE,
                MarketplacePlatform.PYPI,
            ],
            quality_score=0.9,
            metadata={"key": "value"},
        )

        req_dict = req.to_dict()

        assert isinstance(req_dict, dict)
        assert req_dict["tool_name"] == "test_tool"
        assert req_dict["quality_score"] == 0.9
        assert "github_marketplace" in req_dict["platforms"]
        assert "pypi" in req_dict["platforms"]
        assert req_dict["metadata"]["key"] == "value"


class TestMarketplaceAgent:
    """Testa MarketplaceAgent para publicação automatizada."""

    @pytest.fixture
    def temp_state_file(self) -> Path:
        """Cria arquivo temporário para estado."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir / "marketplace_state.json"
        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_initialization_default(self, temp_state_file: Path) -> None:
        """Testa inicialização com valores padrão."""
        agent = MarketplaceAgent(state_file=temp_state_file)

        assert agent is not None
        assert len(agent.platforms) > 0
        assert agent.revenue_distribution is not None
        assert agent.min_quality_threshold == 0.8
        assert len(agent.pending_approvals) == 0
        assert len(agent.published_tools) == 0
        assert agent.total_revenue == 0.0

    def test_initialization_custom(self, temp_state_file: Path) -> None:
        """Testa inicialização com valores customizados."""
        agent = MarketplaceAgent(
            platforms=[MarketplacePlatform.PYPI],
            revenue_distribution=RevenueDistribution(
                agent_operations=0.6,
                agent_development=0.3,
                human_share=0.1,
            ),
            state_file=temp_state_file,
            min_quality_threshold=0.9,
        )

        assert agent.platforms == [MarketplacePlatform.PYPI]
        assert agent.revenue_distribution.agent_operations == 0.6
        assert agent.min_quality_threshold == 0.9

    def test_evaluate_tool_quality_high(self, temp_state_file: Path) -> None:
        """Testa avaliação de ferramenta de alta qualidade."""
        agent = MarketplaceAgent(state_file=temp_state_file)

        # Tool com boa qualidade
        tool_artifact = '''"""
        High quality tool with documentation.
        """

        def process_data(data: list[str]) -> dict[str, int]:
            """Process data and return statistics."""
            try:
                import logging
                logger = logging.getLogger(__name__)
                logger.info("Processing data")
                return {"count": len(data)}
            except Exception as e:
                logger.error(f"Error: {e}")
                return {}
        '''

        metadata = {"has_tests": True, "quality_score": 0.9}
        quality = agent.evaluate_tool_quality(tool_artifact, metadata)

        assert quality >= 0.8

    def test_evaluate_tool_quality_low(self, temp_state_file: Path) -> None:
        """Testa avaliação de ferramenta de baixa qualidade."""
        agent = MarketplaceAgent(state_file=temp_state_file)

        # Tool simples sem documentação
        tool_artifact = "def test(): pass"
        metadata = {}
        quality = agent.evaluate_tool_quality(tool_artifact, metadata)

        assert quality < 0.5

    def test_generate_docs(self, temp_state_file: Path) -> None:
        """Testa geração de documentação."""
        agent = MarketplaceAgent(state_file=temp_state_file)

        tool_artifact = '''"""
        Test tool for demonstration.
        """
        def main():
            print("Hello")
        '''

        docs = agent.generate_docs(
            tool_artifact=tool_artifact,
            tool_name="test_tool",
            metadata={"quality_score": 0.85},
        )

        assert isinstance(docs, str)
        assert "test_tool" in docs
        assert "Test tool for demonstration" in docs
        assert "Usage" in docs
        assert "License" in docs

    def test_suggest_pricing_basic(self, temp_state_file: Path) -> None:
        """Testa sugestão de preço básica."""
        agent = MarketplaceAgent(state_file=temp_state_file)

        tool_artifact = "def test(): pass\n" * 50  # 50 linhas
        quality_score = 0.8
        metadata = {}

        price = agent.suggest_pricing(tool_artifact, quality_score, metadata)

        assert isinstance(price, float)
        assert price >= 0.99  # Preço mínimo
        assert price > 0

    def test_suggest_pricing_high_quality(self, temp_state_file: Path) -> None:
        """Testa que maior qualidade resulta em preço maior."""
        agent = MarketplaceAgent(state_file=temp_state_file)

        tool_artifact = "def test(): pass\n" * 100  # Complexidade média

        price_low = agent.suggest_pricing(tool_artifact, 0.3, {})
        price_high = agent.suggest_pricing(tool_artifact, 0.9, {})

        assert price_high > price_low

    def test_suggest_pricing_complexity(self, temp_state_file: Path) -> None:
        """Testa que maior complexidade resulta em preço maior."""
        agent = MarketplaceAgent(state_file=temp_state_file)

        quality_score = 0.8

        simple_tool = "def test(): pass\n" * 20
        complex_tool = "def test(): pass\n" * 200

        price_simple = agent.suggest_pricing(simple_tool, quality_score, {})
        price_complex = agent.suggest_pricing(complex_tool, quality_score, {})

        assert price_complex >= price_simple

    @pytest.mark.asyncio
    async def test_request_human_approval_high_quality(self, temp_state_file: Path) -> None:
        """Testa aprovação automática para alta qualidade."""
        agent = MarketplaceAgent(state_file=temp_state_file)

        req = PublicationRequest(
            tool_name="quality_tool",
            tool_artifact="code",
            documentation="docs",
            suggested_price=9.99,
            platforms=[MarketplacePlatform.GITHUB_MARKETPLACE],
            quality_score=0.9,  # Alta qualidade
        )

        approved = await agent.request_human_approval(req)

        assert approved is True
        assert req.approved is True
        assert req.approval_timestamp is not None
        assert req.approved_by is not None

    @pytest.mark.asyncio
    async def test_request_human_approval_low_quality(self, temp_state_file: Path) -> None:
        """Testa rejeição para baixa qualidade."""
        agent = MarketplaceAgent(state_file=temp_state_file)

        req = PublicationRequest(
            tool_name="low_quality_tool",
            tool_artifact="code",
            documentation="docs",
            suggested_price=1.99,
            platforms=[MarketplacePlatform.GITHUB_MARKETPLACE],
            quality_score=0.5,  # Baixa qualidade
        )

        approved = await agent.request_human_approval(req)

        assert approved is False

    @pytest.mark.asyncio
    async def test_publish_to_platforms_success(self, temp_state_file: Path) -> None:
        """Testa publicação para plataformas."""
        agent = MarketplaceAgent(state_file=temp_state_file)

        req = PublicationRequest(
            tool_name="test_tool",
            tool_artifact="code",
            documentation="docs",
            suggested_price=9.99,
            platforms=[
                MarketplacePlatform.GITHUB_MARKETPLACE,
                MarketplacePlatform.PYPI,
            ],
            quality_score=0.9,
            approved=True,
        )

        results = await agent.publish_to_platforms(req)

        assert isinstance(results, dict)
        assert len(results) == 2
        assert MarketplacePlatform.GITHUB_MARKETPLACE in results
        assert MarketplacePlatform.PYPI in results
        assert all(results.values())  # Todos devem ser True
        assert len(agent.published_tools) == 2

    @pytest.mark.asyncio
    async def test_publish_to_platforms_not_approved(self, temp_state_file: Path) -> None:
        """Testa que não pode publicar sem aprovação."""
        agent = MarketplaceAgent(state_file=temp_state_file)

        req = PublicationRequest(
            tool_name="test_tool",
            tool_artifact="code",
            documentation="docs",
            suggested_price=9.99,
            platforms=[MarketplacePlatform.GITHUB_MARKETPLACE],
            quality_score=0.9,
            approved=False,  # Não aprovado
        )

        with pytest.raises(ValueError):
            await agent.publish_to_platforms(req)

    @pytest.mark.asyncio
    async def test_publish_tool_high_quality(self, temp_state_file: Path) -> None:
        """Testa publicação completa de ferramenta de alta qualidade."""
        agent = MarketplaceAgent(state_file=temp_state_file)

        tool_artifact = '''"""
        High quality tool.
        """
        def process(data: list) -> dict:
            """Process data."""
            try:
                import logging
                logger = logging.getLogger(__name__)
                return {"result": data}
            except Exception as e:
                return {}
        '''

        result = await agent.publish_tool(
            tool_artifact=tool_artifact,
            tool_name="quality_tool",
            metadata={"has_tests": True, "quality_score": 0.85},  # Explicit high score
        )

        assert result is not None
        assert result.approved is True
        assert len(agent.published_tools) > 0

    @pytest.mark.asyncio
    async def test_publish_tool_low_quality_no_improvement(self, temp_state_file: Path) -> None:
        """Testa que ferramenta de baixa qualidade sem melhoria é rejeitada."""
        agent = MarketplaceAgent(state_file=temp_state_file)

        tool_artifact = "def test(): pass"  # Muito simples

        result = await agent.publish_tool(
            tool_artifact=tool_artifact,
            tool_name="simple_tool",
            metadata={},
        )

        # Deve retornar None porque não pode melhorar
        assert result is None
        assert len(agent.published_tools) == 0

    def test_state_persistence(self, temp_state_file: Path) -> None:
        """Testa persistência de estado."""
        # Criar agent e adicionar dados
        agent1 = MarketplaceAgent(state_file=temp_state_file)
        agent1.published_tools.append(
            {
                "tool_name": "test",
                "platform": "github",
                "price": 9.99,
            }
        )
        agent1.total_revenue = 100.0
        agent1._save_state()

        # Criar novo agent com mesmo state_file
        agent2 = MarketplaceAgent(state_file=temp_state_file)

        # Estado deve ser restaurado
        assert agent2.total_revenue == 100.0
        assert len(agent2.published_tools) == 1
        assert agent2.published_tools[0]["tool_name"] == "test"
