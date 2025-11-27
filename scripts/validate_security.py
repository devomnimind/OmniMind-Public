from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from src.audit.immutable_audit import get_audit_system
from src.security.dlp import DLPValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("immunity-p0.validation")


def check_audit_chain() -> Dict[str, object]:
    audit = get_audit_system()
    summary = audit.verify_chain_integrity()
    logger.info("Audit chain validity: %s", summary.get("valid"))
    return summary


def check_dlp() -> Dict[str, str]:
    policy_file = os.environ.get("OMNIMIND_DLP_POLICY_FILE", "config/dlp_policies.yaml")
    validator = DLPValidator(policy_path=policy_file)
    policies = [policy.name for policy in validator.policies]
    logger.info("DLP policies loaded: %s", policies)
    return {"policies": policies}


def check_sandbox_artifacts() -> Dict[str, str]:
    kernel = os.environ.get("OMNIMIND_FIRECRACKER_KERNEL", "/opt/firecracker/vmlinux.bin")
    rootfs = os.environ.get("OMNIMIND_FIRECRACKER_ROOTFS", "/opt/firecracker/rootfs.ext4")
    kernel_exists = os.path.exists(kernel)
    rootfs_exists = os.path.exists(rootfs)
    logger.info("Sandbox assets kernel=%s rootfs=%s", kernel_exists, rootfs_exists)
    return {
        "kernel": kernel,
        "kernel_exists": kernel_exists,
        "rootfs": rootfs,
        "rootfs_exists": rootfs_exists,
    }


def main() -> None:
    now = datetime.now(timezone.utc)
    logger.info("Security validation started at %s", now.isoformat())
    audit_result = check_audit_chain()
    dlp_result = check_dlp()
    sandbox_result = check_sandbox_artifacts()
    output = {
        "timestamp": now.isoformat(),
        "audit": audit_result,
        "dlp": dlp_result,
        "sandbox": sandbox_result,
    }
    log_path = Path(
        os.environ.get("OMNIMIND_SECURITY_VALIDATION_LOG", "logs/security_validation.jsonl")
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(output, ensure_ascii=False) + "\n")
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
