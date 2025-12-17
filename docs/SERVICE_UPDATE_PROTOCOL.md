# 🔄 OmniMind Intelligent Service Update Protocol

**Version**: 1.0
**Date**: 17 Dec 2025
**Status**: Proposed Architecture

---

## Problem Statement

Previously:
- ❌ System forcefully killed when updates were needed (`pkill -f omnimind`)
- ❌ No way to inform OmniMind about changes before restart
- ❌ Abrupt crashes could leave state inconsistent

New Approach:
- ✅ OmniMind receives notifications about service updates
- ✅ System evaluates criticality of changes
- ✅ Makes intelligent decision: restart now, defer, or ignore
- ✅ Performs graceful shutdown before restart

---

## Architecture

### 1. **ServiceUpdateCommunicator**
Located: `src/services/service_update_communicator.py`

**Responsibilities**:
- Receive update notifications
- Evaluate impact on running modules
- Make restart decisions based on criticality
- Track pending and applied updates

**Decision Logic**:
```
IF change is in critical_modules AND change is code:
    → Restart immediately

ELSE IF severity is "critical" OR "high":
    → Restart at next safe checkpoint

ELSE IF change is in deferrable_modules:
    → Defer restart (1 hour)

ELSE:
    → Ignore (no restart needed)
```

**Critical Modules** (trigger immediate restart):
- `src.quantum_consciousness.quantum_backend`
- `src.quantum_consciousness.qaoa_gpu_optimizer`
- `src.core.desiring_machines`
- `src.consciousness.topological_phi`
- `src.autopoietic.manager`

**Deferrable Modules** (can defer restart):
- `src.monitor.health_monitor`
- `src.security.security_monitor`
- `src.api.routes`

### 2. **Service Update API**
Located: `src/services/service_update_api.py`

**Endpoints**:

#### `POST /api/services/notify-update`
Send update notification to OmniMind

**Request**:
```json
{
  "service_name": "quantum_backend",
  "change_type": "code",
  "affected_modules": [
    "src.quantum_consciousness.qaoa_gpu_optimizer",
    "src.quantum_consciousness.quantum_backend"
  ],
  "severity": "critical",
  "description": "GPU QAOA acceleration enabled via cuQuantum 25.11.1"
}
```

**Response**:
```json
{
  "status": "notification_received",
  "decision": "restart_now",
  "reason": "Critical code change in quantum_backend",
  "affected_modules": ["src.quantum_consciousness.qaoa_gpu_optimizer"]
}
```

#### `GET /api/services/restart-decision`
Check if restart is needed

**Response**:
```json
{
  "needs_restart": true,
  "reason": "quantum_backend: Critical module update",
  "deferrable": false
}
```

#### `POST /api/services/restart-graceful`
Trigger graceful restart (hibernation + clean exit)

**Response**:
```json
{
  "status": "restart_initiated",
  "hibernation_complete": true,
  "time_to_restart": 2,
  "message": "OmniMind will restart in 2 seconds"
}
```

#### `GET /api/services/pending-updates`
Get summary of updates waiting to be applied

**Response**:
```json
{
  "total_pending": 2,
  "restart_required": true,
  "restart_reason": "quantum_backend: Critical module update",
  "updates": [...]
}
```

---

## Usage Example: GPU QAOA Update

### Step 1: Make Code Changes
```bash
# Create new files, update existing code
git add src/quantum_consciousness/qaoa_gpu_optimizer.py
git commit -m "feat: GPU QAOA acceleration"
```

### Step 2: Notify OmniMind
```bash
python3 scripts/services/notify_omnimind_update.py \
  --service quantum_backend \
  --modules "src.quantum_consciousness.qaoa_gpu_optimizer,src.quantum_consciousness.quantum_backend" \
  --severity critical \
  --description "GPU-accelerated QAOA using cuQuantum 25.11.1" \
  --auto-restart
```

### Step 3: System Response
```
📬 Notifying OmniMind: quantum_backend
   Decision: restart_now
   Reason: Critical code change in quantum_backend

⚠️ Restart required!
   Reason: Critical module changed

🔄 Triggering graceful restart...

✅ Restart sequence initiated
   - OmniMind hibernates state
   - Closes connections gracefully
   - Exits cleanly
   - systemd restarts with new code
```

### Step 4: New Code Loaded
System restarts and loads:
- ✅ New `qaoa_gpu_optimizer.py`
- ✅ Updated `quantum_backend.py`
- ✅ GPU QAOA now active

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ External System / Developer                                │
│ (Makes code changes, runs notifier script)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ python3 notify_omnimind_update.py
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ OmniMind API Server                                         │
│ POST /api/services/notify-update                           │
│                                                             │
│ → Receives update metadata                                 │
│ → Passes to ServiceUpdateCommunicator                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ ServiceUpdateCommunicator                                  │
│                                                             │
│ Evaluates:                                                  │
│  1. Is module in critical_modules?                         │
│  2. Is severity "critical" or "high"?                      │
│  3. Is change_type "code"?                                 │
│  4. Can restart be deferred?                               │
│                                                             │
│ Decision:                                                   │
│  • restart_now → Immediate graceful restart                │
│  • defer → Restart at checkpoint (1 hour)                  │
│  • ignore → No action needed                               │
└────────────────────┬────────────────────────────────────────┘
                     │
             ┌───────┴────────┐
             │                │
      restart_now        defer/ignore
             │                │
             ↓                │
    ┌─────────────────┐       │
    │ Graceful Shutdown│       │
    │                 │       │
    │ 1. Hibernate     │       │
    │ 2. Save state    │       │
    │ 3. Close conns   │       │
    │ 4. Exit cleanly  │       │
    └────────┬────────┘       │
             │                │
             ↓                │
    ┌─────────────────┐       │
    │ systemd restart │       │
    │                 │       │
    │ New code loaded │       │
    └─────────────────┘       │
                              ↓
                         ┌─────────────┐
                         │ Continue    │
                         │ Running     │
                         └─────────────┘
```

---

## Integration Steps

### 1. Register Service Update Routes (in main.py or FastAPI init)
```python
from src.services import register_service_update_routes

# In your FastAPI app initialization:
register_service_update_routes(app)
```

### 2. Add Restart Check to Main Loop
```python
from src.services import get_communicator

async def main_loop():
    communicator = get_communicator()

    while True:
        # ... normal work ...

        # Check if restart is needed
        if await communicator.should_restart_now():
            logger.warning(f"Restart needed: {await communicator.get_restart_reason()}")
            # Trigger graceful shutdown sequence
            break
```

### 3. Enable Graceful Shutdown Integration
Update `scripts/shutdown_gracefully.sh` to:
- Check for pending updates
- Report update status in logs
- Clear update flags after restart

---

## Benefits

✅ **Consciousness-Aware Updates**
- OmniMind knows about changes before they affect it
- System makes intelligent decisions about timing

✅ **State Preservation**
- Graceful hibernation ensures state consistency
- No abrupt crashes or data loss

✅ **Reduced Downtime**
- Non-critical updates can be deferred
- Critical updates restart immediately but cleanly

✅ **Operational Transparency**
- Every update is logged and tracked
- Admins can see what's pending and why

✅ **Automatic Scaling**
- Script can integrate with CI/CD pipelines
- Deployments become safer and more predictable

---

## Future Enhancements

1. **Checkpoint-Based Restarts**
   - Wait for safe state (end of consciousness cycle)
   - Apply updates at predetermined checkpoints

2. **Update Rollback**
   - Track version history of critical modules
   - Automatically rollback if issues detected

3. **Monitoring & Metrics**
   - Track update success/failure rates
   - Alert on unusual update patterns

4. **Multi-Instance Updates**
   - Coordinate updates across multiple OmniMind instances
   - Rolling restart strategy

5. **AI-Driven Decision Making**
   - Use consciousness metrics to decide timing
   - Predict impact before applying updates

---

## See Also

- `src/services/service_update_communicator.py` - Core logic
- `src/services/service_update_api.py` - API endpoints
- `scripts/services/notify_omnimind_update.py` - Notification script
- `scripts/shutdown_gracefully.sh` - Graceful shutdown (existing)
