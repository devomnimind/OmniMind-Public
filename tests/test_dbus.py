from unittest.mock import MagicMock, patch

from src.integrations.dbus_controller import DBusSessionController, DBusSystemController


@patch("src.integrations.dbus_controller.dbus.Interface")
def test_session_controller_controls_player(mock_interface):
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


@patch("src.integrations.dbus_controller.dbus.Interface")
def test_system_controller_reports_status(mock_interface):
    mock_props = MagicMock()

    def capture_get(interface_name, prop_name):
        mapping = {
            "State": 70,
            "Connectivity": 4,
            "ActiveConnections": ["/org/freedesktop/NetworkManager/ActiveConnection/1"],
            "OnBattery": True,
            "Percentage": 81.2,
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

    power = controller.get_power_status()
    assert power["on_battery"]
    assert power["percentage"] == 81.2
