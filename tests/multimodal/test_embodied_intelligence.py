"""Tests for Embodied Intelligence (Phase 12.4)."""

import pytest

from src.multimodal.embodied_intelligence import (
    Action,
    ActionPlan,
    ActionStatus,
    ActionType,
    EmbodiedIntelligence,
    Goal,
    PhysicalState,
    Position3D,
    SensorReading,
    SensorType,
)


class TestPosition3D:
    """Tests for Position3D dataclass."""

    def test_create_position(self) -> None:
        """Test creating a 3D position."""
        pos = Position3D(x=1.0, y=2.0, z=3.0)

        assert pos.x == 1.0
        assert pos.y == 2.0
        assert pos.z == 3.0

    def test_distance_calculation(self) -> None:
        """Test distance calculation between positions."""
        pos1 = Position3D(0.0, 0.0, 0.0)
        pos2 = Position3D(3.0, 4.0, 0.0)

        distance = pos1.distance_to(pos2)
        assert abs(distance - 5.0) < 1e-10  # 3-4-5 triangle

    def test_position_string(self) -> None:
        """Test position string representation."""
        pos = Position3D(1.5, 2.5, 3.5)
        str_repr = str(pos)

        assert "1.50" in str_repr
        assert "2.50" in str_repr
        assert "3.50" in str_repr


class TestPhysicalState:
    """Tests for PhysicalState dataclass."""

    def test_create_physical_state(self) -> None:
        """Test creating physical state."""
        pos = Position3D(1.0, 2.0, 3.0)
        state = PhysicalState(
            position=pos,
            orientation=(0.1, 0.2, 0.3),
            velocity=(1.0, 0.0, 0.0),
            gripping=True,
            energy_level=0.8,
        )

        assert state.position == pos
        assert state.orientation == (0.1, 0.2, 0.3)
        assert state.gripping is True
        assert state.energy_level == 0.8

    def test_physical_state_validation(self) -> None:
        """Test physical state validation."""
        pos = Position3D(0.0, 0.0, 0.0)

        # Valid state
        PhysicalState(position=pos, energy_level=0.5)

        # Invalid energy level
        with pytest.raises(ValueError, match="Energy level must be"):
            PhysicalState(position=pos, energy_level=1.5)


class TestSensorReading:
    """Tests for SensorReading dataclass."""

    def test_create_sensor_reading(self) -> None:
        """Test creating sensor reading."""
        reading = SensorReading(
            sensor_type=SensorType.CAMERA,
            value={"image_data": "base64..."},
            confidence=0.95,
        )

        assert reading.sensor_type == SensorType.CAMERA
        assert reading.value["image_data"] == "base64..."
        assert reading.confidence == 0.95

    def test_sensor_reading_validation(self) -> None:
        """Test sensor reading validation."""
        # Valid reading
        SensorReading(sensor_type=SensorType.TOUCH, value=0.5, confidence=0.8)

        # Invalid confidence
        with pytest.raises(ValueError, match="Confidence must be"):
            SensorReading(sensor_type=SensorType.TOUCH, value=0.5, confidence=1.5)


class TestAction:
    """Tests for Action dataclass."""

    def test_create_action(self) -> None:
        """Test creating an action."""
        target = Position3D(5.0, 5.0, 0.0)
        action = Action(
            action_type=ActionType.MOVE,
            target_position=target,
            parameters={"speed": 1.5},
            duration=3.0,
        )

        assert action.action_type == ActionType.MOVE
        assert action.target_position == target
        assert action.parameters["speed"] == 1.5
        assert action.duration == 3.0
        assert action.status == ActionStatus.PLANNED

    def test_action_validation(self) -> None:
        """Test action validation."""
        # Valid action
        Action(action_type=ActionType.GRASP, duration=1.0)

        # Invalid duration
        with pytest.raises(ValueError, match="Duration must be"):
            Action(action_type=ActionType.GRASP, duration=-1.0)


class TestGoal:
    """Tests for Goal dataclass."""

    def test_create_goal(self) -> None:
        """Test creating a goal."""
        target_pos = Position3D(10.0, 10.0, 0.0)
        goal = Goal(
            description="Move to target location",
            target_state={"position": target_pos},
            success_criteria={"position_reached": True},
            priority=0.9,
        )

        assert goal.description == "Move to target location"
        assert goal.target_state is not None
        assert goal.target_state["position"] == target_pos
        assert goal.priority == 0.9

    def test_goal_validation(self) -> None:
        """Test goal validation."""
        # Valid goal
        Goal(description="Test goal", priority=0.5)

        # Invalid priority
        with pytest.raises(ValueError, match="Priority must be"):
            Goal(description="Test goal", priority=1.5)


class TestActionPlan:
    """Tests for ActionPlan dataclass."""

    def test_create_action_plan(self) -> None:
        """Test creating an action plan."""
        goal = Goal(description="Test goal")
        actions = [
            Action(action_type=ActionType.OBSERVE, duration=1.0),
            Action(action_type=ActionType.MOVE, duration=2.0),
        ]

        plan = ActionPlan(
            goal=goal,
            actions=actions,
            expected_duration=3.0,
            confidence=0.8,
        )

        assert plan.goal == goal
        assert len(plan.actions) == 2
        assert plan.expected_duration == 3.0
        assert plan.confidence == 0.8

    def test_action_plan_total_actions(self) -> None:
        """Test total actions calculation."""
        goal = Goal(description="Test")
        plan = ActionPlan(
            goal=goal,
            actions=[
                Action(action_type=ActionType.MOVE, duration=1.0),
                Action(action_type=ActionType.GRASP, duration=1.0),
            ],
        )

        assert plan.total_actions() == 2

    def test_action_plan_validation(self) -> None:
        """Test action plan validation."""
        goal = Goal(description="Test")

        # Valid plan
        ActionPlan(goal=goal, expected_duration=5.0, confidence=0.8)

        # Invalid confidence
        with pytest.raises(ValueError, match="Confidence must be"):
            ActionPlan(goal=goal, confidence=1.5)

        # Invalid duration
        with pytest.raises(ValueError, match="Expected duration must be"):
            ActionPlan(goal=goal, expected_duration=-1.0)


class TestEmbodiedIntelligence:
    """Tests for EmbodiedIntelligence class."""

    def test_embodied_intelligence_initialization(self) -> None:
        """Test embodied intelligence initialization."""
        initial_pos = Position3D(1.0, 2.0, 3.0)
        ei = EmbodiedIntelligence(initial_position=initial_pos, enable_physics=True)

        assert ei.current_state.position == initial_pos
        assert ei.enable_physics is True

    def test_sense_environment(self) -> None:
        """Test environment sensing."""
        ei = EmbodiedIntelligence()

        readings = [
            SensorReading(sensor_type=SensorType.CAMERA, value="image", confidence=0.9),
            SensorReading(sensor_type=SensorType.TOUCH, value=0.5, confidence=0.8),
        ]

        env_state = ei.sense_environment(readings)

        assert isinstance(env_state, dict)
        assert "camera" in env_state
        assert "touch" in env_state
        assert "summary" in env_state
        assert "obstacles_detected" in env_state

    def test_plan_action_sequence(self) -> None:
        """Test action sequence planning."""
        ei = EmbodiedIntelligence()

        goal = Goal(
            description="Move to target",
            target_state={"position": Position3D(5.0, 5.0, 0.0)},
        )

        plan = ei.plan_action_sequence(goal)

        assert isinstance(plan, ActionPlan)
        assert plan.goal == goal
        assert len(plan.actions) > 0
        assert plan.expected_duration >= 0.0
        assert 0.0 <= plan.confidence <= 1.0

    def test_execute_action_move(self) -> None:
        """Test executing a move action."""
        ei = EmbodiedIntelligence()

        target = Position3D(5.0, 5.0, 0.0)
        action = Action(action_type=ActionType.MOVE, target_position=target, duration=2.0)

        status = ei.execute_action(action)

        assert status == ActionStatus.COMPLETED
        assert ei.current_state.position == target

    def test_execute_action_grasp(self) -> None:
        """Test executing a grasp action."""
        ei = EmbodiedIntelligence()

        action = Action(action_type=ActionType.GRASP, duration=1.0)

        status = ei.execute_action(action)

        assert status == ActionStatus.COMPLETED
        assert ei.current_state.gripping is True

    def test_execute_action_release(self) -> None:
        """Test executing a release action."""
        ei = EmbodiedIntelligence()

        # First grasp
        ei.execute_action(Action(action_type=ActionType.GRASP, duration=1.0))
        assert ei.current_state.gripping is True

        # Then release
        action = Action(action_type=ActionType.RELEASE, duration=0.5)
        status = ei.execute_action(action)

        assert status == ActionStatus.COMPLETED
        assert ei.current_state.gripping is False

    def test_execute_plan(self) -> None:
        """Test executing full action plan."""
        ei = EmbodiedIntelligence()

        goal = Goal(description="Observe and grasp")
        plan = ActionPlan(
            goal=goal,
            actions=[
                Action(action_type=ActionType.OBSERVE, duration=0.5),
                Action(action_type=ActionType.GRASP, duration=1.0),
            ],
        )

        success = ei.execute_plan(plan)

        assert success is True
        assert ei.current_state.gripping is True

    def test_move_to(self) -> None:
        """Test move_to convenience method."""
        ei = EmbodiedIntelligence()

        target = Position3D(3.0, 4.0, 0.0)
        action = ei.move_to(target, speed=1.5)

        assert action.action_type == ActionType.MOVE
        assert action.status == ActionStatus.COMPLETED
        assert ei.current_state.position == target

    def test_grasp_object(self) -> None:
        """Test grasp_object convenience method."""
        ei = EmbodiedIntelligence()

        obj_pos = Position3D(2.0, 2.0, 1.0)
        action = ei.grasp_object(obj_pos)

        assert action.action_type == ActionType.GRASP
        assert action.status == ActionStatus.COMPLETED
        assert ei.current_state.gripping is True

    def test_release_object(self) -> None:
        """Test release_object convenience method."""
        ei = EmbodiedIntelligence()

        # Grasp first
        ei.grasp_object(Position3D(1.0, 1.0, 0.0))

        # Then release
        action = ei.release_object()

        assert action.action_type == ActionType.RELEASE
        assert action.status == ActionStatus.COMPLETED
        assert ei.current_state.gripping is False

    def test_get_current_state(self) -> None:
        """Test getting current state."""
        initial_pos = Position3D(1.0, 2.0, 3.0)
        ei = EmbodiedIntelligence(initial_position=initial_pos)

        state = ei.get_current_state()

        assert isinstance(state, PhysicalState)
        assert state.position == initial_pos

    def test_check_goal_achieved_position(self) -> None:
        """Test checking if position goal is achieved."""
        ei = EmbodiedIntelligence()

        target = Position3D(0.05, 0.05, 0.0)  # Very close to origin
        goal = Goal(
            description="Reach target",
            target_state={"position": target},
        )

        # Move close to target
        ei.move_to(target)

        achieved = ei.check_goal_achieved(goal)
        assert achieved is True

    def test_get_sensor_history(self) -> None:
        """Test getting sensor history."""
        ei = EmbodiedIntelligence()

        readings = [
            SensorReading(sensor_type=SensorType.CAMERA, value="img1", confidence=0.9),
            SensorReading(sensor_type=SensorType.TOUCH, value=0.5, confidence=0.8),
        ]

        ei.sense_environment(readings)

        history = ei.get_sensor_history()
        assert len(history) == 2

        camera_history = ei.get_sensor_history(sensor_type=SensorType.CAMERA)
        assert len(camera_history) == 1
        assert camera_history[0].sensor_type == SensorType.CAMERA

    def test_get_action_history(self) -> None:
        """Test getting action history."""
        ei = EmbodiedIntelligence()

        ei.execute_action(Action(action_type=ActionType.OBSERVE, duration=1.0))
        ei.execute_action(Action(action_type=ActionType.MOVE, duration=2.0))

        history = ei.get_action_history()
        assert len(history) == 2
        assert history[0].action_type == ActionType.OBSERVE
        assert history[1].action_type == ActionType.MOVE

    def test_clear_history(self) -> None:
        """Test clearing history."""
        ei = EmbodiedIntelligence()

        # Add some sensor readings
        readings = [SensorReading(sensor_type=SensorType.CAMERA, value="img", confidence=0.9)]
        ei.sense_environment(readings)

        # Execute some actions
        ei.execute_action(Action(action_type=ActionType.OBSERVE, duration=1.0))

        assert len(ei.get_sensor_history()) == 1
        assert len(ei.get_action_history()) == 1

        # Clear history
        ei.clear_history()

        assert len(ei.get_sensor_history()) == 0
        assert len(ei.get_action_history()) == 0

    def test_energy_consumption(self) -> None:
        """Test that actions consume energy."""
        ei = EmbodiedIntelligence()
        initial_energy = ei.current_state.energy_level

        # Execute a move action (consumes energy)
        ei.move_to(Position3D(10.0, 10.0, 0.0))

        # Energy should have decreased
        assert ei.current_state.energy_level < initial_energy
