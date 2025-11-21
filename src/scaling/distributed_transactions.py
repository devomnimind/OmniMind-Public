"""Distributed transaction coordination with two-phase commit and saga pattern.

This module implements distributed transaction consistency:
- Two-phase commit protocol (2PC)
- Saga pattern for long-running transactions
- Transaction coordinator
- Participant management
- Compensation handlers for rollback
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class TransactionPhase(str, Enum):
    """Transaction phases."""

    PREPARING = "preparing"
    PREPARED = "prepared"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ABORTING = "aborting"
    ABORTED = "aborted"


class ParticipantState(str, Enum):
    """Participant states in transaction."""

    IDLE = "idle"
    PREPARING = "preparing"
    PREPARED = "prepared"
    COMMITTED = "committed"
    ABORTED = "aborted"
    FAILED = "failed"


@dataclass
class TransactionParticipant:
    """Represents a participant in a distributed transaction."""

    participant_id: str
    node_id: str
    state: ParticipantState = ParticipantState.IDLE
    prepare_timestamp: Optional[datetime] = None
    commit_timestamp: Optional[datetime] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "participant_id": self.participant_id,
            "node_id": self.node_id,
            "state": self.state.value,
            "prepare_timestamp": self.prepare_timestamp.isoformat() if self.prepare_timestamp else None,
            "commit_timestamp": self.commit_timestamp.isoformat() if self.commit_timestamp else None,
            "error": self.error,
        }


@dataclass
class DistributedTransaction:
    """Represents a distributed transaction."""

    transaction_id: str
    phase: TransactionPhase = TransactionPhase.PREPARING
    participants: Dict[str, TransactionParticipant] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    timeout: timedelta = field(default_factory=lambda: timedelta(seconds=30))
    data: Dict[str, Any] = field(default_factory=dict)

    def add_participant(self, participant: TransactionParticipant) -> None:
        """Add a participant to the transaction."""
        self.participants[participant.participant_id] = participant

    def all_prepared(self) -> bool:
        """Check if all participants are prepared."""
        return all(
            p.state == ParticipantState.PREPARED
            for p in self.participants.values()
        )

    def any_failed(self) -> bool:
        """Check if any participant failed."""
        return any(
            p.state == ParticipantState.FAILED
            for p in self.participants.values()
        )

    def is_expired(self) -> bool:
        """Check if transaction has expired."""
        return datetime.now() - self.started_at > self.timeout

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "transaction_id": self.transaction_id,
            "phase": self.phase.value,
            "participants": {
                pid: p.to_dict() for pid, p in self.participants.items()
            },
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "timeout_seconds": self.timeout.total_seconds(),
            "data": self.data,
        }


class TwoPhaseCommitCoordinator:
    """Coordinator for two-phase commit protocol."""

    def __init__(self) -> None:
        """Initialize coordinator."""
        self._transactions: Dict[str, DistributedTransaction] = {}
        self._prepare_handlers: Dict[str, Callable] = {}
        self._commit_handlers: Dict[str, Callable] = {}
        self._abort_handlers: Dict[str, Callable] = {}

    def register_node_handlers(
        self,
        node_id: str,
        prepare_handler: Callable[[str, Dict[str, Any]], bool],
        commit_handler: Callable[[str], bool],
        abort_handler: Callable[[str], None],
    ) -> None:
        """Register handlers for a node.

        Args:
            node_id: Node identifier
            prepare_handler: Async function for prepare phase
            commit_handler: Async function for commit phase
            abort_handler: Async function for abort
        """
        self._prepare_handlers[node_id] = prepare_handler
        self._commit_handlers[node_id] = commit_handler
        self._abort_handlers[node_id] = abort_handler
        logger.info(f"Registered handlers for node {node_id}")

    async def begin_transaction(
        self,
        participant_nodes: List[str],
        data: Optional[Dict[str, Any]] = None,
        timeout_seconds: int = 30,
    ) -> DistributedTransaction:
        """Begin a new distributed transaction.

        Args:
            participant_nodes: List of node IDs
            data: Transaction data
            timeout_seconds: Transaction timeout

        Returns:
            Created transaction
        """
        transaction_id = str(uuid.uuid4())
        
        transaction = DistributedTransaction(
            transaction_id=transaction_id,
            phase=TransactionPhase.PREPARING,
            timeout=timedelta(seconds=timeout_seconds),
            data=data or {},
        )

        # Add participants
        for node_id in participant_nodes:
            participant = TransactionParticipant(
                participant_id=f"{transaction_id}-{node_id}",
                node_id=node_id,
            )
            transaction.add_participant(participant)

        self._transactions[transaction_id] = transaction
        logger.info(f"Started transaction {transaction_id} with {len(participant_nodes)} participants")

        return transaction

    async def execute_transaction(
        self,
        transaction_id: str,
    ) -> bool:
        """Execute a distributed transaction using 2PC.

        Args:
            transaction_id: Transaction to execute

        Returns:
            True if committed, False if aborted
        """
        transaction = self._transactions.get(transaction_id)
        if not transaction:
            raise ValueError(f"Transaction not found: {transaction_id}")

        try:
            # Phase 1: Prepare
            logger.info(f"Transaction {transaction_id}: Starting prepare phase")
            transaction.phase = TransactionPhase.PREPARING

            prepare_tasks = []
            for participant in transaction.participants.values():
                if participant.node_id not in self._prepare_handlers:
                    logger.error(f"No prepare handler for node {participant.node_id}")
                    participant.state = ParticipantState.FAILED
                    participant.error = "No prepare handler registered"
                    continue

                prepare_tasks.append(
                    self._prepare_participant(transaction, participant)
                )

            # Wait for all prepare responses
            if prepare_tasks:
                await asyncio.gather(*prepare_tasks, return_exceptions=True)

            # Check if all prepared
            if transaction.any_failed() or not transaction.all_prepared():
                logger.warning(f"Transaction {transaction_id}: Prepare phase failed")
                await self._abort_transaction(transaction)
                return False

            if transaction.is_expired():
                logger.warning(f"Transaction {transaction_id}: Timeout during prepare")
                await self._abort_transaction(transaction)
                return False

            logger.info(f"Transaction {transaction_id}: All participants prepared")
            transaction.phase = TransactionPhase.PREPARED

            # Phase 2: Commit
            logger.info(f"Transaction {transaction_id}: Starting commit phase")
            transaction.phase = TransactionPhase.COMMITTING

            commit_tasks = []
            for participant in transaction.participants.values():
                if participant.node_id not in self._commit_handlers:
                    logger.error(f"No commit handler for node {participant.node_id}")
                    continue

                commit_tasks.append(
                    self._commit_participant(transaction, participant)
                )

            # Wait for all commits
            if commit_tasks:
                await asyncio.gather(*commit_tasks, return_exceptions=True)

            # Mark as committed
            transaction.phase = TransactionPhase.COMMITTED
            transaction.completed_at = datetime.now()

            logger.info(f"Transaction {transaction_id}: Successfully committed")
            return True

        except Exception as e:
            logger.error(f"Transaction {transaction_id}: Error during execution: {e}")
            await self._abort_transaction(transaction)
            return False

    async def _prepare_participant(
        self,
        transaction: DistributedTransaction,
        participant: TransactionParticipant,
    ) -> None:
        """Prepare a participant."""
        try:
            participant.state = ParticipantState.PREPARING
            
            handler = self._prepare_handlers[participant.node_id]
            success = await asyncio.wait_for(
                handler(transaction.transaction_id, transaction.data),
                timeout=10.0,
            )

            if success:
                participant.state = ParticipantState.PREPARED
                participant.prepare_timestamp = datetime.now()
                logger.debug(f"Participant {participant.participant_id} prepared")
            else:
                participant.state = ParticipantState.FAILED
                participant.error = "Prepare returned False"
                logger.warning(f"Participant {participant.participant_id} failed to prepare")

        except asyncio.TimeoutError:
            participant.state = ParticipantState.FAILED
            participant.error = "Prepare timeout"
            logger.error(f"Participant {participant.participant_id} prepare timeout")
        except Exception as e:
            participant.state = ParticipantState.FAILED
            participant.error = str(e)
            logger.error(f"Participant {participant.participant_id} prepare error: {e}")

    async def _commit_participant(
        self,
        transaction: DistributedTransaction,
        participant: TransactionParticipant,
    ) -> None:
        """Commit a participant."""
        try:
            handler = self._commit_handlers[participant.node_id]
            success = await asyncio.wait_for(
                handler(transaction.transaction_id),
                timeout=10.0,
            )

            if success:
                participant.state = ParticipantState.COMMITTED
                participant.commit_timestamp = datetime.now()
                logger.debug(f"Participant {participant.participant_id} committed")
            else:
                logger.warning(f"Participant {participant.participant_id} commit returned False")

        except Exception as e:
            logger.error(f"Participant {participant.participant_id} commit error: {e}")

    async def _abort_transaction(self, transaction: DistributedTransaction) -> None:
        """Abort a transaction."""
        logger.info(f"Transaction {transaction.transaction_id}: Aborting")
        transaction.phase = TransactionPhase.ABORTING

        # Abort all participants
        abort_tasks = []
        for participant in transaction.participants.values():
            if participant.node_id not in self._abort_handlers:
                continue

            abort_tasks.append(
                self._abort_participant(transaction, participant)
            )

        if abort_tasks:
            await asyncio.gather(*abort_tasks, return_exceptions=True)

        transaction.phase = TransactionPhase.ABORTED
        transaction.completed_at = datetime.now()
        logger.info(f"Transaction {transaction.transaction_id}: Aborted")

    async def _abort_participant(
        self,
        transaction: DistributedTransaction,
        participant: TransactionParticipant,
    ) -> None:
        """Abort a participant."""
        try:
            handler = self._abort_handlers[participant.node_id]
            await asyncio.wait_for(
                handler(transaction.transaction_id),
                timeout=10.0,
            )
            participant.state = ParticipantState.ABORTED
            logger.debug(f"Participant {participant.participant_id} aborted")
        except Exception as e:
            logger.error(f"Participant {participant.participant_id} abort error: {e}")

    def get_transaction(self, transaction_id: str) -> Optional[DistributedTransaction]:
        """Get transaction by ID.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction or None
        """
        return self._transactions.get(transaction_id)

    def get_active_transactions(self) -> List[DistributedTransaction]:
        """Get all active transactions.

        Returns:
            List of active transactions
        """
        return [
            t for t in self._transactions.values()
            if t.phase not in [TransactionPhase.COMMITTED, TransactionPhase.ABORTED]
        ]


@dataclass
class SagaStep:
    """Step in a saga transaction."""

    step_id: str
    action: Callable[[Dict[str, Any]], Any]  # Forward action
    compensation: Callable[[Dict[str, Any]], None]  # Rollback action
    completed: bool = False
    compensated: bool = False
    result: Optional[Any] = None
    error: Optional[str] = None


class SagaCoordinator:
    """Coordinator for saga pattern transactions."""

    def __init__(self) -> None:
        """Initialize saga coordinator."""
        self._sagas: Dict[str, List[SagaStep]] = {}
        self._saga_data: Dict[str, Dict[str, Any]] = {}

    def create_saga(
        self,
        saga_id: str,
        steps: List[Tuple[Callable, Callable]],
    ) -> None:
        """Create a new saga.

        Args:
            saga_id: Unique saga identifier
            steps: List of (action, compensation) tuples
        """
        saga_steps = []
        for i, (action, compensation) in enumerate(steps):
            step = SagaStep(
                step_id=f"{saga_id}-step-{i}",
                action=action,
                compensation=compensation,
            )
            saga_steps.append(step)

        self._sagas[saga_id] = saga_steps
        self._saga_data[saga_id] = {}
        logger.info(f"Created saga {saga_id} with {len(steps)} steps")

    async def execute_saga(self, saga_id: str, initial_data: Optional[Dict[str, Any]] = None) -> bool:
        """Execute a saga transaction.

        Args:
            saga_id: Saga to execute
            initial_data: Initial data for the saga

        Returns:
            True if saga completed successfully
        """
        steps = self._sagas.get(saga_id)
        if not steps:
            raise ValueError(f"Saga not found: {saga_id}")

        data = self._saga_data[saga_id]
        if initial_data:
            data.update(initial_data)

        logger.info(f"Executing saga {saga_id}")

        # Execute steps sequentially
        for i, step in enumerate(steps):
            try:
                logger.debug(f"Saga {saga_id}: Executing step {i}")
                result = await step.action(data)
                step.completed = True
                step.result = result

                # Update saga data with result
                if result and isinstance(result, dict):
                    data.update(result)

            except Exception as e:
                logger.error(f"Saga {saga_id}: Step {i} failed: {e}")
                step.error = str(e)

                # Compensate all completed steps in reverse order
                await self._compensate_saga(saga_id, i)
                return False

        logger.info(f"Saga {saga_id}: Successfully completed")
        return True

    async def _compensate_saga(self, saga_id: str, failed_step_index: int) -> None:
        """Compensate a failed saga.

        Args:
            saga_id: Saga ID
            failed_step_index: Index of the step that failed
        """
        steps = self._sagas[saga_id]
        data = self._saga_data[saga_id]

        logger.warning(f"Saga {saga_id}: Compensating {failed_step_index} completed steps")

        # Compensate in reverse order
        for i in range(failed_step_index - 1, -1, -1):
            step = steps[i]
            if not step.completed:
                continue

            try:
                logger.debug(f"Saga {saga_id}: Compensating step {i}")
                await step.compensation(data)
                step.compensated = True
            except Exception as e:
                logger.error(f"Saga {saga_id}: Compensation for step {i} failed: {e}")

    def get_saga_status(self, saga_id: str) -> Dict[str, Any]:
        """Get status of a saga.

        Args:
            saga_id: Saga ID

        Returns:
            Status dictionary
        """
        steps = self._sagas.get(saga_id)
        if not steps:
            return {"error": "Saga not found"}

        return {
            "saga_id": saga_id,
            "total_steps": len(steps),
            "completed_steps": sum(1 for s in steps if s.completed),
            "compensated_steps": sum(1 for s in steps if s.compensated),
            "steps": [
                {
                    "step_id": s.step_id,
                    "completed": s.completed,
                    "compensated": s.compensated,
                    "error": s.error,
                }
                for s in steps
            ],
        }
