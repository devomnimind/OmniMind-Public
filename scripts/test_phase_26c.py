#!/usr/bin/env python3
"""Test Phase 26C - Autonomous Adaptation Framework

Quick validation script to test all components.

Author: OmniMind Development
License: MIT
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "src"))

from autonomous.autonomous_loop import OmniMindAutonomousLoop
from autonomous.problem_detection_engine import ProblemDetectionEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


async def test_autonomous_loop():
    """Test autonomous loop for a short period"""
    print("\n" + "=" * 60)
    print("🧠 PHASE 26C: AUTONOMOUS ADAPTATION FRAMEWORK")
    print("=" * 60 + "\n")

    loop = OmniMindAutonomousLoop()

    # Test 1: System state detection
    print("📊 Test 1: System State Detection")
    state = loop.get_system_state()
    print(f"   ✅ CPU: {state.cpu_percent:.1f}%")
    print(
        f"   ✅ Memory: {state.memory_percent:.1f}% ({state.memory_available_gb:.2f}GB available)"
    )
    print(f"   ✅ GPU: {state.gpu_count} devices")
    if state.gpu_memory_percent:
        print(f"   ✅ GPU Memory: {state.gpu_memory_percent:.1f}%")
    print()

    # Test 2: Problem detection
    print("🔍 Test 2: Problem Detection")
    detector = ProblemDetectionEngine()
    issues = detector.detect_issues(state)
    if issues:
        print(f"   ⚠️  {len(issues)} issues detected:")
        for issue in issues[:3]:  # Show first 3
            print(f"      - {issue.type} ({issue.severity}): {issue.description}")
    else:
        print("   ✅ No issues detected (system healthy)")
    print()

    # Test 3: Solution lookup
    print("🔎 Test 3: Solution Lookup")
    solver = loop.solver
    if issues:
        issue_dict = {
            "type": issues[0].type,
            "description": issues[0].description,
            "severity": issues[0].severity,
        }
        solution = solver.find_solution(issue_dict)
        print(f"   ✅ Source: {solution.get('source', 'N/A')}")
        print(f"   ✅ Confidence: {solution.get('confidence', 0):.2f}")
    else:
        print("   ℹ️  No issues to solve")
    print()

    # Test 4: Framework adapter
    print("🔧 Test 4: Framework Adapter")
    adapter = loop.adapter
    print(f"   ✅ Machine: {adapter.machine_config.platform}")
    print(f"   ✅ RAM: {adapter.machine_config.memory_gb:.1f}GB")
    print(f"   ✅ GPUs: {adapter.machine_config.gpu_count}")
    print()

    # Test 5: Run autonomous loop for 30 seconds
    print("🔄 Test 5: Autonomous Loop (30 seconds)")
    print("   Running autonomous loop...")
    print("   (Press Ctrl+C to stop early)\n")

    try:
        await asyncio.wait_for(loop.autonomous_run(check_interval=5.0), timeout=30.0)
    except asyncio.TimeoutError:
        print("\n   ✅ Autonomous loop ran successfully for 30 seconds")
    except KeyboardInterrupt:
        print("\n   ⚠️  Interrupted by user")

    print("\n" + "=" * 60)
    print("✅ PHASE 26C VALIDATION COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_autonomous_loop())
