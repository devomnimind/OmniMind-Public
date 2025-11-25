#!/usr/bin/env python3
"""
Simple test script for dashboard authentication
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Simple authentication check
_AUTH_FILE = Path("config/dashboard_auth.json")

def load_dashboard_credentials():
    if not _AUTH_FILE.exists():
        return None
    try:
        with _AUTH_FILE.open("r", encoding="utf-8") as stream:
            data = json.load(stream)
        user = data.get("user")
        password = data.get("pass")
        if isinstance(user, str) and isinstance(password, str):
            return {"user": user, "pass": password}
    except Exception as exc:
        print(f"Failed to read dashboard auth file {_AUTH_FILE}: {exc}")
    return None

def ensure_dashboard_credentials():
    env_user = os.environ.get("OMNIMIND_DASHBOARD_USER")
    env_pass = os.environ.get("OMNIMIND_DASHBOARD_PASS")
    if env_user and env_pass:
        print("Using dashboard credentials from environment variables")
        return env_user, env_pass

    saved = load_dashboard_credentials()
    if saved:
        print("Loaded dashboard credentials from file")
        return saved["user"], saved["pass"]

    print("No credentials found")
    return None, None

if __name__ == "__main__":
    user, password = ensure_dashboard_credentials()
    print(f"Dashboard user: {user}")
    print(f"Dashboard pass: {password}")