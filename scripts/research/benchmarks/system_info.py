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

import json
import os
import platform
from datetime import UTC, datetime

import psutil


def gather_system_info() -> dict:
    uname = platform.uname()
    boot = datetime.fromtimestamp(psutil.boot_time()).isoformat()
    cpu_freq = psutil.cpu_freq()
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "os": {
            "system": uname.system,
            "node": uname.node,
            "release": uname.release,
            "version": uname.version,
            "machine": uname.machine,
            "processor": uname.processor,
        },
        "cpu": {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "frequency": {
                "current_mhz": cpu_freq.current if cpu_freq else None,
                "min_mhz": cpu_freq.min if cpu_freq else None,
                "max_mhz": cpu_freq.max if cpu_freq else None,
            },
            "architecture": platform.machine(),
        },
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "used": psutil.virtual_memory().used,
            "percent": psutil.virtual_memory().percent,
        },
        "swap": {
            "total": psutil.swap_memory().total,
            "used": psutil.swap_memory().used,
            "percent": psutil.swap_memory().percent,
        },
        "disk": [
            {
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent,
            }
            for part in psutil.disk_partitions(all=False)
            for usage in [psutil.disk_usage(part.mountpoint)]
        ],
        "network": {
            iface: {
                "isup": nic.isup,
                "speed": nic.speed,
                "mtu": nic.mtu,
                "addresses": [
                    {
                        "family": addr.family.name,
                        "address": addr.address,
                    }
                    for addr in addrs
                ],
            }
            for iface, addrs in psutil.net_if_addrs().items()
            if (nic := psutil.net_if_stats().get(iface))
        },
        "uptime": boot,
    }


def main() -> None:
    data = gather_system_info()
    os.makedirs("docs/reports/benchmarks", exist_ok=True)
    with open("docs/reports/hardware_audit.json", "w", encoding="utf-8") as stream:
        json.dump({"system_info": data}, stream, indent=2)


if __name__ == "__main__":
    main()
