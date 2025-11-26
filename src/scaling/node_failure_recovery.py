"""Node Failure Recovery with Raft Consensus Protocol.

This module implements:
- Raft consensus algorithm for distributed coordination
- Leader election
- Log replication
- State synchronization
- Automatic failover
"""

from __future__ import annotations

import asyncio
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class NodeRole(str, Enum):
    """Raft node roles."""

    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


class LogEntryType(str, Enum):
    """Types of log entries."""

    COMMAND = "command"
    CONFIGURATION = "configuration"
    NO_OP = "no_op"


@dataclass
class LogEntry:
    """Raft log entry."""

    term: int
    index: int
    entry_type: LogEntryType
    command: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "term": self.term,
            "index": self.index,
            "entry_type": self.entry_type.value,
            "command": self.command,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class RaftState:
    """Persistent Raft state."""

    current_term: int = 0
    voted_for: Optional[str] = None
    log: List[LogEntry] = field(default_factory=list)
    commit_index: int = 0
    last_applied: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "current_term": self.current_term,
            "voted_for": self.voted_for,
            "log": [entry.to_dict() for entry in self.log],
            "commit_index": self.commit_index,
            "last_applied": self.last_applied,
        }


class RaftNode:
    """Raft consensus node for distributed coordination."""

    def __init__(
        self,
        node_id: str,
        cluster_nodes: List[str],
        election_timeout_min: float = 150.0,
        election_timeout_max: float = 300.0,
        heartbeat_interval: float = 50.0,
    ) -> None:
        """Initialize Raft node.

        Args:
            node_id: Unique identifier for this node
            cluster_nodes: List of all node IDs in cluster (including self)
            election_timeout_min: Minimum election timeout (ms)
            election_timeout_max: Maximum election timeout (ms)
            heartbeat_interval: Leader heartbeat interval (ms)
        """
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes
        self.election_timeout_min = election_timeout_min / 1000.0  # Convert to seconds
        self.election_timeout_max = election_timeout_max / 1000.0
        self.heartbeat_interval = heartbeat_interval / 1000.0

        # Raft state
        self.state = RaftState()
        self.role = NodeRole.FOLLOWER
        self.leader_id: Optional[str] = None

        # Volatile state (leader only)
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}

        # Election and heartbeat
        self._election_timer: Optional[asyncio.Task[None]] = None
        self._heartbeat_timer: Optional[asyncio.Task[None]] = None
        self._running = False

        # State machine
        self.state_machine: Dict[str, Any] = {}

        logger.info(f"RaftNode {node_id} initialized with {len(cluster_nodes)} nodes")

    def _get_election_timeout(self) -> float:
        """Get randomized election timeout."""
        return random.uniform(self.election_timeout_min, self.election_timeout_max)

    def _reset_election_timer(self) -> None:
        """Reset election timer."""
        if self._election_timer:
            self._election_timer.cancel()

        if self._running:
            timeout = self._get_election_timeout()
            self._election_timer = asyncio.create_task(
                self._election_timeout_handler(timeout)
            )

    async def _election_timeout_handler(self, timeout: float) -> None:
        """Handle election timeout."""
        try:
            await asyncio.sleep(timeout)
            if self.role != NodeRole.LEADER:
                await self._start_election()
        except asyncio.CancelledError:
            pass

    async def _start_election(self) -> None:
        """Start leader election."""
        # Become candidate
        self.role = NodeRole.CANDIDATE
        self.state.current_term += 1
        self.state.voted_for = self.node_id
        votes_received = 1  # Vote for self

        logger.info(
            f"Node {self.node_id} starting election for term {self.state.current_term}"
        )

        # Request votes from other nodes
        for node_id in self.cluster_nodes:
            if node_id != self.node_id:
                # In real implementation, send RPC to node
                # For now, simulate vote response
                vote_granted = await self._request_vote(node_id)
                if vote_granted:
                    votes_received += 1

        # Check if won election
        majority = len(self.cluster_nodes) // 2 + 1
        if votes_received >= majority:
            await self._become_leader()
        else:
            # Lost election, revert to follower
            self.role = NodeRole.FOLLOWER
            self._reset_election_timer()

    async def _request_vote(self, node_id: str) -> bool:
        """Request vote from node.

        Args:
            node_id: Node to request vote from

        Returns:
            True if vote granted
        """
        # Simplified vote logic (in real implementation, would send RPC)
        # For testing, simulate vote based on term and log state

        # Check if we have the most up-to-date log (for future use in real impl)
        # last_log_index = len(self.state.log) - 1 if self.state.log else -1
        # last_log_term = self.state.log[-1].term if self.state.log else 0

        # Simulate vote grant (70% probability for testing)
        return random.random() < 0.7

    async def _become_leader(self) -> None:
        """Become leader."""
        self.role = NodeRole.LEADER
        self.leader_id = self.node_id

        # Initialize leader state
        last_log_index = len(self.state.log) - 1 if self.state.log else -1
        for node_id in self.cluster_nodes:
            if node_id != self.node_id:
                self.next_index[node_id] = last_log_index + 1
                self.match_index[node_id] = 0

        logger.info(
            f"Node {self.node_id} became LEADER for term {self.state.current_term}"
        )

        # Cancel election timer
        if self._election_timer:
            self._election_timer.cancel()

        # Start sending heartbeats
        if self._heartbeat_timer:
            self._heartbeat_timer.cancel()
        self._heartbeat_timer = asyncio.create_task(self._send_heartbeats())

        # Append no-op entry to commit entries from previous terms
        await self.append_entry(
            LogEntry(
                term=self.state.current_term,
                index=len(self.state.log),
                entry_type=LogEntryType.NO_OP,
                command={},
            )
        )

    async def _send_heartbeats(self) -> None:
        """Send periodic heartbeats to followers."""
        while self._running and self.role == NodeRole.LEADER:
            try:
                # Send AppendEntries RPC to all followers
                for node_id in self.cluster_nodes:
                    if node_id != self.node_id:
                        await self._append_entries_rpc(node_id)

                await asyncio.sleep(self.heartbeat_interval)
            except asyncio.CancelledError:
                break

    async def _append_entries_rpc(self, node_id: str) -> bool:
        """Send AppendEntries RPC to follower.

        Args:
            node_id: Follower node ID

        Returns:
            True if successful
        """
        # Get entries to send
        next_idx = self.next_index.get(node_id, 0)
        entries = self.state.log[next_idx:] if next_idx < len(self.state.log) else []

        # In real implementation, send RPC
        # For now, simulate success (90% probability)
        success = random.random() < 0.9

        if success:
            # Update indices
            if entries:
                self.match_index[node_id] = next_idx + len(entries) - 1
                self.next_index[node_id] = next_idx + len(entries)

            # Update commit index if majority replicated
            await self._update_commit_index()

        return success

    async def _update_commit_index(self) -> None:
        """Update commit index based on majority replication."""
        if self.role != NodeRole.LEADER:
            return

        # Find highest index replicated on majority
        for n in range(len(self.state.log) - 1, self.state.commit_index, -1):
            if self.state.log[n].term != self.state.current_term:
                continue

            # Count replicas
            replicas = 1  # Self
            for node_id in self.cluster_nodes:
                if node_id != self.node_id:
                    if self.match_index.get(node_id, 0) >= n:
                        replicas += 1

            # Check majority
            majority = len(self.cluster_nodes) // 2 + 1
            if replicas >= majority:
                self.state.commit_index = n
                await self._apply_committed_entries()
                break

    async def _apply_committed_entries(self) -> None:
        """Apply committed entries to state machine."""
        while self.state.last_applied < self.state.commit_index:
            self.state.last_applied += 1
            entry = self.state.log[self.state.last_applied]

            # Apply to state machine
            if entry.entry_type == LogEntryType.COMMAND:
                self._apply_command(entry.command)

            logger.debug(
                f"Node {self.node_id} applied entry {self.state.last_applied}: "
                f"{entry.entry_type.value}"
            )

    def _apply_command(self, command: Dict[str, Any]) -> None:
        """Apply command to state machine.

        Args:
            command: Command to apply
        """
        # Simple key-value store state machine
        operation = command.get("operation")
        key = command.get("key")

        if operation == "set":
            value = command.get("value")
            if key is not None:
                self.state_machine[key] = value
                logger.debug(f"State machine: SET {key} = {value}")
        elif operation == "delete":
            if key is not None and key in self.state_machine:
                del self.state_machine[key]
                logger.debug(f"State machine: DELETE {key}")

    async def append_entry(self, entry: LogEntry) -> bool:
        """Append entry to log (leader only).

        Args:
            entry: Log entry to append

        Returns:
            True if successfully replicated
        """
        if self.role != NodeRole.LEADER:
            logger.warning(f"Node {self.node_id} is not leader, cannot append entry")
            return False

        # Append to local log
        self.state.log.append(entry)
        logger.info(
            f"Leader {self.node_id} appended entry {entry.index} "
            f"(term={entry.term}, type={entry.entry_type.value})"
        )

        # Replicate to followers (handled by heartbeat mechanism)
        return True

    async def handle_append_entries(
        self,
        term: int,
        leader_id: str,
        prev_log_index: int,
        prev_log_term: int,
        entries: List[LogEntry],
        leader_commit: int,
    ) -> bool:
        """Handle AppendEntries RPC from leader.

        Args:
            term: Leader's term
            leader_id: Leader's ID
            prev_log_index: Index of log entry immediately preceding new ones
            prev_log_term: Term of prevLogIndex entry
            entries: Log entries to store
            leader_commit: Leader's commit index

        Returns:
            True if successful
        """
        # Reset election timer
        self._reset_election_timer()

        # Reply false if term < currentTerm
        if term < self.state.current_term:
            return False

        # Update term and convert to follower if necessary
        if term > self.state.current_term:
            self.state.current_term = term
            self.state.voted_for = None
            self.role = NodeRole.FOLLOWER

        self.leader_id = leader_id

        # Reply false if log doesn't contain entry at prevLogIndex with prevLogTerm
        if prev_log_index >= 0:
            if prev_log_index >= len(self.state.log):
                return False
            if self.state.log[prev_log_index].term != prev_log_term:
                # Delete conflicting entry and all that follow
                self.state.log = self.state.log[:prev_log_index]
                return False

        # Append new entries
        if entries:
            self.state.log.extend(entries)

        # Update commit index
        if leader_commit > self.state.commit_index:
            self.state.commit_index = min(
                leader_commit, len(self.state.log) - 1 if self.state.log else 0
            )
            await self._apply_committed_entries()

        return True

    async def submit_command(self, command: Dict[str, Any]) -> bool:
        """Submit command to cluster (redirects to leader if needed).

        Args:
            command: Command to submit

        Returns:
            True if successfully submitted
        """
        if self.role == NodeRole.LEADER:
            # Append as leader
            entry = LogEntry(
                term=self.state.current_term,
                index=len(self.state.log),
                entry_type=LogEntryType.COMMAND,
                command=command,
            )
            return await self.append_entry(entry)
        else:
            # Redirect to leader (in real implementation)
            logger.info(f"Node {self.node_id} redirecting to leader {self.leader_id}")
            return False

    def get_state(self) -> Dict[str, Any]:
        """Get current node state.

        Returns:
            Node state dictionary
        """
        return {
            "node_id": self.node_id,
            "role": self.role.value,
            "term": self.state.current_term,
            "leader_id": self.leader_id,
            "voted_for": self.state.voted_for,
            "log_size": len(self.state.log),
            "commit_index": self.state.commit_index,
            "last_applied": self.state.last_applied,
            "state_machine": self.state_machine.copy(),
        }

    async def start(self) -> None:
        """Start Raft node."""
        self._running = True
        self._reset_election_timer()
        logger.info(f"RaftNode {self.node_id} started")

    async def stop(self) -> None:
        """Stop Raft node."""
        self._running = False

        if self._election_timer:
            self._election_timer.cancel()
        if self._heartbeat_timer:
            self._heartbeat_timer.cancel()

        logger.info(f"RaftNode {self.node_id} stopped")


class FailoverCoordinator:
    """Coordinates automatic failover using Raft consensus."""

    def __init__(
        self,
        node_id: str,
        cluster_nodes: List[str],
        health_check_interval: float = 5.0,
    ) -> None:
        """Initialize failover coordinator.

        Args:
            node_id: This node's ID
            cluster_nodes: All cluster nodes
            health_check_interval: Health check interval (seconds)
        """
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes
        self.health_check_interval = health_check_interval

        # Raft consensus
        self.raft_node = RaftNode(node_id, cluster_nodes)

        # Node health tracking
        self.node_health: Dict[str, bool] = {nid: True for nid in cluster_nodes}

        # Failover state
        self.failed_nodes: Set[str] = set()
        self.recovered_nodes: Set[str] = set()

        self._running = False
        self._health_check_task: Optional[asyncio.Task[None]] = None

        logger.info(f"FailoverCoordinator initialized for node {node_id}")

    async def _check_node_health(self) -> None:
        """Periodically check node health."""
        while self._running:
            for node_id in self.cluster_nodes:
                if node_id == self.node_id:
                    continue

                # Simulate health check (in real implementation, ping node)
                is_healthy = random.random() < 0.95  # 95% uptime

                previous_health = self.node_health.get(node_id, True)

                if is_healthy != previous_health:
                    self.node_health[node_id] = is_healthy

                    if not is_healthy:
                        await self._handle_node_failure(node_id)
                    else:
                        await self._handle_node_recovery(node_id)

            await asyncio.sleep(self.health_check_interval)

    async def _handle_node_failure(self, node_id: str) -> None:
        """Handle node failure.

        Args:
            node_id: Failed node ID
        """
        self.failed_nodes.add(node_id)
        logger.warning(f"Node {node_id} failed")

        # Submit failure event to Raft log
        if self.raft_node.role == NodeRole.LEADER:
            command = {
                "operation": "node_failure",
                "node_id": node_id,
                "timestamp": datetime.now().isoformat(),
            }
            await self.raft_node.submit_command(command)

    async def _handle_node_recovery(self, node_id: str) -> None:
        """Handle node recovery.

        Args:
            node_id: Recovered node ID
        """
        if node_id in self.failed_nodes:
            self.failed_nodes.remove(node_id)
            self.recovered_nodes.add(node_id)
            logger.info(f"Node {node_id} recovered")

            # Submit recovery event to Raft log
            if self.raft_node.role == NodeRole.LEADER:
                command = {
                    "operation": "node_recovery",
                    "node_id": node_id,
                    "timestamp": datetime.now().isoformat(),
                }
                await self.raft_node.submit_command(command)

    async def start(self) -> None:
        """Start failover coordinator."""
        self._running = True
        await self.raft_node.start()
        self._health_check_task = asyncio.create_task(self._check_node_health())
        logger.info(f"FailoverCoordinator started for node {self.node_id}")

    async def stop(self) -> None:
        """Stop failover coordinator."""
        self._running = False

        if self._health_check_task:
            self._health_check_task.cancel()

        await self.raft_node.stop()
        logger.info(f"FailoverCoordinator stopped for node {self.node_id}")

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get cluster status.

        Returns:
            Cluster status dictionary
        """
        return {
            "node_id": self.node_id,
            "raft_state": self.raft_node.get_state(),
            "node_health": self.node_health.copy(),
            "failed_nodes": list(self.failed_nodes),
            "recovered_nodes": list(self.recovered_nodes),
            "healthy_nodes": sum(1 for h in self.node_health.values() if h),
            "total_nodes": len(self.cluster_nodes),
        }
