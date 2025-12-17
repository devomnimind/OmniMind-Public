#!/usr/bin/env python3
"""
Debug script to check what credentials are being loaded by auth.py
"""

import json
import os
from pathlib import Path

print("🔍 OmniMind Credentials Debug")
print("=" * 60)

# Check environment variables
print("\n1️⃣  Environment Variables:")
env_user = os.getenv("OMNIMIND_DASHBOARD_USER") or os.getenv("DASHBOARD_USER")
env_pass = os.getenv("OMNIMIND_DASHBOARD_PASS") or os.getenv("DASHBOARD_PASS")
print(f"   OMNIMIND_DASHBOARD_USER: {env_user or '(not set)'}")
print(f"   OMNIMIND_DASHBOARD_PASS: {'***' if env_pass else '(not set)'}")

# Check file
print("\n2️⃣  File location (config/dashboard_auth.json):")
auth_file = Path(os.environ.get("OMNIMIND_DASHBOARD_AUTH_FILE", "config/dashboard_auth.json"))
print(f"   Path: {auth_file}")
print(f"   Exists: {auth_file.exists()}")
print(f"   Absolute: {auth_file.absolute()}")

if auth_file.exists():
    try:
        with auth_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        user = data.get("user", "")
        pass_word = data.get("pass", "")
        print(f"   User: {user}")
        print(f"   Pass: {'***' if pass_word else '(empty)'}")
    except Exception as e:
        print(f"   Error reading file: {e}")
else:
    print("   ⚠️  File does not exist!")

# What will be used?
print("\n3️⃣  What will be used by verify_credentials():")
if env_user and env_pass:
    print(f"   ✅ ENV VARS: {env_user} / ***")
elif auth_file.exists():
    try:
        with auth_file.open("r") as f:
            data = json.load(f)
        user = data.get("user", "")
        print(f"   ✅ FILE: {user} / ***")
    except:
        print("   ❌ FALLBACK: admin / omnimind2025! (file error)")
else:
    print("   ❌ FALLBACK: admin / omnimind2025! (file missing)")

print("\n" + "=" * 60)
