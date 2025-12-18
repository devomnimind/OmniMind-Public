# 🔴 OmniMind Login Issue - ROOT CAUSE & SOLUTION

## The Problem 🐛

Login failing with `Invalid dashboard credentials` error even though:
- ✅ Credentials endpoint (`/auth/credentials`) returns correct credentials
- ✅ Credentials file (`config/dashboard_auth.json`) contains correct credentials
- ❌ Backend rejects those same credentials when used for API calls

## Root Cause 🎯

**Environment variables are overriding the credentials file!**

```
Old hardcoded env vars from deploy/.env:
  OMNIMIND_DASHBOARD_USER=dashboard
  OMNIMIND_DASHBOARD_PASS=omnimind

These override the actual credentials:
  f483b52c30c2eaed / tazYUoFeR8Yzouduz2y0Mw
```

**How it happens:**

1. `auth.py` checks ENV VARS FIRST (highest priority)
2. Finds old `OMNIMIND_DASHBOARD_USER=dashboard`
3. Uses that instead of reading the file
4. Frontend sends correct credentials from file
5. Backend rejects them because it's looking for different ones

## Solution ✅

### Option 1: Clear Environment Variables (QUICK FIX)
```bash
# Before starting backend:
unset OMNIMIND_DASHBOARD_USER OMNIMIND_DASHBOARD_PASS DASHBOARD_USER DASHBOARD_PASS

# Then start backend:
cd /home/fahbrain/projects/omnimind
python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 &
```

### Option 2: Update Environment Variables (PROPER FIX)
Update `/home/fahbrain/projects/omnimind/.env`:

**Current:**
```bash
OMNIMIND_DASHBOARD_USER=
OMNIMIND_DASHBOARD_PASS=
```

**Should be:** (leave empty so it uses file)
```bash
OMNIMIND_DASHBOARD_USER=
OMNIMIND_DASHBOARD_PASS=
```

Or set to actual credentials:
```bash
OMNIMIND_DASHBOARD_USER=f483b52c30c2eaed
OMNIMIND_DASHBOARD_PASS=tazYUoFeR8Yzouduz2y0Mw
```

### Option 3: Clear deploy/.env (PERMANENT FIX)

Remove or update `deploy/.env` to use file-based credentials:

**Current `deploy/.env` line 27-28:**
```bash
OMNIMIND_DASHBOARD_USER=dashboard
OMNIMIND_DASHBOARD_PASS=omnimind
```

**Change to:**
```bash
# Credentials loaded from config/dashboard_auth.json
# OMNIMIND_DASHBOARD_USER=
# OMNIMIND_DASHBOARD_PASS=
```

## How to Verify It's Fixed ✅

```bash
# Step 1: Check what credentials are being used
python scripts/debug_credentials.py

# Step 2: Should show FILE credentials, not ENV VAR credentials
# ✅ FILE: f483b52c30c2eaed / ***

# Step 3: Test login
bash scripts/test_login.sh

# Should output:
# ✅ Credentials fetched: f483b52c30c2eaed / ***
# ✅ /daemon/status responded successfully
```

## Code Flow Explanation 🔄

```
auth.py - _get_dashboard_credentials():
  1. Check ENV VARS first (❌ OLD VALUES HERE)
  2. If empty, read file (✅ CORRECT VALUES HERE)
  3. If file missing, fallback to hardcoded

Frontend sends:  f483b52c30c2eaed:tazYUoFeR8Yzouduz2y0Mw
Backend expects: dashboard:omnimind
Result: ❌ 401 Unauthorized
```

## Priority Order (in auth.py) 📋

1. **Environment variables** (highest - for prod overrides)
   - `OMNIMIND_DASHBOARD_USER`
   - `OMNIMIND_DASHBOARD_PASS`
2. **JSON file** (source of truth for local development)
   - `config/dashboard_auth.json`
3. **Hardcoded fallback** (emergency only)
   - `admin` / `omnimind2025!`

## Recommended Workflow 🚀

```bash
# 1. Clear old env vars
unset OMNIMIND_DASHBOARD_USER OMNIMIND_DASHBOARD_PASS

# 2. Start backend
cd /home/fahbrain/projects/omnimind
python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 &

# 3. Open http://localhost:3000 in browser
# Frontend will:
#   - Fetch credentials from /auth/credentials ✅
#   - Auto-fill login form with actual credentials ✅
#   - Login successfully ✅
```

## Files to Review 📄

- `web/backend/auth.py` - Credential lookup logic
- `config/dashboard_auth.json` - Current credentials (REAL)
- `deploy/.env` - Old hardcoded credentials (REMOVE OR COMMENT)
- `.env` - Main env config (should be empty for dashboard vars)

---

**TL;DR:** Old environment variables are hiding the real credentials. Clear them and login will work.
