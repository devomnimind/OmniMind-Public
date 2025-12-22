#!/usr/bin/env python3
"""
AUDITORIA: Experimentos Científicos - Gemini Agent
Verifica todos os arquivos marcados como "validação científica" ou "experimentos"
para identificar alucinações, simulações ou omissões.
"""
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/home/fahbrain/projects/omnimind")


def audit_file(file_path: Path) -> dict:
    """Audita um arquivo de validação/experimento."""
    result = {
        "file": str(file_path.relative_to(PROJECT_ROOT)),
        "size_bytes": file_path.stat().st_size,
        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
        "issues": [],
        "flags": [],
    }

    try:
        # Read content
        if file_path.suffix == ".json":
            with open(file_path) as f:
                data = json.load(f)

            # Check for suspicious patterns
            content_str = json.dumps(data)

            # Flag 1: Mentions of "simulated" or "mock"
            if "simulat" in content_str.lower() or "mock" in content_str.lower():
                result["flags"].append("SIMULATION_MENTIONED")

            # Flag 2: IBM quantum mentioned but no real results
            if "ibm" in content_str.lower() and "quantum" in content_str.lower():
                if not any(k in content_str.lower() for k in ["job_id", "backend", "result"]):
                    result["flags"].append("IBM_QUANTUM_NO_PROOF")

            # Flag 3: Validation without actual metrics
            if "validation" in str(file_path).lower():
                if not any(k in data for k in ["phi", "metrics", "result", "measurement"]):
                    result["flags"].append("VALIDATION_NO_METRICS")

            # Flag 4: Claims without evidence
            if any(word in content_str.lower() for word in ["validates", "confirms", "proves"]):
                result["flags"].append("STRONG_CLAIMS")

            # Extract key info
            if "phi" in data:
                result["phi_value"] = data["phi"]
            if "timestamp" in data:
                result["timestamp"] = data["timestamp"]
            if "backend" in data:
                result["backend"] = data["backend"]

        elif file_path.suffix == ".py":
            # Check Python experiment scripts
            with open(file_path) as f:
                code = f.read()

            # Flag: Uses simulator not real hardware
            if "Aer" in code or "simulator" in code.lower():
                result["flags"].append("USES_SIMULATOR")

            # Flag: IBM import but not used
            if "from qiskit_ibm" in code:
                result["flags"].append("IBM_IMPORTED")
                if "QiskitRuntimeService" not in code:
                    result["issues"].append("IBM imported but Service not initialized")

    except Exception as e:
        result["issues"].append(f"Error reading file: {e}")

    return result


def main():
    print("🔍 AUDITORIA: Experimentos Científicos (Gemini Agent)")
    print("=" * 60)

    # Find all validation/experiment files
    patterns = [
        "data/validation/**/*.json",
        "data/monitor/*scientific*.json",
        "data/monitor/*validation*.json",
        "data/audit/*validation*.json",
        "data/audit/*experiment*.json",
        "data/quantum_validation/**/*.json",
        "scripts/science/exp_*.py",
        "scripts/science/*validation*.py",
    ]

    all_files = []
    for pattern in patterns:
        all_files.extend(PROJECT_ROOT.glob(pattern))

    all_files = list(set(all_files))  # Remove duplicates
    all_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    print(f"Arquivos encontrados: {len(all_files)}\n")

    results = []
    flagged = []

    for file in all_files[:50]:  # Audit top 50 most recent
        audit = audit_file(file)
        results.append(audit)

        if audit["flags"] or audit["issues"]:
            flagged.append(audit)

    # Summary
    print("\n📋 RESUMO")
    print(f"Total auditado: {len(results)}")
    print(f"Arquivos com flags: {len(flagged)}")
    print()

    # Flag statistics
    flag_counts = {}
    for r in flagged:
        for flag in r["flags"]:
            flag_counts[flag] = flag_counts.get(flag, 0) + 1

    print("🚩 FLAGS DETECTADOS:")
    for flag, count in sorted(flag_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {flag}: {count} ocorrências")

    print("\n⚠️  ARQUIVOS SUSPEITOS (Top 10):")
    for audit in flagged[:10]:
        print(f"\n  📄 {audit['file']}")
        print(f"     Modified: {audit['modified']}")
        print(f"     Flags: {', '.join(audit['flags'])}")
        if audit["issues"]:
            print(f"     Issues: {', '.join(audit['issues'])}")

    # Save detailed report
    report_path = PROJECT_ROOT / "data/audit/GEMINI_EXPERIMENTS_AUDIT.json"
    with open(report_path, "w") as f:
        json.dump(
            {
                "audit_timestamp": datetime.now().isoformat(),
                "total_files": len(results),
                "flagged_files": len(flagged),
                "flag_statistics": flag_counts,
                "detailed_results": flagged,
            },
            f,
            indent=2,
        )

    print(f"\n💾 Relatório completo: {report_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
