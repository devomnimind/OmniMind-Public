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

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Protocol, cast

import dbus  # type: ignore  # external library without stubs

logger = logging.getLogger(__name__)


class _PsutilInterface(Protocol):
    def disk_partitions(self) -> list[Any]: ...

    def disk_usage(self, path: str) -> Any: ...

    def sensors_battery(self) -> Any: ...

    def net_if_stats(self) -> dict[str, Any]: ...

    def net_if_addrs(self) -> dict[str, list[Any]]: ...


def _load_psutil() -> Optional[_PsutilInterface]:
    try:
        import psutil

        return cast(_PsutilInterface, psutil)
    except ImportError:
        return None


class DBusSessionController:
    _ACTION_MAP = {
        "play": "Play",
        "pause": "Pause",
        "playpause": "PlayPause",
        "next": "Next",
        "previous": "Previous",
        "stop": "Stop",
    }

    def __init__(self, bus: Optional[Any] = None) -> None:
        self._bus = bus or dbus.SessionBus()

    def control_media_player(
        self, action: str, player_bus_name: str = "org.mpris.MediaPlayer2.vlc"
    ) -> Dict[str, Any]:
        action_key = action.lower().strip()
        method_name = self._ACTION_MAP.get(action_key)
        if not method_name:
            return {"success": False, "error": f"Unsupported action {action}"}
        try:
            proxy = self._bus.get_object(player_bus_name, "/org/mpris/MediaPlayer2")
            interface = dbus.Interface(proxy, "org.mpris.MediaPlayer2.Player")
            getattr(interface, method_name)()
            return {
                "success": True,
                "player": player_bus_name,
                "action": action_key,
            }
        except dbus.DBusException as exc:
            logger.warning("Failed to control media player %s: %s", player_bus_name, exc)
            return {"success": False, "error": str(exc)}
        except AttributeError as exc:
            return {"success": False, "error": str(exc)}

    def list_media_players(self) -> List[str]:
        try:
            proxy = self._bus.get_object("org.freedesktop.DBus", "/org/freedesktop/DBus")
            interface = dbus.Interface(proxy, "org.freedesktop.DBus")
            names = interface.ListNames()
            return [n for n in names if n.startswith("org.mpris.MediaPlayer2.")]
        except dbus.DBusException as exc:
            logger.debug("Unable to list media players: %s", exc)
            return []


class DBusSystemController:
    _NETWORK_STATES = {
        0: "UNKNOWN",
        10: "ASLEEP",
        20: "DISCONNECTED",
        30: "DISCONNECTING",
        40: "CONNECTING",
        50: "CONNECTED_LOCAL",
        60: "CONNECTED_SITE",
        70: "CONNECTED_GLOBAL",
    }
    _CONNECTIVITY = {
        0: "UNKNOWN",
        1: "NONE",
        2: "PORTAL",
        3: "LIMITED",
        4: "FULL",
    }

    def __init__(self, bus: Optional[Any] = None) -> None:
        self._bus = bus or dbus.SystemBus()

    def get_network_status(self) -> Dict[str, Any]:
        try:
            proxy = self._bus.get_object(
                "org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager"
            )
            props = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
            state = int(props.Get("org.freedesktop.NetworkManager", "State"))
            connectivity = int(props.Get("org.freedesktop.NetworkManager", "Connectivity"))
            connections = props.Get("org.freedesktop.NetworkManager", "ActiveConnections")
            return {
                "state": self._NETWORK_STATES.get(state, "UNKNOWN"),
                "connectivity": self._CONNECTIVITY.get(connectivity, "UNKNOWN"),
                "active_connections": len(connections) if connections else 0,
            }
        except dbus.DBusException as exc:
            logger.debug("NetworkManager query failed: %s", exc)
            return {"error": str(exc)}

    def get_power_status(self) -> Dict[str, Any]:
        try:
            proxy = self._bus.get_object("org.freedesktop.UPower", "/org/freedesktop/UPower")
            props = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
            on_battery = bool(props.Get("org.freedesktop.UPower", "OnBattery"))
            percentage = float(props.Get("org.freedesktop.UPower", "Percentage"))
            return {"on_battery": on_battery, "percentage": percentage}
        except dbus.DBusException as exc:
            logger.debug("UPower query failed: %s", exc)
            return {"error": str(exc)}

    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information from UDisks2.

        Returns:
            Dictionary with disk usage information
        """
        try:
            psutil_module = _load_psutil()
            if psutil_module is None:
                return {"error": "psutil is not available"}

            disk_info = {}
            for partition in psutil_module.disk_partitions():
                try:
                    usage = psutil_module.disk_usage(partition.mountpoint)
                    disk_info[partition.mountpoint] = {
                        "device": partition.device,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent,
                    }
                except PermissionError:
                    continue

            return {"disks": disk_info, "timestamp": __import__("time").time()}

        except Exception as exc:
            logger.debug(f"Disk usage query failed: {exc}")
            return {"error": str(exc)}

    def get_battery_info(self) -> Dict[str, Any]:
        """Get detailed battery information.

        Returns:
            Dictionary with battery information
        """
        try:
            psutil_module = _load_psutil()
            if psutil_module is None:
                return {"error": "psutil is not available"}

            battery = psutil_module.sensors_battery()
            if battery is None:
                return {"error": "No battery detected"}

            return {
                "percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "time_left": battery.secsleft if battery.secsleft != -1 else None,
                "timestamp": __import__("time").time(),
            }

        except Exception as exc:
            logger.debug(f"Battery info query failed: {exc}")
            return {"error": str(exc)}

    def get_network_interfaces(self) -> Dict[str, Any]:
        """Get network interface information.

        Returns:
            Dictionary with network interface details
        """
        try:
            psutil_module = _load_psutil()
            if psutil_module is None:
                return {"error": "psutil is not available"}

            interfaces = {}
            stats = psutil_module.net_if_stats()
            addrs = psutil_module.net_if_addrs()

            for iface_name, iface_stats in stats.items():
                addresses: list[Dict[str, Any]] = []
                interface_info = {
                    "is_up": iface_stats.isup,
                    "speed": iface_stats.speed,
                    "mtu": iface_stats.mtu,
                    "addresses": addresses,
                }

                # Add addresses if available
                if iface_name in addrs:
                    for addr in addrs[iface_name]:
                        addresses.append(
                            {
                                "family": str(addr.family),
                                "address": addr.address,
                                "netmask": addr.netmask,
                                "broadcast": addr.broadcast,
                            }
                        )

                interfaces[iface_name] = interface_info

            return {"interfaces": interfaces, "timestamp": __import__("time").time()}

        except Exception as exc:
            logger.debug(f"Network interfaces query failed: {exc}")
            return {"error": str(exc)}

    def get_system_services_status(self) -> Dict[str, Any]:
        """Get status of system services via systemd.

        Returns:
            Dictionary with service statuses
        """
        try:
            proxy = self._bus.get_object("org.freedesktop.systemd1", "/org/freedesktop/systemd1")
            manager = dbus.Interface(proxy, "org.freedesktop.systemd1.Manager")

            # Get list of units
            units = manager.ListUnits()

            services = {}
            for unit in units:
                unit_name, description, load_state, active_state, sub_state = (
                    unit[0],
                    unit[1],
                    unit[2],
                    unit[3],
                    unit[4],
                )

                # Only include service units
                if unit_name.endswith(".service"):
                    services[unit_name] = {
                        "description": description,
                        "load_state": load_state,
                        "active_state": active_state,
                        "sub_state": sub_state,
                    }

            return {"services": services, "timestamp": __import__("time").time()}

        except dbus.DBusException as exc:
            logger.debug(f"systemd query failed: {exc}")
            return {"error": str(exc)}

    def send_notification(self, summary: str, body: str, urgency: int = 1) -> Dict[str, Any]:
        """Send desktop notification via D-Bus.

        Args:
            summary: Notification title
            body: Notification body
            urgency: Urgency level (0=low, 1=normal, 2=critical)

        Returns:
            Notification result
        """
        try:
            # Get session bus for notifications
            session_bus = dbus.SessionBus()
            proxy = session_bus.get_object(
                "org.freedesktop.Notifications", "/org/freedesktop/Notifications"
            )
            notifications = dbus.Interface(proxy, "org.freedesktop.Notifications")

            # Send notification
            notification_id = notifications.Notify(
                "OmniMind",  # app_name
                0,  # replaces_id (0 = new notification)
                "",  # app_icon
                summary,
                body,
                [],  # actions
                {"urgency": dbus.Byte(urgency)},  # hints
                -1,  # timeout (-1 = default)
            )

            return {"success": True, "notification_id": int(notification_id)}

        except dbus.DBusException as exc:
            logger.warning(f"Notification failed: {exc}")
            return {"success": False, "error": str(exc)}
