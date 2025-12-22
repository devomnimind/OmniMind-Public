#!/usr/bin/env python3
import os
import sys
import logging
import ibm_boto3
from ibm_botocore.client import Config, ClientError

# Setup Path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BucketDrill")


def locate_bucket_region():
    key = os.getenv("IBM_CLOUD_API_KEY") or os.getenv("IBM_API_KEY")
    crn = os.getenv("IBM_COS_CRN")
    target_bucket = "watsonx-data-05ac4241-00f6-4060-8998-49533eaf31bb"

    regions = ["us-south", "us-east", "au-syd", "eu-de", "eu-gb", "jp-tok"]

    logger.info(f"🌍 Starting GLOBAL SEARCH for bucket: {target_bucket}")

    found_region = None

    for region in regions:
        # Construct endpoint
        endpoint = f"https://s3.{region}.cloud-object-storage.appdomain.cloud"
        logger.info(f"   📡 Probing region: {region} ({endpoint})...")

        try:
            cos = ibm_boto3.resource(
                "s3",
                ibm_api_key_id=key,
                ibm_service_instance_id=crn,
                config=Config(signature_version="oauth"),
                endpoint_url=endpoint,
            )

            # Use head_bucket to check existence/access
            cos.meta.client.head_bucket(Bucket=target_bucket)

            logger.info(f"✅ FOUND IT! Bucket exists in region: {region}")
            found_region = region
            break

        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "Unknown")
            if code == "404":
                logger.debug(f"      - Not in {region} (404)")
            elif code == "400":
                logger.debug(f"      - Bad Request in {region} (Constraint Mismatch)")
            elif code == "403":
                logger.warning(f"      - Access Denied in {region} (403) - Found but locked?")
                # 403 usually means it exists but permission issue. It implies correct region often.
                found_region = region
                break
            else:
                logger.debug(f"      - Error in {region}: {code} - {e}")

    if found_region:
        logger.info(f"\n✨ WINNER: The ecosystem resides in '{found_region}'.")
        endpoint = f"https://s3.{found_region}.cloud-object-storage.appdomain.cloud"
        logger.info(f"   Correct Endpoint: {endpoint}")
    else:
        logger.critical(
            "\n❌ Bucket not found in ANY standard region. Check if it's Private Only or Cross-Region."
        )


if __name__ == "__main__":
    locate_bucket_region()
