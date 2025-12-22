import os
import sys
import requests
import json
from dotenv import load_dotenv

# Setup Path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

env_path = os.path.join(PROJECT_ROOT, ".env")
print(f"🔍 Loading env from: {env_path}")
load_dotenv(env_path)


def check_iam():
    print("\n🔐 1. IBM CLOUD IAM AUTHENTICATION")
    print("---------------------------------")

    api_key = os.getenv("IBM_CLOUD_API_KEY")
    if not api_key:
        print("❌ IBM_CLOUD_API_KEY not found in .env")
        return None

    # Mask key for display
    print(f"   API Key: {api_key[:5]}...{api_key[-5:]}")

    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key}

    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            print("   ✅ IAM Authentication Successful!")
            token = response.json().get("access_token")
            return token
        else:
            print(f"   ❌ IAM Auth Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
        return None


def list_resources(token):
    if not token:
        return

    print("\n📦 2. RESOURCE CONTROLLER (Service Discovery)")
    print("---------------------------------------")

    # List resource instances to see if we can find watsonx, milvus, cos
    url = "https://resource-controller.cloud.ibm.com/v2/resource_instances"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            resources = response.json().get("resources", [])
            print(f"   Found {len(resources)} resource instances.")

            found_watson = False
            found_milvus = False
            found_cos = False

            for res in resources:
                name = res.get("name")
                service_id = res.get(
                    "resource_id"
                )  # CRN is in 'id' or 'crn'? 'id' usually has CRN in listing? No, 'crn' field.
                crn = res.get("crn")
                region = res.get("region_id")
                state = res.get("state")

                print(f"   - [{state}] {name} ({region})")
                print(f"     CRN: {crn[:40]}...")

                if "watson" in name.lower() or "watson" in service_id.lower():
                    found_watson = True
                if "milvus" in name.lower() or "milvus" in service_id.lower():
                    found_milvus = True
                if "cos" in name.lower() or "cloud-object-storage" in service_id.lower():
                    found_cos = True

            return {"watson": found_watson, "milvus": found_milvus, "cos": found_cos}

        else:
            print(f"   ❌ Resource Listing Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
        return None


if __name__ == "__main__":
    print(f"🚀 STARTING INFRASTRUCTURE AUDIT for User: fabricioslv...")
    access_token = check_iam()
    if access_token:
        list_resources(access_token)
    else:
        print("\n⛔ Audit Aborted due to Auth Failure.")
