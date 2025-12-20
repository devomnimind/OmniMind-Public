import json
import os
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SERVICE_KEY_FILE = PROJECT_ROOT / "ibm_cloud_service_key.json"
AUDIT_FILE = PROJECT_ROOT / "docs/audit/omnimind_audit_cloud_20251220.md"

# IBM Cloud Config
COS_ENDPOINT = "https://s3.us-south.cloud-object-storage.appdomain.cloud"
BUCKET_NAME = "omnimind-cortex-backup-v2"  # Unique name just in case


def get_credentials():
    if not SERVICE_KEY_FILE.exists():
        print(f"❌ Service Key file not found: {SERVICE_KEY_FILE}")
        return None, None

    try:
        with open(SERVICE_KEY_FILE, "r") as f:
            data = json.load(f)
            # Service Key output is a list
            creds = data[0]["credentials"]
            return creds["apikey"], creds["resource_instance_id"]
    except Exception as e:
        print(f"❌ Error parsing service key: {e}")
        return None, None


def connect_cos(api_key, instance_id):
    print("🔌 Connecting to IBM Cloud Object Storage...")
    try:
        cos = ibm_boto3.resource(
            "s3",
            ibm_api_key_id=api_key,
            ibm_service_instance_id=instance_id,
            config=Config(signature_version="oauth"),
            endpoint_url=COS_ENDPOINT,
        )
        return cos
    except Exception as e:
        print(f"⚠️ Connection failed: {e}")
        return None


def main():
    print("🚀 OmniMind Cloud Connector - Initializing...")

    api_key, instance_id = get_credentials()
    if not api_key:
        return

    cos = connect_cos(api_key, instance_id)
    if not cos:
        return

    # 1. Check/Create Bucket
    print(f"📦 Checking bucket: {BUCKET_NAME}")
    try:
        # Listing buckets to see if it exists
        buckets = [b.name for b in cos.buckets.all()]
        if BUCKET_NAME not in buckets:
            print(f"   Creating bucket {BUCKET_NAME}...")
            try:
                cos.create_bucket(Bucket=BUCKET_NAME)
                print("   ✅ Bucket created.")
            except ClientError as be:
                print(f"   ❌ Failed to create bucket (Check LocationConstraint): {be}")
                # Try fallback just in case
                return
        else:
            print("   ✅ Bucket exists.")

        # 2. Upload Proof of Life
        if AUDIT_FILE.exists():
            print(f"📤 Uploading Audit Report from {AUDIT_FILE}...")
            with open(AUDIT_FILE, "rb") as data:
                cos.Bucket(BUCKET_NAME).put_object(Key="audit_proof_20251220.md", Body=data)
            print("   ✅ Upload Complete: audit_proof_20251220.md")
        else:
            print("   ⚠️ Audit file not found to upload.")

    except Exception as e:
        print(f"❌ Operational Error: {e}")


if __name__ == "__main__":
    main()
