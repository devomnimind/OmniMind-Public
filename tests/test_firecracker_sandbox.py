from pathlib import Path
from typing import Any, Dict
from src.security.firecracker_sandbox import FirecrackerSandbox

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


def test_sandbox_disabled_without_artifacts(tmp_path: Path) -> None:
    sandbox: FirecrackerSandbox = FirecrackerSandbox(
        kernel_path=None, rootfs_path=None, enabled=True
    )
    payload: Dict[str, Any] = {"task": "critical"}
    result = sandbox.run(payload)
    assert not result.success
    assert "unavailable" in result.output.lower()


def test_sandbox_executes_with_dummy_images(tmp_path: Path) -> None:
    kernel = tmp_path / "vmlinux.bin"
    rootfs = tmp_path / "rootfs.ext4"
    kernel.write_text("kernel")
    rootfs.write_text("rootfs")
    sandbox = FirecrackerSandbox(kernel_path=str(kernel), rootfs_path=str(rootfs))
    payload: Dict[str, Any] = {"task": "critical", "plan": "firecracker"}
    result = sandbox.run(payload, sandbox_name="testsandbox")
    assert result.success
    assert result.sandbox == "testsandbox"
    assert result.metadata.get("payload_summary")
