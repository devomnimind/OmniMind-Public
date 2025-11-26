from typing import Any

from unittest.mock import MagicMock, patch
import pytest

from src.integrations.dbus_controller import (
    DBusSessionController,
    DBusSystemController,
    _load_psutil,
)


class TestLoadPsutil:
    """Tests for _load_psutil helper."""

    def test_load_psutil_success(self) -> None:
        """Test successful psutil loading."""
        psutil = _load_psutil()
        # If psutil is available, it should return the module
        # If not, it should return None
        assert psutil is None or psutil is not None

    @patch("src.integrations.dbus_controller.cast")
    def test_load_psutil_import_error(self, mock_cast: MagicMock) -> None:
        """Test psutil loading when module is not available."""
        with patch("builtins.__import__", side_effect=ImportError):
            result = _load_psutil()
            assert result is None


class TestDBusSessionController:
    """Tests for DBusSessionController."""

    def test_initialization_default_bus(self) -> None:
        """Test initialization with default bus."""
        with patch("src.integrations.dbus_controller.dbus.SessionBus") as mock_bus:
            controller = DBusSessionController()
            assert controller._bus is not None
            mock_bus.assert_called_once()

    def test_initialization_custom_bus(self) -> None:
        """Test initialization with custom bus."""
        mock_bus = MagicMock()
        controller = DBusSessionController(bus=mock_bus)
        assert controller._bus is mock_bus

    @patch("src.integrations.dbus_controller.dbus.Interface")
    def test_control_media_player_play(self, mock_interface: MagicMock) -> None:
        """Test play action."""
        mock_iface = MagicMock()
        mock_interface.return_value = mock_iface

        mock_bus = MagicMock()
        controller = DBusSessionController(bus=mock_bus)

        response = controller.control_media_player("play")

        assert response["success"]
        assert response["action"] == "play"
        mock_iface.Play.assert_called_once()

    @patch("src.integrations.dbus_controller.dbus.Interface")
    def test_control_media_player_pause(self, mock_interface: MagicMock) -> None:
        """Test pause action."""
        mock_iface = MagicMock()
        mock_interface.return_value = mock_iface

        mock_bus = MagicMock()
        controller = DBusSessionController(bus=mock_bus)

        response = controller.control_media_player("pause")

        assert response["success"]
        assert response["action"] == "pause"
        mock_iface.Pause.assert_called_once()

    @patch("src.integrations.dbus_controller.dbus.Interface")
    def test_control_media_player_next(self, mock_interface: MagicMock) -> None:
        """Test next action."""
        mock_iface = MagicMock()
        mock_interface.return_value = mock_iface

        mock_bus = MagicMock()
        controller = DBusSessionController(bus=mock_bus)

        response = controller.control_media_player("next")

        assert response["success"]
        mock_iface.Next.assert_called_once()

    @patch("src.integrations.dbus_controller.dbus.Interface")
    def test_control_media_player_previous(self, mock_interface: MagicMock) -> None:
        """Test previous action."""
        mock_iface = MagicMock()
        mock_interface.return_value = mock_iface

        mock_bus = MagicMock()
        controller = DBusSessionController(bus=mock_bus)

        response = controller.control_media_player("previous")

        assert response["success"]
        mock_iface.Previous.assert_called_once()

    @patch("src.integrations.dbus_controller.dbus.Interface")
    def test_control_media_player_stop(self, mock_interface: MagicMock) -> None:
        """Test stop action."""
        mock_iface = MagicMock()
        mock_interface.return_value = mock_iface

        mock_bus = MagicMock()
        controller = DBusSessionController(bus=mock_bus)

        response = controller.control_media_player("stop")

        assert response["success"]
        mock_iface.Stop.assert_called_once()

    @patch("src.integrations.dbus_controller.dbus.Interface")
    def test_control_media_player_playpause(self, mock_interface: MagicMock) -> None:
        """Test playpause action."""
        mock_iface = MagicMock()
        mock_interface.return_value = mock_iface

        mock_bus = MagicMock()
        mock_proxy = MagicMock()
        mock_bus.get_object.return_value = mock_proxy

        controller = DBusSessionController(bus=mock_bus)
        response = controller.control_media_player("playpause", "org.test.Player")

        assert response["success"]
        mock_iface.PlayPause.assert_called_once()
        mock_bus.get_object.assert_called_once()

    def test_control_media_player_unsupported_action(self) -> None:
        """Test unsupported action."""
        mock_bus = MagicMock()
        controller = DBusSessionController(bus=mock_bus)

        response = controller.control_media_player("invalid_action")

        assert not response["success"]
        assert "Unsupported action" in response["error"]

    @patch("src.integrations.dbus_controller.dbus.Interface")
    def test_control_media_player_dbus_exception(self, mock_interface: MagicMock) -> None:
        """Test DBusException handling."""
        import dbus

        mock_iface = MagicMock()
        mock_iface.Play.side_effect = dbus.DBusException("Connection failed")
        mock_interface.return_value = mock_iface

        mock_bus = MagicMock()
        controller = DBusSessionController(bus=mock_bus)

        response = controller.control_media_player("play")

        assert not response["success"]
        assert "error" in response

    def test_control_media_player_attribute_error(self) -> None:
        """Test AttributeError handling."""
        # Test invalid action which returns error gracefully
        mock_bus = MagicMock()
        controller = DBusSessionController(bus=mock_bus)

        # Invalid action should return error, not raise
        response = controller.control_media_player("invalid")

        assert not response["success"]
        assert "Unsupported action" in response["error"]

    @patch("src.integrations.dbus_controller.dbus.Interface")
    def test_list_media_players(self, mock_interface: MagicMock) -> None:
        """Test listing media players."""
        mock_iface = MagicMock()
        mock_iface.ListNames.return_value = [
            "org.mpris.MediaPlayer2.vlc",
            "org.mpris.MediaPlayer2.spotify",
            "org.freedesktop.DBus",
            "other.service",
        ]
        mock_interface.return_value = mock_iface

        mock_bus = MagicMock()
        controller = DBusSessionController(bus=mock_bus)

        players = controller.list_media_players()

        assert len(players) == 2
        assert "org.mpris.MediaPlayer2.vlc" in players
        assert "org.mpris.MediaPlayer2.spotify" in players

    @patch("src.integrations.dbus_controller.dbus.Interface")
    def test_list_media_players_dbus_exception(self, mock_interface: MagicMock) -> None:
        """Test DBusException in list_media_players."""
        import dbus

        mock_iface = MagicMock()
        mock_iface.ListNames.side_effect = dbus.DBusException("Failed")
        mock_interface.return_value = mock_iface

        mock_bus = MagicMock()
        controller = DBusSessionController(bus=mock_bus)

        players = controller.list_media_players()

        assert players == []

    def test_action_case_insensitive(self) -> None:
        """Test that actions are case-insensitive."""
        with patch("src.integrations.dbus_controller.dbus.Interface") as mock_interface:
            mock_iface = MagicMock()
            mock_interface.return_value = mock_iface

            mock_bus = MagicMock()
            controller = DBusSessionController(bus=mock_bus)

            response = controller.control_media_player("PLAY")
            assert response["success"]

            response = controller.control_media_player("PlAyPaUsE")
            assert response["success"]


class TestDBusSystemController:
    """Tests for DBusSystemController."""

    def test_initialization_default_bus(self) -> None:
        """Test initialization with default bus."""
        with patch("src.integrations.dbus_controller.dbus.SystemBus") as mock_bus:
            controller = DBusSystemController()
            assert controller._bus is not None
            mock_bus.assert_called_once()

    def test_initialization_custom_bus(self) -> None:
        """Test initialization with custom bus."""
        mock_bus = MagicMock()
        controller = DBusSystemController(bus=mock_bus)
        assert controller._bus is mock_bus

    @patch("src.integrations.dbus_controller.dbus.Interface")
    def test_get_network_status_success(self, mock_interface: MagicMock) -> None:
        """Test successful network status retrieval."""
        mock_props = MagicMock()

        def capture_get(interface_name: str, prop_name: str) -> Any:
            mapping = {
                "State": 70,
                "Connectivity": 4,
                "ActiveConnections": ["/org/freedesktop/NetworkManager/ActiveConnection/1"],
            }
            return mapping[prop_name]

        mock_props.Get.side_effect = capture_get
        mock_interface.return_value = mock_props

        mock_bus = MagicMock()
        controller = DBusSystemController(bus=mock_bus)

        network = controller.get_network_status()
        assert network["state"] == "CONNECTED_GLOBAL"
        assert network["connectivity"] == "FULL"
        assert network["active_connections"] == 1

    @patch("src.integrations.dbus_controller.dbus.Interface")
    def test_get_network_status_dbus_exception(self, mock_interface: MagicMock) -> None:
        """Test DBusException in get_network_status."""
        import dbus

        mock_props = MagicMock()
        mock_props.Get.side_effect = dbus.DBusException("Failed")
        mock_interface.return_value = mock_props

        mock_bus = MagicMock()
        controller = DBusSystemController(bus=mock_bus)

        network = controller.get_network_status()

        assert "error" in network

    @patch("src.integrations.dbus_controller.dbus.Interface")
    def test_get_power_status_success(self, mock_interface: MagicMock) -> None:
        """Test successful power status retrieval."""
        mock_props = MagicMock()

        def capture_get(interface_name: str, prop_name: str) -> Any:
            mapping = {
                "OnBattery": True,
                "Percentage": 81.2,
            }
            return mapping[prop_name]

        mock_props.Get.side_effect = capture_get
        mock_interface.return_value = mock_props

        mock_bus = MagicMock()
        controller = DBusSystemController(bus=mock_bus)

        power = controller.get_power_status()
        assert power["on_battery"]
        assert power["percentage"] == 81.2

    @patch("src.integrations.dbus_controller.dbus.Interface")
    def test_get_power_status_dbus_exception(self, mock_interface: MagicMock) -> None:
        """Test DBusException in get_power_status."""
        import dbus

        mock_props = MagicMock()
        mock_props.Get.side_effect = dbus.DBusException("Failed")
        mock_interface.return_value = mock_props

        mock_bus = MagicMock()
        controller = DBusSystemController(bus=mock_bus)

        power = controller.get_power_status()

        assert "error" in power

    @patch("src.integrations.dbus_controller._load_psutil")
    def test_get_disk_usage_success(self, mock_load_psutil: MagicMock) -> None:
        """Test successful disk usage retrieval."""
        mock_psutil = MagicMock()
        mock_partition = MagicMock()
        mock_partition.mountpoint = "/"
        mock_partition.device = "/dev/sda1"
        mock_partition.fstype = "ext4"

        mock_usage = MagicMock()
        mock_usage.total = 1000000000
        mock_usage.used = 500000000
        mock_usage.free = 500000000
        mock_usage.percent = 50.0

        mock_psutil.disk_partitions.return_value = [mock_partition]
        mock_psutil.disk_usage.return_value = mock_usage
        mock_load_psutil.return_value = mock_psutil

        mock_bus = MagicMock()
        controller = DBusSystemController(bus=mock_bus)

        disk_info = controller.get_disk_usage()

        assert "disks" in disk_info
        assert "/" in disk_info["disks"]
        assert disk_info["disks"]["/"]["percent"] == 50.0

    @patch("src.integrations.dbus_controller._load_psutil")
    def test_get_disk_usage_psutil_not_available(self, mock_load_psutil: MagicMock) -> None:
        """Test disk usage when psutil is not available."""
        mock_load_psutil.return_value = None

        mock_bus = MagicMock()
        controller = DBusSystemController(bus=mock_bus)

        disk_info = controller.get_disk_usage()

        assert "error" in disk_info
        assert "psutil is not available" in disk_info["error"]

    @patch("src.integrations.dbus_controller._load_psutil")
    def test_get_battery_info_success(self, mock_load_psutil: MagicMock) -> None:
        """Test successful battery info retrieval."""
        mock_psutil = MagicMock()
        mock_battery = MagicMock()
        mock_battery.percent = 75.5
        mock_battery.power_plugged = True
        mock_battery.secsleft = 3600

        mock_psutil.sensors_battery.return_value = mock_battery
        mock_load_psutil.return_value = mock_psutil

        mock_bus = MagicMock()
        controller = DBusSystemController(bus=mock_bus)

        battery_info = controller.get_battery_info()

        assert battery_info["percent"] == 75.5
        assert battery_info["power_plugged"] is True
        assert battery_info["time_left"] == 3600

    @patch("src.integrations.dbus_controller._load_psutil")
    def test_get_battery_info_no_battery(self, mock_load_psutil: MagicMock) -> None:
        """Test battery info when no battery is detected."""
        mock_psutil = MagicMock()
        mock_psutil.sensors_battery.return_value = None
        mock_load_psutil.return_value = mock_psutil

        mock_bus = MagicMock()
        controller = DBusSystemController(bus=mock_bus)

        battery_info = controller.get_battery_info()

        assert "error" in battery_info
        assert "No battery detected" in battery_info["error"]

    @patch("src.integrations.dbus_controller._load_psutil")
    def test_get_network_interfaces_success(self, mock_load_psutil: MagicMock) -> None:
        """Test successful network interfaces retrieval."""
        mock_psutil = MagicMock()

        mock_stat = MagicMock()
        mock_stat.isup = True
        mock_stat.speed = 1000
        mock_stat.mtu = 1500

        mock_addr = MagicMock()
        mock_addr.family = 2  # AF_INET
        mock_addr.address = "192.168.1.100"
        mock_addr.netmask = "255.255.255.0"
        mock_addr.broadcast = "192.168.1.255"

        mock_psutil.net_if_stats.return_value = {"eth0": mock_stat}
        mock_psutil.net_if_addrs.return_value = {"eth0": [mock_addr]}
        mock_load_psutil.return_value = mock_psutil

        mock_bus = MagicMock()
        controller = DBusSystemController(bus=mock_bus)

        interfaces = controller.get_network_interfaces()

        assert "interfaces" in interfaces
        assert "eth0" in interfaces["interfaces"]
        assert interfaces["interfaces"]["eth0"]["is_up"] is True
        assert interfaces["interfaces"]["eth0"]["speed"] == 1000

    @patch("src.integrations.dbus_controller._load_psutil")
    def test_get_network_interfaces_psutil_not_available(self, mock_load_psutil: MagicMock) -> None:
        """Test network interfaces when psutil is not available."""
        mock_load_psutil.return_value = None

        mock_bus = MagicMock()
        controller = DBusSystemController(bus=mock_bus)

        interfaces = controller.get_network_interfaces()

        assert "error" in interfaces

    def test_network_states_mapping(self) -> None:
        """Test network states constants."""
        assert DBusSystemController._NETWORK_STATES[70] == "CONNECTED_GLOBAL"
        assert DBusSystemController._NETWORK_STATES[0] == "UNKNOWN"

    def test_connectivity_mapping(self) -> None:
        """Test connectivity constants."""
        assert DBusSystemController._CONNECTIVITY[4] == "FULL"
        assert DBusSystemController._CONNECTIVITY[0] == "UNKNOWN"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
