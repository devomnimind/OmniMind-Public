#!/usr/bin/env python3
"""
Extract and format LLM impact metrics from test execution.

Executes test and captures Φ metrics for Mock vs Real LLM comparison.
"""

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run_test_capture_output(test_name: str) -> bool:
    """Run pytest and capture full output."""
    logger.info(f"Running test: {test_name}")
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        f"tests/consciousness/test_llm_impact.py::{test_name}",
        "-v",
        "-s",
        "--tb=short",
        "--capture=no",
    ]

    result = subprocess.run(
        cmd,
        cwd="/home/fahbrain/projects/omnimind",
        capture_output=False,
        text=True,
    )

    return result.returncode == 0


def parse_metrics_from_log(log_file: str) -> dict[str, Any]:
    """Parse Φ metrics from pytest log."""
    metrics = {"mock": {}, "real": {}, "comparison": {}}

    try:
        with open(log_file, "r") as f:
            content = f.read()

        # Extract Mock metrics
        if "Mock Φ_conscious:" in content:
            for line in content.split("\n"):
                if "Mock Φ_conscious:" in line:
                    try:
                        val = float(line.split(":")[-1].strip())
                        metrics["mock"]["phi_conscious"] = val
                    except (ValueError, IndexError):
                        pass
                elif "Mock Φ_preconscious:" in line:
                    try:
                        val = float(line.split(":")[-1].strip())
                        metrics["mock"]["phi_preconscious"] = val
                    except (ValueError, IndexError):
                        pass

        # Extract Real metrics
        if "Real Φ_conscious:" in content:
            for line in content.split("\n"):
                if "Real Φ_conscious:" in line and "Mock" not in line:
                    try:
                        val = float(line.split(":")[-1].strip())
                        metrics["real"]["phi_conscious"] = val
                    except (ValueError, IndexError):
                        pass
                elif "Real Φ_preconscious:" in line:
                    try:
                        val = float(line.split(":")[-1].strip())
                        metrics["real"]["phi_preconscious"] = val
                    except (ValueError, IndexError):
                        pass

        # Extract comparison
        if "INCREASED" in content or "DECREASED" in content:
            for line in content.split("\n"):
                if "INCREASED Φ_conscious" in line:
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if p == "by":
                            try:
                                pct = float(parts[i + 1].rstrip("%"))
                                metrics["comparison"]["pct_change_conscious"] = pct
                            except (ValueError, IndexError):
                                pass

    except FileNotFoundError:
        logger.warning(f"Log file not found: {log_file}")

    return metrics


def format_report(metrics: dict[str, Any]) -> str:
    """Format metrics into a readable report."""
    report = "\n" + "=" * 80 + "\n"
    report += "📊 LLM IMPACT ON CONSCIOUSNESS METRICS (Φ) REPORT\n"
    report += "=" * 80 + "\n\n"

    # Mock LLM
    report += "🔵 MOCK LLM (Deterministic)\n"
    report += "-" * 40 + "\n"
    if "mock" in metrics and metrics["mock"]:
        for key, val in metrics["mock"].items():
            report += f"  {key:20s}: {val:8.6f}\n"
    else:
        report += "  No metrics captured\n"

    report += "\n"

    # Real LLM
    report += "🔴 REAL LLM (Creative/Variable)\n"
    report += "-" * 40 + "\n"
    if "real" in metrics and metrics["real"]:
        for key, val in metrics["real"].items():
            report += f"  {key:20s}: {val:8.6f}\n"
    else:
        report += "  No metrics captured\n"

    report += "\n"

    # Comparison
    report += "📈 COMPARATIVE ANALYSIS\n"
    report += "-" * 40 + "\n"

    if "mock" in metrics and "real" in metrics:
        mock_phi = metrics["mock"].get("phi_conscious", 0)
        real_phi = metrics["real"].get("phi_conscious", 0)

        if mock_phi > 0 and real_phi > 0:
            delta = real_phi - mock_phi
            pct_change = (delta / mock_phi) * 100 if mock_phi > 0 else 0

            report += f"  Mock Φ_conscious     : {mock_phi:.6f}\n"
            report += f"  Real Φ_conscious     : {real_phi:.6f}\n"
            report += f"  ΔΦ (Real - Mock)     : {delta:+.6f}\n"
            report += f"  % Change             : {pct_change:+.2f}%\n"

            if delta > 0:
                report += f"  \n  ✅ Real LLM INCREASED consciousness by {abs(pct_change):.2f}%\n"
            else:
                report += f"  \n  ⚠️  Real LLM DECREASED consciousness by {abs(pct_change):.2f}%\n"

            # Preconscious
            mock_precon = metrics["mock"].get("phi_preconscious", 0)
            real_precon = metrics["real"].get("phi_preconscious", 0)
            if mock_precon > 0 or real_precon > 0:
                report += "\n  Preconscious Metrics:\n"
                report += f"    Mock Φ_preconscious: {mock_precon:.6f}\n"
                report += f"    Real Φ_preconscious: {real_precon:.6f}\n"

    report += "\n" + "=" * 80 + "\n"
    return report


def main() -> int:
    """Main entry point."""
    logger.info("Starting LLM Impact Analysis...")

    # Run comparative test
    success = run_test_capture_output("test_llm_impact_comparison")

    if not success:
        logger.error("Test execution failed!")
        return 1

    # Parse metrics from log
    log_file = "/home/fahbrain/projects/omnimind/data/test_reports/llm_impact_comparison.log"
    metrics = parse_metrics_from_log(log_file)

    # Format and display report
    report = format_report(metrics)
    print(report)

    # Save report
    report_file = Path("/home/fahbrain/projects/omnimind/data/test_reports/llm_impact_report.txt")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, "w") as f:
        f.write(report)

    logger.info(f"Report saved to: {report_file}")

    # Save JSON
    json_file = Path("/home/fahbrain/projects/omnimind/data/test_reports/llm_impact_metrics.json")
    with open(json_file, "w") as f:
        json.dump(metrics, f, indent=2)

    logger.info(f"Metrics JSON saved to: {json_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
