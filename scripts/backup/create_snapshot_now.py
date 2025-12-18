#!/usr/bin/env python3
"""
Create consciousness snapshot immediately.

Useful for manual snapshots before experiments or important changes.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.consciousness.integration_loop import IntegrationLoop


async def main():
    """Create snapshot immediately."""
    import argparse

    parser = argparse.ArgumentParser(description="Create consciousness snapshot")
    parser.add_argument("--tag", type=str, help="Tag for snapshot (e.g., 'experimento_001')")
    parser.add_argument("--description", type=str, help="Description of snapshot")
    parser.add_argument(
        "--no-loop",
        action="store_true",
        help="Don't create IntegrationLoop (use existing state)",
    )

    args = parser.parse_args()

    # Create IntegrationLoop (or use existing)
    if args.no_loop:
        print("⚠️  Using existing IntegrationLoop state (if available)")
        # In this case, we'd need to get existing loop instance
        # For now, create a new one
        loop = IntegrationLoop(enable_extended_results=True, enable_logging=False)
    else:
        print("Creating IntegrationLoop...")
        loop = IntegrationLoop(enable_extended_results=True, enable_logging=False)

    # Create snapshot
    print("Creating consciousness snapshot...")
    snapshot_id = loop.create_full_snapshot(tag=args.tag, description=args.description)

    print(f"\n✅ Snapshot created successfully!")
    print(f"Snapshot ID: {snapshot_id}")
    if args.tag:
        print(f"Tag: {args.tag}")
    if args.description:
        print(f"Description: {args.description}")
    print(f"\nTo restore this snapshot:")
    print(f"   loop.restore_from_snapshot('{snapshot_id}')")


if __name__ == "__main__":
    asyncio.run(main())
