from pathlib import Path
from typing import Any, Dict

from src.security.firecracker_sandbox import FirecrackerSandbox


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
