import os
import sys
from dotenv import load_dotenv

# Load env
load_dotenv()

try:
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference

    print("✅ ibm_watsonx_ai imported successfully")
except ImportError:
    print("❌ ibm_watsonx_ai NOT found")
    sys.exit(1)

api_key = os.getenv("IBM_WATSONX_APIKEY") or os.getenv("IBM_CLOUD_API_KEY")
project_id = os.getenv("IBM_WATSONX_PROJECT_ID")
url = os.getenv("IBM_WATSONX_URL", "https://au-syd.ml.cloud.ibm.com")

print(f"URL: {url}")
print(f"Project ID: {project_id}")
print(f"API Key present: {bool(api_key)}")

if not api_key or not project_id:
    print("❌ Missing credentials")
    sys.exit(1)

try:
    creds = Credentials(url=url, api_key=api_key)
    client = APIClient(creds, project_id=project_id)
    print("✅ APIClient created")

    model = ModelInference(
        model_id="meta-llama/llama-3-3-70b-instruct",
        api_client=client,
        params={"max_new_tokens": 50},
    )
    print("✅ ModelInference initialized")

    print("Attempting generation...")
    res = model.generate_text(prompt="Hello, who are you?")
    print(f"✅ Response: {res}")
except Exception as e:
    print(f"❌ Error: {e}")
