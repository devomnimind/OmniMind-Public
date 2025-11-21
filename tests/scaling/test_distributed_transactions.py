"""Tests for distributed transactions coordination."""

import asyncio
import pytest

from src.scaling.distributed_transactions import (
    DistributedTransaction,
    ParticipantState,
    SagaCoordinator,
    SagaStep,
    TransactionParticipant,
    TransactionPhase,
    TwoPhaseCommitCoordinator,
)


class TestTransactionParticipant:
    """Tests for TransactionParticipant."""

    def test_initialization(self):
        """Test participant initialization."""
        participant = TransactionParticipant(
            participant_id="p1",
            node_id="node-1",
        )

        assert participant.participant_id == "p1"
        assert participant.node_id == "node-1"
        assert participant.state == ParticipantState.IDLE

    def test_to_dict(self):
        """Test participant serialization."""
        participant = TransactionParticipant(
            participant_id="p1",
            node_id="node-1",
        )

        participant_dict = participant.to_dict()

        assert "participant_id" in participant_dict
        assert "node_id" in participant_dict
        assert "state" in participant_dict


class TestDistributedTransaction:
    """Tests for DistributedTransaction."""

    def test_initialization(self):
        """Test transaction initialization."""
        transaction = DistributedTransaction(transaction_id="tx-1")

        assert transaction.transaction_id == "tx-1"
        assert transaction.phase == TransactionPhase.PREPARING
        assert len(transaction.participants) == 0

    def test_add_participant(self):
        """Test adding participants."""
        transaction = DistributedTransaction(transaction_id="tx-1")

        p1 = TransactionParticipant("p1", "node-1")
        p2 = TransactionParticipant("p2", "node-2")

        transaction.add_participant(p1)
        transaction.add_participant(p2)

        assert len(transaction.participants) == 2
        assert "p1" in transaction.participants

    def test_all_prepared(self):
        """Test checking if all participants are prepared."""
        transaction = DistributedTransaction(transaction_id="tx-1")

        p1 = TransactionParticipant("p1", "node-1")
        p2 = TransactionParticipant("p2", "node-2")

        p1.state = ParticipantState.PREPARED
        p2.state = ParticipantState.PREPARED

        transaction.add_participant(p1)
        transaction.add_participant(p2)

        assert transaction.all_prepared()

    def test_not_all_prepared(self):
        """Test when not all participants are prepared."""
        transaction = DistributedTransaction(transaction_id="tx-1")

        p1 = TransactionParticipant("p1", "node-1")
        p2 = TransactionParticipant("p2", "node-2")

        p1.state = ParticipantState.PREPARED
        p2.state = ParticipantState.PREPARING

        transaction.add_participant(p1)
        transaction.add_participant(p2)

        assert not transaction.all_prepared()

    def test_any_failed(self):
        """Test checking for failed participants."""
        transaction = DistributedTransaction(transaction_id="tx-1")

        p1 = TransactionParticipant("p1", "node-1")
        p2 = TransactionParticipant("p2", "node-2")

        p1.state = ParticipantState.PREPARED
        p2.state = ParticipantState.FAILED

        transaction.add_participant(p1)
        transaction.add_participant(p2)

        assert transaction.any_failed()


@pytest.mark.asyncio
class TestTwoPhaseCommitCoordinator:
    """Tests for TwoPhaseCommitCoordinator."""

    async def test_initialization(self):
        """Test coordinator initialization."""
        coordinator = TwoPhaseCommitCoordinator()

        assert len(coordinator._transactions) == 0

    async def test_begin_transaction(self):
        """Test beginning a transaction."""
        coordinator = TwoPhaseCommitCoordinator()

        transaction = await coordinator.begin_transaction(
            participant_nodes=["node-1", "node-2"],
            data={"key": "value"},
        )

        assert transaction.transaction_id is not None
        assert len(transaction.participants) == 2
        assert transaction.data["key"] == "value"

    async def test_execute_successful_transaction(self):
        """Test successful transaction execution."""
        coordinator = TwoPhaseCommitCoordinator()

        # Register mock handlers
        async def prepare_handler(tx_id: str, data: dict) -> bool:
            await asyncio.sleep(0.01)
            return True

        async def commit_handler(tx_id: str) -> bool:
            await asyncio.sleep(0.01)
            return True

        async def abort_handler(tx_id: str) -> None:
            await asyncio.sleep(0.01)

        coordinator.register_node_handlers(
            "node-1",
            prepare_handler,
            commit_handler,
            abort_handler,
        )

        coordinator.register_node_handlers(
            "node-2",
            prepare_handler,
            commit_handler,
            abort_handler,
        )

        # Begin and execute transaction
        transaction = await coordinator.begin_transaction(["node-1", "node-2"])
        success = await coordinator.execute_transaction(transaction.transaction_id)

        assert success
        assert transaction.phase == TransactionPhase.COMMITTED

    async def test_execute_failed_transaction(self):
        """Test failed transaction execution."""
        coordinator = TwoPhaseCommitCoordinator()

        # Register mock handlers (one fails)
        async def prepare_success(tx_id: str, data: dict) -> bool:
            await asyncio.sleep(0.01)
            return True

        async def prepare_fail(tx_id: str, data: dict) -> bool:
            await asyncio.sleep(0.01)
            return False

        async def commit_handler(tx_id: str) -> bool:
            await asyncio.sleep(0.01)
            return True

        async def abort_handler(tx_id: str) -> None:
            await asyncio.sleep(0.01)

        coordinator.register_node_handlers(
            "node-1",
            prepare_success,
            commit_handler,
            abort_handler,
        )

        coordinator.register_node_handlers(
            "node-2",
            prepare_fail,  # This will fail
            commit_handler,
            abort_handler,
        )

        # Begin and execute transaction
        transaction = await coordinator.begin_transaction(["node-1", "node-2"])
        success = await coordinator.execute_transaction(transaction.transaction_id)

        assert not success
        assert transaction.phase == TransactionPhase.ABORTED

    async def test_get_transaction(self):
        """Test getting transaction by ID."""
        coordinator = TwoPhaseCommitCoordinator()

        transaction = await coordinator.begin_transaction(["node-1"])
        tx_id = transaction.transaction_id

        retrieved = coordinator.get_transaction(tx_id)

        assert retrieved is not None
        assert retrieved.transaction_id == tx_id

    async def test_get_active_transactions(self):
        """Test getting active transactions."""
        coordinator = TwoPhaseCommitCoordinator()

        tx1 = await coordinator.begin_transaction(["node-1"])
        tx2 = await coordinator.begin_transaction(["node-2"])

        active = coordinator.get_active_transactions()

        assert len(active) == 2


@pytest.mark.asyncio
class TestSagaCoordinator:
    """Tests for SagaCoordinator."""

    async def test_initialization(self):
        """Test saga coordinator initialization."""
        coordinator = SagaCoordinator()

        assert len(coordinator._sagas) == 0

    async def test_create_saga(self):
        """Test creating a saga."""
        coordinator = SagaCoordinator()

        async def step1_action(data: dict) -> dict:
            return {"step1": "done"}

        async def step1_compensation(data: dict) -> None:
            pass

        async def step2_action(data: dict) -> dict:
            return {"step2": "done"}

        async def step2_compensation(data: dict) -> None:
            pass

        steps = [
            (step1_action, step1_compensation),
            (step2_action, step2_compensation),
        ]

        coordinator.create_saga("saga-1", steps)

        assert "saga-1" in coordinator._sagas
        assert len(coordinator._sagas["saga-1"]) == 2

    async def test_execute_successful_saga(self):
        """Test successful saga execution."""
        coordinator = SagaCoordinator()

        results = []

        async def step1_action(data: dict) -> dict:
            results.append("step1")
            return {"step1": "done"}

        async def step1_compensation(data: dict) -> None:
            results.append("compensate1")

        async def step2_action(data: dict) -> dict:
            results.append("step2")
            return {"step2": "done"}

        async def step2_compensation(data: dict) -> None:
            results.append("compensate2")

        steps = [
            (step1_action, step1_compensation),
            (step2_action, step2_compensation),
        ]

        coordinator.create_saga("saga-1", steps)
        success = await coordinator.execute_saga("saga-1")

        assert success
        assert "step1" in results
        assert "step2" in results
        assert "compensate1" not in results  # No compensation needed

    async def test_execute_failed_saga_with_compensation(self):
        """Test failed saga with compensation."""
        coordinator = SagaCoordinator()

        results = []

        async def step1_action(data: dict) -> dict:
            results.append("step1")
            return {"step1": "done"}

        async def step1_compensation(data: dict) -> None:
            results.append("compensate1")

        async def step2_action(data: dict) -> dict:
            results.append("step2")
            raise Exception("Step 2 failed!")

        async def step2_compensation(data: dict) -> None:
            results.append("compensate2")

        steps = [
            (step1_action, step1_compensation),
            (step2_action, step2_compensation),
        ]

        coordinator.create_saga("saga-1", steps)
        success = await coordinator.execute_saga("saga-1")

        assert not success
        assert "step1" in results
        assert "step2" in results
        assert "compensate1" in results  # Step 1 should be compensated

    async def test_get_saga_status(self):
        """Test getting saga status."""
        coordinator = SagaCoordinator()

        async def step1_action(data: dict) -> dict:
            return {}

        async def step1_compensation(data: dict) -> None:
            pass

        steps = [(step1_action, step1_compensation)]

        coordinator.create_saga("saga-1", steps)
        status = coordinator.get_saga_status("saga-1")

        assert status["saga_id"] == "saga-1"
        assert status["total_steps"] == 1
        assert "steps" in status

    async def test_saga_not_found(self):
        """Test getting status of non-existent saga."""
        coordinator = SagaCoordinator()

        status = coordinator.get_saga_status("non-existent")

        assert "error" in status


class TestSagaStep:
    """Tests for SagaStep."""

    def test_initialization(self):
        """Test saga step initialization."""
        async def action(data: dict) -> dict:
            return {}

        async def compensation(data: dict) -> None:
            pass

        step = SagaStep(
            step_id="step-1",
            action=action,
            compensation=compensation,
        )

        assert step.step_id == "step-1"
        assert not step.completed
        assert not step.compensated
