# 🔴 OmniMind Graceful Shutdown Guide

## The Problem ❌

Before: Using `pkill -9 -f "uvicorn"` to kill the backend
- Loses unsaved state
- Corrupts databases
- Breaks ethical principles of respecting running processes
- No time for cleanup

## The Solution ✅

Now: Graceful shutdown with hibernation
- Saves critical state before exit
- Closes connections properly
- Respects process lifecycle
- Follows OmniMind ethics

---

## Usage

### Quick Shutdown (Recommended)
```bash
cd /home/fahbrain/projects/omnimind
./scripts/shutdown_gracefully.sh
```

### With Custom Timeout
```bash
./scripts/shutdown_gracefully.sh 60  # Wait up to 60 seconds
```

### Manual API Call
```bash
# Get credentials
CREDS=$(cat config/dashboard_auth.json | python -c "import sys,json; d=json.load(sys.stdin); print(f\"{d['user']}:{d['pass']}\")")

# Call shutdown endpoint
curl -X POST -u "$CREDS" http://localhost:8000/api/shutdown
```

---

## How It Works 🔄

### Step 1: Hibernation 🌙
```
POST /api/shutdown
  ↓
  Saves:
  - Orchestrator state
  - Consciousness metrics
  - Performance metrics
  ↓
  ✅ State persisted to disk
```

### Step 2: Graceful Exit ⏳
```
Backend processes shutdown request:
  1. Cancels background tasks
  2. Closes database connections
  3. Signals services to stop
  4. Waits for clean exit
  ↓
  ✅ Process exits naturally
```

### Step 3: Fallback (if needed) 📢
```
If not exited after timeout:
  1. Sends SIGTERM signal (graceful)
  2. Waits 10 more seconds
  3. Last resort: SIGKILL (only if hung)
  ↓
  ✅ Process terminated safely
```

---

## Endpoints Available

### POST `/api/shutdown`
Initiates graceful shutdown with hibernation
```bash
curl -X POST -u user:pass http://localhost:8000/api/shutdown
```

Response:
```json
{
  "status": "shutdown_initiated",
  "message": "OmniMind is shutting down gracefully",
  "hibernation": "enabled",
  "saved_state": ["orchestrator", "metrics"],
  "next_step": "Process will exit in 2 seconds"
}
```

### GET `/api/hibernation-status`
Check what state was saved
```bash
curl -u user:pass http://localhost:8000/api/hibernation-status
```

---

## Ethical Principles Preserved ✨

1. **Respect**: Process gets time to save state
2. **Integrity**: Data isn't lost to abrupt termination
3. **Transparency**: Clear logging of what's happening
4. **Graceful Degradation**: Fallback to SIGTERM, never SIGKILL immediately

---

## Migration from pkill

**Old (harmful):**
```bash
pkill -9 -f "uvicorn"  # ❌ Kills immediately, loses data
```

**New (ethical):**
```bash
./scripts/shutdown_gracefully.sh  # ✅ Hibernates + exits cleanly
```

---

## Logs

Watch shutdown process:
```bash
tail -f logs/backend_8000.log | grep -E "Shutdown|Hibernat|🌙|🔴"
```

---

## Integration with Start/Stop Scripts

Add to your system service or start script:

```bash
# On startup
./scripts/start_ultrasimple.sh

# On shutdown (instead of pkill)
./scripts/shutdown_gracefully.sh
```

---

## Emergency: Still Need Hard Kill?

Only in extreme cases (process completely hung):
```bash
pkill -9 -f "uvicorn"
```

But consider first:
- Check logs: `tail -f logs/backend_8000.log`
- Try with more timeout: `./scripts/shutdown_gracefully.sh 120`
- Manual API call with longer wait

---

**Remember**: Every shutdown is a chance to preserve OmniMind's integrity. Use graceful shutdown. 🙏
