import os
import sys
import json
import subprocess
import pkg_resources
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configuration
PROJECT_ROOT = Path("/home/fahbrain/projects/omnimind")
LOG_DIR = PROJECT_ROOT / "logs"
OUTPUT_DIR = PROJECT_ROOT / "data/audit_p0"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def run_command(command: str) -> str:
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

def audit_dependencies() -> Dict[str, Any]:
    print("Auditing dependencies...")
    report = {"outdated": [], "integrity": {}, "missing": []}

    # Check outdated
    outdated = run_command("pip list --outdated --format=json")
    try:
        report["outdated"] = json.loads(outdated)
    except:
        report["outdated"] = "Could not parse pip list output"

    # Check key packages
    key_packages = ["qiskit", "dwave-ocean-sdk", "protobuf", "torch"]
    installed = {p.key: p.version for p in pkg_resources.working_set}

    for pkg in key_packages:
        if pkg in installed:
            report["integrity"][pkg] = {"status": "installed", "version": installed[pkg]}
        else:
            report["integrity"][pkg] = {"status": "missing"}

    return report

def audit_services() -> Dict[str, Any]:
    print("Auditing services...")
    services = {
        "observer": False,
        "auditor": False,
        "replay": False,
        "frontend": False,
        "backend": False
    }

    ps_output = run_command("ps aux")
    for line in ps_output.splitlines():
        if "observer_service.py" in line: services["observer"] = True
        if "external_auditor" in line: services["auditor"] = True
        if "replay_service" in line: services["replay"] = True
        if "vite" in line: services["frontend"] = True
        if "uvicorn" in line: services["backend"] = True

    return services

def audit_logs() -> Dict[str, Any]:
    print("Auditing logs...")
    errors = []
    warnings = []

    # Scan last 48h logs (simplified to checking file modification time)
    cutoff = datetime.now() - timedelta(hours=48)

    for log_file in LOG_DIR.glob("**/*.log"):
        if log_file.stat().st_mtime > cutoff.timestamp():
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        if "ERROR" in line or "Exception" in line:
                            errors.append({"file": log_file.name, "line": line.strip()})
                        if "WARNING" in line:
                            warnings.append({"file": log_file.name, "line": line.strip()})
            except Exception as e:
                print(f"Could not read {log_file}: {e}")

    return {"error_count": len(errors), "warning_count": len(warnings), "errors": errors[:50]}

def audit_security() -> Dict[str, Any]:
    print("Auditing security placeholders...")
    placeholders = ["TODO", "FIXME", "PASSWORD", "API_KEY", "MOCK", "TEST_USER"]
    findings = []

    for ext in ["py", "ts", "tsx", "js"]:
        for file_path in PROJECT_ROOT.rglob(f"*.{ext}"):
            if "node_modules" in str(file_path) or ".venv" in str(file_path):
                continue

            try:
                with open(file_path, 'r') as f:
                    for i, line in enumerate(f, 1):
                        for p in placeholders:
                            if p in line:
                                findings.append({
                                    "file": str(file_path.relative_to(PROJECT_ROOT)),
                                    "line": i,
                                    "type": p,
                                    "content": line.strip()
                                })
            except:
                pass

    return findings

def main():
    audit_data = {
        "timestamp": datetime.now().isoformat(),
        "dependencies": audit_dependencies(),
        "services": audit_services(),
        "logs": audit_logs(),
        "security": audit_security()
    }

    output_file = OUTPUT_DIR / "audit_report_raw.json"
    with open(output_file, 'w') as f:
        json.dump(audit_data, f, indent=2)

    print(f"Audit complete. Data saved to {output_file}")

if __name__ == "__main__":
    main()
