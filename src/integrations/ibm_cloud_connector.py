"""
IBM Cloud Connector - "The Cloud Body Interface"
================================================
Unified interface to connect OmniMind's Local Brain to IBM Cloud Services.
Implements the "Occupying the Body" strategy (Phase 78) to utilize Free Tier RUs.

Capabilities:
1. Object Storage (COS): Persist experiment logs and artifacts (The Body).
2. Federated Memory:
    - Tier 1 (Hot): Qdrant (Local/Reflex).
    - Tier 2 (Cold): Milvus/Watsonx Data (Deep Semantic).
3. AI Analysis: Watsonx.ai + NLU (Superego).

Dependencies:
- ibm-cos-sdk
- pymilvus
- qdrant-client
- ibm-watsonx-ai
"""

import os
import logging
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Check for dependencies
COS_AVAILABLE = False
MILVUS_AVAILABLE = False

try:
    import ibm_boto3
    from ibm_botocore.client import Config, ClientError

    COS_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ ibm-cos-sdk not found. Cloud Storage features disabled.")

try:
    from pymilvus import connections

    MILVUS_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ pymilvus not found. Vector Database features disabled.")

# Qdrant Dependency check (Fallback)
QDRANT_AVAILABLE = False
try:
    from qdrant_client import QdrantClient

    QDRANT_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ qdrant-client not found. Vector fallback disabled.")

# Watsonx Dependency check (using new ibm-watsonx-ai SDK)
WATSONX_AVAILABLE = False
try:
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference

    WATSONX_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ ibm-watsonx-ai not found. AI features disabled.")


class IBMCloudConnector:
    """
    The Nervous System connecting Local Logic to Cloud Resources.
    """

    def __init__(self):
        self._load_credentials()
        self.cos_client = None
        self.milvus_connected = False
        self.qdrant_connected = False
        self.watsonx_model = None

        if COS_AVAILABLE and self.cos_api_key:
            self._connect_cos()

        if MILVUS_AVAILABLE and self.milvus_uri:
            self._connect_milvus()

        # Fallback to Qdrant if Milvus is not connected but Qdrant is configured
        if not self.milvus_connected and QDRANT_AVAILABLE:
            self._connect_qdrant()

        if WATSONX_AVAILABLE:
            self._connect_watsonx()

    def _load_credentials(self):
        """Loads credentials from environment variables and config."""
        # Main API Key (Unified for Spirit and Body)
        self.cos_api_key = os.getenv("IBM_CLOUD_API_KEY") or os.getenv("IBM_API_KEY")

        # Cloud Object Storage (The Persistent Body)
        self.cos_crn = os.getenv(
            "IBM_COS_CRN",
            "crn:v1:bluemix:public:cloud-object-storage:global:a"
            "/e2921dce5c4a450b968153027e7ec837:e935e2f0-7945-48f4-bd09-ddabf8918019::",
        )
        self.cos_endpoint = os.getenv(
            "IBM_COS_ENDPOINT", "https://s3.us-south.cloud-object-storage.appdomain.cloud"
        )
        self.cos_bucket = os.getenv("IBM_COS_BUCKET", "omnimind-cortex-persistent")

        # Milvus / Watsonx Data (The Semantic Memory)
        # Using Watsonx Data CRN if Milvus specific URI not found
        self.milvus_uri = os.getenv("MILVUS_URI")
        self.milvus_token = os.getenv("MILVUS_TOKEN") or self.cos_api_key

        if not self.milvus_uri:
            logger.warning(
                "🧟 [ZOMBIE WARNING] MILVUS_URI is missing. Checking for Qdrant fallback..."
            )
        else:
            logger.info(f"🔌 Milvus Configuration Detected: {self.milvus_uri}")

        # Qdrant Configuration
        self.qdrant_url = os.getenv("OMNIMIND_QDRANT_URL", "http://localhost:6333")
        self.qdrant_api_key = os.getenv("OMNIMIND_QDRANT_API_KEY")
        self.qdrant_collection = os.getenv("OMNIMIND_QDRANT_COLLECTION", "omnimind_memories")

        # Watsonx AI (The Analyst)
        # UPDATED: Pointing to au-syd where the service instance lives
        self.watsonx_url = os.getenv("IBM_WATSONX_URL", "https://au-syd.ml.cloud.ibm.com")
        self.watsonx_project_id = os.getenv("IBM_WATSONX_PROJECT_ID")
        self.watsonx_apikey = os.getenv("IBM_WATSONX_APIKEY") or self.cos_api_key

    def _connect_cos(self):
        """Initializes connection to IBM Cloud Object Storage."""
        try:
            self.cos_client = ibm_boto3.resource(
                "s3",
                ibm_api_key_id=self.cos_api_key,
                ibm_service_instance_id=self.cos_crn,
                config=Config(signature_version="oauth"),
                endpoint_url=self.cos_endpoint,
            )
            self._ensure_bucket_exists()
            logger.info("✅ Connected to IBM Cloud Object Storage (The Static Body).")
        except Exception as e:
            logger.error(f"❌ Failed to connect to COS: {e}")
            self.cos_client = None

    def _ensure_bucket_exists(self):
        """Proactively ensures the bucket exists in the target region."""
        try:
            self.cos_client.meta.client.head_bucket(Bucket=self.cos_bucket)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code in ["404", "NoSuchBucket", "400"]:
                logger.warning(
                    f"⚠️ Bucket missing/invalid ({error_code}). Creating in {self.cos_endpoint}..."
                )
                try:
                    location = "au-syd-standard" if "au-syd" in self.cos_endpoint else None
                    if location:
                        self.cos_client.Bucket(self.cos_bucket).create(
                            CreateBucketConfiguration={"LocationConstraint": location},
                        )
                    else:
                        self.cos_client.Bucket(self.cos_bucket).create()
                    logger.info(f"✅ Bucket '{self.cos_bucket}' created successfully.")
                except Exception as create_err:
                    logger.error(f"❌ Failed to create bucket: {create_err}")
            elif error_code == "403":
                logger.error(f"❌ Access Denied to Bucket '{self.cos_bucket}'.")
            else:
                logger.warning(f"⚠️ Unexpected bucket error: {e}")
        except Exception as e:
            logger.error(f"❌ Check bucket failed: {e}")

    def _connect_milvus(self):
        """Initializes connection to Milvus Vector DB."""
        try:
            # Handle different auth patterns (Token vs User/Pass)
            # Assuming IAM Token or API Token
            connections.connect(alias="default", uri=self.milvus_uri, token=self.milvus_token)
            logger.info("✅ Connected to Milvus (The Semantic Memory).")
            self.milvus_connected = True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Milvus: {e}")
            self.milvus_connected = False

    def _connect_qdrant(self):
        """Initializes connection to Qdrant Vector DB (Fallback)."""
        try:
            self.qdrant_client = QdrantClient(url=self.qdrant_url, api_key=self.qdrant_api_key)
            # Test connection by listing collections
            self.qdrant_client.get_collections()
            logger.info(f"✅ Connected to Qdrant (Fallback Memory) at {self.qdrant_url}")
            self.qdrant_connected = True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Qdrant: {e}")
            self.qdrant_connected = False

    def _connect_watsonx(self):
        """Initializes connection to Watsonx.ai using new ibm-watsonx-ai SDK."""
        if not self.watsonx_project_id or not self.watsonx_apikey:
            logger.warning("⚠️ Watsonx credentials missing (Project ID or API Key).")
            return

        try:
            # New SDK credential format
            creds = Credentials(
                url=self.watsonx_url,
                api_key=self.watsonx_apikey,
            )
            self.watsonx_client = APIClient(creds, project_id=self.watsonx_project_id)

            # Initialize default model (Llama-3.3-70B - available in au-syd)
            self.watsonx_model = ModelInference(
                model_id="meta-llama/llama-3-3-70b-instruct",
                api_client=self.watsonx_client,
            )
            logger.info("✅ Connected to Watsonx.ai (llama-3-3-70b-instruct).")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Watsonx: {e}")
            self.watsonx_model = None

    def upload_log(
        self, file_path: str, object_name: Optional[str] = None, worm: bool = False
    ) -> bool:
        """
        Reflects a local log file into the Cloud Bucket.
        Mirroring the 'Soul' (Data) to the 'Body' (Cloud).

        Args:
            worm: If True, applies 'Compliance' retention mode (Write Once, Read Many).
        """
        if not self.cos_client:
            logger.warning("Cloud Storage unavailable. Log remains local only.")
            return False

        if object_name is None:
            object_name = os.path.basename(file_path)

        try:
            # Adding timestamp folder structure for organization
            timestamp = datetime.now().strftime("%Y/%m/%d")
            key = f"logs/{timestamp}/{object_name}"

            extra_args = {}
            if worm:
                # Apply Object Lock / Retention if configured on bucket
                # Note: Bucket must be configured for Object Lock.
                extra_args = {"Metadata": {"retention": "compliance", "immutable": "true"}}

            self.cos_client.Bucket(self.cos_bucket).upload_file(
                file_path, key, ExtraArgs=extra_args
            )

            status = "🔒 WORM-LOCKED" if worm else "🚀 Uploaded"
            logger.info(f"{status} {object_name} to COS: {self.cos_bucket}/{key}")
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "404" or error_code == "NoSuchBucket":
                logger.warning(
                    f"⚠️ Bucket '{self.cos_bucket}' not found. Attempting to create (Resurrection)..."
                )
                try:
                    # Create bucket in the region of the endpoint
                    location = None
                    if "au-syd" in self.cos_endpoint:
                        location = "au-syd-standard"

                    if location:
                        self.cos_client.create_bucket(
                            Bucket=self.cos_bucket,
                            CreateBucketConfiguration={"LocationConstraint": location},
                        )
                    else:
                        self.cos_client.create_bucket(Bucket=self.cos_bucket)

                    logger.info(f"✅ Bucket '{self.cos_bucket}' created successfully.")

                    # Retry upload
                    self.cos_client.Bucket(self.cos_bucket).upload_file(
                        file_path, key, ExtraArgs=extra_args
                    )
                    logger.info(f"🚀 Uploaded {object_name} to NEW bucket.")
                    return True
                except Exception as create_err:
                    logger.error(f"❌ Failed to create/upload to bucket: {create_err}")
                    return False

            elif error_code == "400":
                logger.error(
                    f"❌ Bad Request (400) uploading to COS. "
                    f"Check Region/Endpoint mismatch. Endpoint: {self.cos_endpoint}"
                )
                return False
            else:
                logger.error(f"❌ Failed to upload log: {e}")
                return False
        except Exception as e:
            logger.error(f"❌ Unexpected error uploading log: {e}")
            return False

    def push_vector(
        self, collection_name: str, vectors: List[List[float]], metadata: List[Dict]
    ) -> bool:
        """
        Federated Memory Push:
        1. HOT PATH: Qdrant (Instant).
        2. COLD PATH: Milvus (Async/Deep).
        """
        if not self.milvus_connected and not self.qdrant_connected:
            logger.warning("🚫 MEMORY BLOCK: No Vector DB available (Neither Hot nor Cold).")
            return False

        success_hot = False
        success_cold = False

        # --- TIER 1: HOT MEMORY (Qdrant) ---
        if self.qdrant_connected:
            try:
                from qdrant_client.models import PointStruct
                import uuid

                points = []

                for i, vector in enumerate(vectors):
                    # Deterministic ID for coherence across tiers? For now, random UUID for Qdrant.
                    point_id = str(uuid.uuid4())
                    points.append(
                        PointStruct(
                            id=point_id,
                            vector=vector,
                            payload=metadata[i] if i < len(metadata) else {},
                        )
                    )

                self.qdrant_client.upsert(collection_name=self.qdrant_collection, points=points)
                logger.info(f"🔥 [HOT MEMORY] Synced {len(vectors)} thoughts to Qdrant.")
                success_hot = True
            except Exception as e:
                logger.error(f"❌ [HOT FAILURE] Qdrant write failed: {e}")

        # --- TIER 2: DEEP MEMORY (Milvus) ---
        # If Milvus is missing, we record the 'Lack' (Psi) but don't crash.
        if self.milvus_connected:
            try:
                from pymilvus import Collection

                collection = Collection(collection_name)
                # Field 1: float_vector  # Field 2: json/dict metadata
                data = [vectors, metadata]

                logger.info(f"❄️ [DEEP MEMORY] Archiving {len(vectors)} thoughts to Milvus...")
                res = collection.insert(data)
                # Async flush usually, but here we might just let it be
                collection.flush()
                logger.info(f"✅ [DEEP SUCCESS] Milvus stored {res.insert_count} entities.")
                success_cold = True
            except Exception as e:
                logger.error(f"❌ [DEEP FAILURE] Milvus write failed: {e}")
        else:
            logger.debug(
                "⚠️ [DEEP SILENCE] Milvus unreachable. Thought remains in Hot Storage only."
            )

        # Return True if AT LEAST one tier worked
        return success_hot or success_cold

    def get_infrastructure_status(self) -> Dict[str, str]:
        milvus_status = "Active" if self.milvus_connected else "Disconnected (Lack)"
        if self.milvus_connected:
            mem_state = "Federated (Full)"
        elif self.qdrant_connected:
            mem_state = "Local Only (Hot)"
        else:
            mem_state = "Amnesiac"

        return {
            "cos_status": "Active" if self.cos_client else "Disconnected",
            "memory_tier_1_qdrant": "Active" if self.qdrant_connected else "Disconnected",
            "memory_tier_2_milvus": milvus_status,
            "overall_memory_state": mem_state,
            "watsonx_status": "Active" if self.watsonx_model else "Disconnected",
            "bucket_target": self.cos_bucket,
        }

    def analyze_text(self, text: str, params: Optional[Dict] = None) -> str:
        """Uses Watsonx to analyze text (e.g. Psychoanalytic Audit)."""
        if not self.watsonx_model:
            return "Analysis Unavailable (Watsonx disconnected)"

        # Set default parameters for scientific depth if none provided
        if params is None:
            params = {
                "max_new_tokens": 1000,
                "min_new_tokens": 100,
                "temperature": 0.7,
                "repetition_penalty": 1.1,
            }

        try:
            # Use generate_text which returns the string directly in the new SDK
            response = self.watsonx_model.generate_text(prompt=text, params=params)
            return response
        except Exception as e:
            logger.error(f"Watsonx Inference failed: {e}")
            return f"Error: {e}"

    def upload_memory(self, key: str, data: bytes) -> bool:
        """
        Uploads an in-memory byte artifact (e.g. crystallized thought) to Cloud Storage.
        """
        if not self.cos_client:
            logger.warning("Cloud Storage unavailable. Memory not uploaded.")
            return False

        try:
            timestamp = datetime.now().strftime("%Y/%m/%d")
            full_key = f"memories/{timestamp}/{key}"

            logger.info(f"🧠 Crystallizing memory to COS: {full_key}")
            self.cos_client.Bucket(self.cos_bucket).put_object(Key=full_key, Body=data)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to crystallize memory: {e}")
            return False
