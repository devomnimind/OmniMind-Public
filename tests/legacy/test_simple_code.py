#!/usr/bin/env python3
"""
Simple CodeAgent Test - Direct Implementation
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.agents import CodeAgent


def test_simple_code_generation():
    print("Testing CodeAgent direct file creation...")

    agent = CodeAgent("/home/fahbrain/projects/omnimind/config/agent_config.yaml")

    task = """Create a file hello_world.py with a simple function:

def greet(name):
    return f"Hello, {name}!"

if __name__ == '__main__':
    print(greet("World"))
"""

    print(f"\nTask: {task}")
    print("\nExecuting...")

    result = agent.run(task)

    print(f"\n✓ Result: {result}")

    # Check if file exists
    file_path = Path("/home/fahbrain/projects/omnimind/hello_world.py")
    if file_path.exists():
        print(f"✅ File created: {file_path}")
        print(f"Content:\n{file_path.read_text()}")
    else:
        print("❌ File NOT created")
        print("\nDEBUG: Agent state:")
        print(f"  Completed: {result.get('completed')}")
        print(f"  Messages: {len(result.get('messages', []))}")


if __name__ == "__main__":
    test_simple_code_generation()
