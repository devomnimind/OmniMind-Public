#!/usr/bin/env python3
"""Debug completion flag issue"""

import sys

sys.path.insert(0, ".")

from src.agents import ReactAgent

agent = ReactAgent("config/agent_config.yaml")

print("🧪 Testing completion detection...\n")

# Test simple task that should complete in 1 iteration
result = agent.run(
    "Create a file test_completion.txt with content 'test'", max_iterations=3
)

print("\n📊 Results:")
print(f"Completed: {result['completed']}")
print(f"Final Result: {result['final_result']}")
print(f"Iterations: {result['iteration']}")
print(f"Actions: {len(result['actions_taken'])}")

if result["actions_taken"]:
    last_action = result["actions_taken"][-1]
    print(f"\nLast action result: {last_action['result'][:200]}")

if result["observations"]:
    last_obs = result["observations"][-1]
    print(f"Last observation: {last_obs[:200]}")

    # Check keyword matching
    keywords = ["success", "completed", "done", "written"]
    matches = [w for w in keywords if w in last_obs.lower()]
    print(f"Matching keywords: {matches}")

print(f"\n✅ Expected: completed=True")
print(f"❓ Actual: completed={result['completed']}")
