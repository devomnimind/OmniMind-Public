import os
import sys
import logging
from dotenv import load_dotenv

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

logging.basicConfig(level=logging.INFO)
from src.quantum.backends.ibm_real import IBMRealBackend

try:
    print("Attempting to connect to the Real...")
    backend = IBMRealBackend()
    if backend.service:
        print(f"SUCCESS! Connected via: {backend.service.channel}")
        if backend.backend:
            print(f"Active Backend: {backend.backend.name}")
        else:
            print("No real backend found, but service is connected.")
    else:
        print("Failed: No service initialized.")
except Exception as e:
    print(f"FAILED to connect: {e}")
