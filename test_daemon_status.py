#!/usr/bin/env python3
import asyncio
import os
import sys

# Set up paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
src_path = os.path.join(project_root, 'src')
web_path = os.path.join(project_root, 'web')

sys.path.insert(0, src_path)
sys.path.insert(0, web_path)

# Set PYTHONPATH
os.environ['PYTHONPATH'] = f"{src_path}:{web_path}"

async def test_daemon_status():
    try:
        from src.api.routes.daemon import get_daemon_status
        result = await get_daemon_status()
        print("✅ Daemon status retrieved successfully!")
        print(f"Keys: {list(result.keys())}")
        if 'consciousness_metrics' in result:
            print(f"Consciousness metrics keys: {list(result['consciousness_metrics'].keys())}")
            print(f"Phi: {result['consciousness_metrics'].get('phi', 'N/A')}")
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("Testing daemon status...")
    result = asyncio.run(test_daemon_status())
    if result:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!")