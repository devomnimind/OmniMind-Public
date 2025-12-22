import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ImportCheck")

logger.info(f"Python Executable: {sys.executable}")
logger.info(f"Python Path: {sys.path}")

try:
    import pymilvus
    from pymilvus import connections, Collection, Utility

    logger.info(f"✅ pymilvus fully imported (Version: {pymilvus.__version__})")
except ImportError as e:
    logger.error(f"❌ pymilvus specific import failed: {e}")

try:
    import ibm_watson_machine_learning

    logger.info("✅ ibm_watson_machine_learning imported")
except ImportError as e:
    logger.error(f"❌ ibm_watson_machine_learning failed: {e}")
