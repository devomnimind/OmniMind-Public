import requests
import time
import json


def test_api_endpoints():
    base_url = "http://localhost:8001"
    auth = ("admin", "admin")  # Default credentials

    # Wait for API to be ready
    print(f"Testing API at {base_url}...")
    try:
        # 1. Health Check
        print("Checking Health...")
        r = requests.get(f"{base_url}/api/health", auth=auth)
        print(f"Health ({r.url}): {r.status_code}")

        # 2. Daemon Status
        print("Checking Daemon Status...")
        r = requests.get(f"{base_url}/api/daemon/status", auth=auth)
        print(f"Daemon Status ({r.url}): {r.status_code}")
        if r.status_code == 200:
            status = r.json()
            print(f"  CPU: {status['system_metrics']['cpu_percent']}%")
            print(f"  Phi: {status['consciousness_metrics']['phi']}")

        # 3. Chat Endpoint
        print("Checking Chat...")
        r = requests.post(
            f"{base_url}/api/chat",
            auth=auth,
            json={"message": "Olá OmniMind!", "context": status if r.status_code == 200 else {}},
        )
        print(f"Chat ({r.url}): {r.status_code}")
        if r.status_code == 200:
            print(f"  Response: {r.json()['response']}")

    except Exception as e:
        print(f"Error during verification: {e}")


if __name__ == "__main__":
    test_api_endpoints()
