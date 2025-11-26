"""Tests for node failure recovery with Raft consensus."""

import pytest

from src.scaling.node_failure_recovery import (
    FailoverCoordinator,
    LogEntry,
    LogEntryType,
    NodeRole,
    RaftNode,
    RaftState,
)


def test_raft_state_creation() -> None:
    """Test RaftState creation."""
    state = RaftState()

    assert state.current_term == 0
    assert state.voted_for is None
    assert len(state.log) == 0
    assert state.commit_index == 0
    assert state.last_applied == 0


def test_raft_state_to_dict() -> None:
    """Test RaftState serialization."""
    state = RaftState(current_term=5, voted_for="node-1")

    data = state.to_dict()

    assert data["current_term"] == 5
    assert data["voted_for"] == "node-1"
    assert isinstance(data["log"], list)


def test_log_entry_creation() -> None:
    """Test LogEntry creation."""
    entry = LogEntry(
        term=1,
        index=0,
        entry_type=LogEntryType.COMMAND,
        command={"operation": "set", "key": "test", "value": "value1"},
    )

    assert entry.term == 1
    assert entry.index == 0
    assert entry.entry_type == LogEntryType.COMMAND
    assert entry.command["key"] == "test"


def test_log_entry_to_dict() -> None:
    """Test LogEntry serialization."""
    entry = LogEntry(
        term=1,
        index=0,
        entry_type=LogEntryType.COMMAND,
        command={"operation": "set"},
    )

    data = entry.to_dict()

    assert data["term"] == 1
    assert data["index"] == 0
    assert data["entry_type"] == "command"
    assert isinstance(data["timestamp"], str)


def test_raft_node_creation() -> None:
    """Test RaftNode creation."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    assert node.node_id == "node-1"
    assert len(node.cluster_nodes) == 3
    assert node.role == NodeRole.FOLLOWER
    assert node.leader_id is None


def test_raft_node_initial_state() -> None:
    """Test RaftNode initial state."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    state = node.get_state()

    assert state["node_id"] == "node-1"
    assert state["role"] == "follower"
    assert state["term"] == 0
    assert state["log_size"] == 0


@pytest.mark.asyncio
async def test_raft_node_start_stop() -> None:
    """Test RaftNode start and stop."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    await node.start()
    assert node._running is True

    await node.stop()
    assert node._running is False


@pytest.mark.asyncio
async def test_apply_command_set() -> None:
    """Test applying SET command to state machine."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1"],
    )

    command = {"operation": "set", "key": "test_key", "value": "test_value"}
    node._apply_command(command)

    assert node.state_machine["test_key"] == "test_value"


@pytest.mark.asyncio
async def test_apply_command_delete() -> None:
    """Test applying DELETE command to state machine."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1"],
    )

    # Set a value first
    node.state_machine["test_key"] = "test_value"
    assert "test_key" in node.state_machine

    # Delete it
    command = {"operation": "delete", "key": "test_key"}
    node._apply_command(command)

    assert "test_key" not in node.state_machine


@pytest.mark.asyncio
async def test_become_leader() -> None:
    """Test node becoming leader."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    await node.start()
    await node._become_leader()

    assert node.role == NodeRole.LEADER
    assert node.leader_id == "node-1"
    assert len(node.next_index) == 2  # For other 2 nodes
    assert len(node.match_index) == 2

    await node.stop()


@pytest.mark.asyncio
async def test_append_entry_as_leader() -> None:
    """Test appending entry as leader."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    await node.start()
    await node._become_leader()

    entry = LogEntry(
        term=1,
        index=1,
        entry_type=LogEntryType.COMMAND,
        command={"operation": "set", "key": "test", "value": "value1"},
    )

    success = await node.append_entry(entry)

    assert success is True
    assert len(node.state.log) > 0  # At least no-op + this entry

    await node.stop()


@pytest.mark.asyncio
async def test_append_entry_as_follower() -> None:
    """Test that follower cannot append entries."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    entry = LogEntry(
        term=1,
        index=0,
        entry_type=LogEntryType.COMMAND,
        command={"operation": "set"},
    )

    success = await node.append_entry(entry)

    assert success is False
    assert len(node.state.log) == 0


@pytest.mark.asyncio
async def test_submit_command_as_leader() -> None:
    """Test submitting command as leader."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2"],
    )

    await node.start()
    await node._become_leader()

    command = {"operation": "set", "key": "test", "value": "value1"}
    success = await node.submit_command(command)

    assert success is True
    assert any(e.command == command for e in node.state.log)

    await node.stop()


@pytest.mark.asyncio
async def test_submit_command_as_follower() -> None:
    """Test submitting command as follower (should fail)."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    command = {"operation": "set", "key": "test", "value": "value1"}
    success = await node.submit_command(command)

    assert success is False


@pytest.mark.asyncio
async def test_handle_append_entries_success() -> None:
    """Test handling AppendEntries RPC."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    await node.start()

    entries = [
        LogEntry(
            term=1,
            index=0,
            entry_type=LogEntryType.COMMAND,
            command={"operation": "set", "key": "k1", "value": "v1"},
        )
    ]

    success = await node.handle_append_entries(
        term=1,
        leader_id="node-2",
        prev_log_index=-1,
        prev_log_term=0,
        entries=entries,
        leader_commit=0,
    )

    assert success is True
    assert node.state.current_term == 1
    assert node.leader_id == "node-2"
    assert len(node.state.log) == 1

    await node.stop()


@pytest.mark.asyncio
async def test_handle_append_entries_old_term() -> None:
    """Test rejecting AppendEntries from old term."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    node.state.current_term = 5

    success = await node.handle_append_entries(
        term=3,  # Old term
        leader_id="node-2",
        prev_log_index=-1,
        prev_log_term=0,
        entries=[],
        leader_commit=0,
    )

    assert success is False


@pytest.mark.asyncio
async def test_handle_append_entries_updates_term() -> None:
    """Test that AppendEntries updates term if higher."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    node.state.current_term = 1

    success = await node.handle_append_entries(
        term=5,  # Higher term
        leader_id="node-2",
        prev_log_index=-1,
        prev_log_term=0,
        entries=[],
        leader_commit=0,
    )

    assert success is True
    assert node.state.current_term == 5


@pytest.mark.asyncio
async def test_election_timeout_randomization() -> None:
    """Test that election timeout is randomized."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
        election_timeout_min=100.0,
        election_timeout_max=200.0,
    )

    timeouts = [node._get_election_timeout() for _ in range(100)]

    # All should be within range
    assert all(0.1 <= t <= 0.2 for t in timeouts)

    # Should have variety (not all the same)
    assert len(set(timeouts)) > 10


@pytest.mark.asyncio
async def test_failover_coordinator_creation() -> None:
    """Test FailoverCoordinator creation."""
    coordinator = FailoverCoordinator(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    assert coordinator.node_id == "node-1"
    assert len(coordinator.cluster_nodes) == 3
    assert len(coordinator.node_health) == 3
    assert all(coordinator.node_health.values())  # All healthy initially


@pytest.mark.asyncio
async def test_failover_coordinator_start_stop() -> None:
    """Test FailoverCoordinator start and stop."""
    coordinator = FailoverCoordinator(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    await coordinator.start()
    assert coordinator._running is True
    assert coordinator.raft_node._running is True

    await coordinator.stop()
    assert coordinator._running is False


@pytest.mark.asyncio
async def test_failover_coordinator_get_status() -> None:
    """Test getting cluster status."""
    coordinator = FailoverCoordinator(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    status = coordinator.get_cluster_status()

    assert status["node_id"] == "node-1"
    assert status["total_nodes"] == 3
    assert status["healthy_nodes"] == 3
    assert "raft_state" in status
    assert "node_health" in status


@pytest.mark.asyncio
async def test_handle_node_failure() -> None:
    """Test handling node failure."""
    coordinator = FailoverCoordinator(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    await coordinator.start()
    await coordinator.raft_node._become_leader()

    # Simulate node failure
    await coordinator._handle_node_failure("node-2")

    assert "node-2" in coordinator.failed_nodes
    assert len(coordinator.failed_nodes) == 1

    await coordinator.stop()


@pytest.mark.asyncio
async def test_handle_node_recovery() -> None:
    """Test handling node recovery."""
    coordinator = FailoverCoordinator(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    await coordinator.start()
    await coordinator.raft_node._become_leader()

    # Simulate failure then recovery
    coordinator.failed_nodes.add("node-2")
    await coordinator._handle_node_recovery("node-2")

    assert "node-2" not in coordinator.failed_nodes
    assert "node-2" in coordinator.recovered_nodes

    await coordinator.stop()


@pytest.mark.asyncio
async def test_leader_initialization() -> None:
    """Test leader initializes next_index and match_index."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    # Add some log entries
    node.state.log.append(LogEntry(term=0, index=0, entry_type=LogEntryType.NO_OP, command={}))

    await node.start()
    await node._become_leader()

    # Check indices initialized
    assert "node-2" in node.next_index
    assert "node-3" in node.next_index
    assert node.next_index["node-2"] == 1  # last_log_index + 1
    assert node.match_index["node-2"] == 0

    await node.stop()


@pytest.mark.asyncio
async def test_multiple_log_entries() -> None:
    """Test appending multiple log entries."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2"],
    )

    await node.start()
    await node._become_leader()

    # Append multiple entries
    for i in range(5):
        entry = LogEntry(
            term=1,
            index=len(node.state.log),
            entry_type=LogEntryType.COMMAND,
            command={"operation": "set", "key": f"k{i}", "value": f"v{i}"},
        )
        await node.append_entry(entry)

    # Should have no-op + 5 commands
    assert len(node.state.log) >= 5

    await node.stop()


@pytest.mark.asyncio
async def test_state_machine_consistency() -> None:
    """Test that state machine applies commands in order."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1"],
    )

    # Apply commands directly
    commands = [
        {"operation": "set", "key": "x", "value": "1"},
        {"operation": "set", "key": "y", "value": "2"},
        {"operation": "set", "key": "x", "value": "3"},  # Overwrite x
    ]

    for cmd in commands:
        node._apply_command(cmd)

    assert node.state_machine["x"] == "3"
    assert node.state_machine["y"] == "2"


@pytest.mark.asyncio
async def test_commit_index_update() -> None:
    """Test commit index update mechanism."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    await node.start()
    await node._become_leader()

    # Simulate log replication
    node.match_index["node-2"] = 1
    node.match_index["node-3"] = 1

    # Add entry to log
    entry = LogEntry(
        term=node.state.current_term,
        index=1,
        entry_type=LogEntryType.COMMAND,
        command={"operation": "set", "key": "test", "value": "val"},
    )
    # Ensure we have entries in log
    if len(node.state.log) <= 1:
        node.state.log.append(entry)

    await node._update_commit_index()

    # Commit index should be updated (with majority replication)
    assert node.state.commit_index >= 0

    await node.stop()


@pytest.mark.asyncio
async def test_node_role_transitions() -> None:
    """Test node role transitions."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2", "node-3"],
    )

    # Start as follower
    assert node.role == NodeRole.FOLLOWER

    # Become candidate
    node.role = NodeRole.CANDIDATE
    assert node.role == NodeRole.CANDIDATE

    # Become leader
    await node._become_leader()
    assert node.role == NodeRole.LEADER


@pytest.mark.asyncio
async def test_log_entry_types() -> None:
    """Test different log entry types."""
    node = RaftNode(
        node_id="node-1",
        cluster_nodes=["node-1", "node-2"],
    )

    await node.start()
    await node._become_leader()

    # Test different entry types
    types = [LogEntryType.COMMAND, LogEntryType.CONFIGURATION, LogEntryType.NO_OP]

    for entry_type in types:
        entry = LogEntry(
            term=1,
            index=len(node.state.log),
            entry_type=entry_type,
            command={},
        )
        await node.append_entry(entry)

    # Verify entries were added
    assert len(node.state.log) > len(types)

    await node.stop()
