# OmniMind Sequential Initialization Strategy

**Date**: 2025-12-09
**Status**: Active - High CPU Issue Resolved
**Author**: System Architecture Team

## Problem Statement

Backend initialization was getting stuck with 100% CPU consumption and services not responding to health checks due to:

1. **Heavy initialization during startup** - Orchestrator and Consciousness metrics loading blocked event loop
2. **Parallel, unordered startup** - Multiple services competing for resources
3. **No dependency management** - Services starting before their dependencies
4. **Missing health check feedback** - No way to verify service readiness before next startup
5. **Infinite loops in background tasks** - Consciousness metrics running too frequently

## Solution Architecture

### Three-Tier Initialization Strategy

```
TIER 1: CRITICAL (0-15s)
├─ Backend Health Endpoints ONLY
├─ WebSocket Manager (fast)
├─ Agent Broadcaster (fast)
└─ Essential routing

        ↓ (verify health)

TIER 2: ESSENTIAL (15-60s, after Tier 1 healthy)
├─ MCP Orchestrator (heavy - async, non-blocking)
├─ Observer Service
├─ Daemon Monitor
└─ Realtime Analytics

        ↓ (verify all healthy)

TIER 3: BACKGROUND (60s+, after Tier 2 ready)
├─ Consciousness Metrics (very heavy)
├─ Frontend
├─ eBPF Monitor
└─ Long-term metrics collection
```

### Key Features

#### 1. **Disabled During Startup** (Environment Variables)

```bash
# Disable heavy services during backend initialization
export OMNIMIND_INIT_ORCHESTRATOR=0         # Default: disabled
export OMNIMIND_INIT_CONSCIOUSNESS=0        # Default: disabled

# Enable when you need them
export OMNIMIND_INIT_ORCHESTRATOR=1         # Enables after health check
export OMNIMIND_INIT_CONSCIOUSNESS=1        # Starts after 60s
```

#### 2. **Health Check Verification**

Each service must pass health checks before moving to next tier:

```python
async def health_check_with_retry(
    service_name: str,
    max_retries: int = 10,
    retry_interval: float = 2.0
) -> bool:
    """Verify service is healthy before proceeding"""
```

#### 3. **Individual Timeouts**

Each service has its own startup timeout:

```
Backend Primary (8000):      30s
Backend Secondary (8080):    30s  (depends on primary)
WebSocket Manager:           10s
MCP Orchestrator:            45s  (depends on WebSocket)
Observer Service:            20s
Daemon Monitor:              15s
Consciousness Collector:     60s  (delayed 60s into startup)
Frontend:                    30s
```

#### 4. **Dependency Management**

Services only start after their dependencies are verified healthy:

```
Backend Primary (no deps)
  ├─ Backend Secondary (depends on Primary)
  ├─ WebSocket Manager (depends on Primary)
  │   └─ MCP Orchestrator (depends on WebSocket)
  ├─ Observer Service (depends on Primary)
  └─ Daemon Monitor (depends on Primary)
```

## Usage

### Ultra-Fast Backend (Lean Mode)

**Best for**: Development, testing, CI/CD, rapid iteration

```bash
cd /home/fahbrain/projects/omnimind
./scripts/canonical/system/start_ultrasimple.sh

# Expected startup time: 15-20 seconds
# Backend responds within 5 seconds
# All health checks pass
# Heavy services disabled
```

**Environment**:
```bash
OMNIMIND_INIT_ORCHESTRATOR=0
OMNIMIND_INIT_CONSCIOUSNESS=0
```

### Sequential Initialization (Full Stack)

**Best for**: Production, full features, long-running systems

```bash
cd /home/fahbrain/projects/omnimind
./scripts/canonical/system/start_sequential.sh

# Tier 1: 10-20s (Backend + essential services)
# Tier 2: 15-45s (Orchestrator, monitoring)
# Tier 3: 60s+  (Heavy tasks, consciousness)
# Total: ~90-120 seconds for full system
```

**Environment**:
```bash
OMNIMIND_INIT_ORCHESTRATOR=1
OMNIMIND_INIT_CONSCIOUSNESS=1
```

### Original Start Script (Now Fixed)

```bash
cd /home/fahbrain/projects/omnimind
./scripts/start_omnimind_system.sh

# Uses improved run_cluster.sh with proper variable expansion
# Starts secondary services after backend verification
```

## Monitoring

### Check Backend Status

```bash
# Health check
curl http://localhost:8000/health/

# Specific service status
curl http://localhost:8000/health/ | jq '.checks'

# Full system status
curl http://localhost:8000/status/
```

### Monitor Logs

```bash
# Backend primary
tail -f logs/backend_8000.log

# All backends
tail -f logs/backend_*.log

# Sequential init results
cat logs/init_results.json

# Real-time monitoring
watch -n 1 'ps aux | grep -E "uvicorn|python.*main" | grep -v grep'
```

### CPU Monitoring

```bash
# Check current CPU usage
ps aux --no-headers -o pcpu,cmd | grep python | head -10

# Monitor system resources
htop -p $(pgrep -f 'uvicorn.*main:app' | tr '\n' ',' | sed 's/,$//')

# Check if spinning
strace -p $(pgrep -f 'uvicorn.*main:app' | head -1) -e trace=none 2>&1 | head -20
```

## Troubleshooting

### Backend stuck at 100% CPU

**Problem**: Backend process using maximum CPU, not responding

**Diagnosis**:
```bash
# Check what backend is doing
strace -p $(pgrep -f 'uvicorn.*main:app' | head -1) -e trace=none

# Check logs for infinite loops
tail -f logs/backend_8000.log | grep -E "WARNING|Error|loop"

# Monitor memory
watch -n 1 'ps aux | grep uvicorn | grep -v grep'
```

**Solution**:
```bash
# Kill backend
pkill -9 -f 'uvicorn.*main:app'

# Start with lean mode first
./scripts/canonical/system/start_ultrasimple.sh

# If that works, enable features gradually:
# export OMNIMIND_INIT_ORCHESTRATOR=1
# restart
```

### Health checks failing

**Problem**: Backend not responding to health check

**Solution**:
```bash
# Check if port is listening
netstat -tlnp | grep 8000
ss -tlnp | grep 8000

# Check if process exists
ps aux | grep uvicorn

# Check for port conflicts
lsof -i :8000

# Check logs
tail -n 50 logs/backend_8000.log
```

### Services not starting in order

**Problem**: Sequential initialization not working

**Solution**:
```bash
# Verify dependencies are running
ps aux | grep -E 'uvicorn|python.*main' | grep -v grep

# Check init results
cat logs/init_results.json | python -m json.tool

# Run with verbose logging
PYTHONVERBOSE=1 ./scripts/canonical/system/start_sequential.sh

# Manual start
python ./scripts/canonical/system/init_sequential_services.py
```

## Performance Metrics

### Startup Times (Measured 2025-12-09)

| Mode | Backend Ready | All Services | Total |
|------|---------------|--------------|-------|
| **Ultra-Simple** | 3-5s | 5-10s | 10-15s |
| **Sequential** | 5-8s | 30-60s | 60-90s |
| **Full System** | 8-12s | 90-180s | 120-180s |

### Resource Usage

| Service | CPU (startup) | Memory (idle) | Memory (peak) |
|---------|---------------|--------------|---------------|
| Backend | 15-30% | 180MB | 250MB |
| Orchestrator | 40-60% | 50MB | 300MB+ |
| Consciousness | 80%+ | 100MB | 500MB+ |
| Frontend | 5-10% | 60MB | 120MB |
| **Total** | **varies** | **500MB** | **1.2GB+** |

## Environment Variables Reference

### Initialization Control

```bash
# Startup mode
OMNIMIND_MODE=production|test

# Service initialization flags
OMNIMIND_INIT_ORCHESTRATOR=0|1        # Orchestrator (default: 0)
OMNIMIND_INIT_CONSCIOUSNESS=0|1       # Consciousness metrics (default: 0)

# Metrics collection
OMNIMIND_METRICS_INTERVAL=30          # Seconds between metrics (default: 30)
OMNIMIND_CONSCIOUSNESS_METRICS_INTERVAL=300  # Seconds (default: 300)

# Project root (auto-detected if not set)
OMNIMIND_PROJECT_ROOT=/path/to/omnimind

# Debug flags
OMNIMIND_DEBUG=1
PYTHONVERBOSE=1
```

## Recommended Workflows

### Development/Testing

```bash
# 1. Start lean backend
./scripts/canonical/system/start_ultrasimple.sh &

# 2. Run quick tests
pytest tests/ -v

# 3. When needing orchestrator:
# - Kill backend
# - export OMNIMIND_INIT_ORCHESTRATOR=1
# - restart

pkill -9 -f 'uvicorn.*main:app'
export OMNIMIND_INIT_ORCHESTRATOR=1
./scripts/canonical/system/start_ultrasimple.sh
```

### Production Deployment

```bash
# 1. Full sequential start
./scripts/canonical/system/start_sequential.sh

# 2. Verify all tiers
sleep 120
curl http://localhost:8000/status/

# 3. Monitor ongoing
tail -f logs/backend_8000.log &
watch -n 2 ps aux | grep python
```

### CI/CD Pipeline

```bash
# Start lean backend for tests
export OMNIMIND_INIT_ORCHESTRATOR=0
export OMNIMIND_INIT_CONSCIOUSNESS=0
./scripts/canonical/system/start_ultrasimple.sh

# Wait for readiness
while ! curl -s http://localhost:8000/health/ > /dev/null; do sleep 1; done

# Run tests
pytest tests/ --timeout=30

# Cleanup
pkill -9 -f 'uvicorn.*main:app'
```

## Architecture Decisions

### Why Disable Heavy Services by Default?

1. **Faster feedback loops** - Backend responds immediately for health checks
2. **Reduced resource pressure** - CPU at 15-30% instead of 100%
3. **Reliable startup** - No infinite loops blocking event loop
4. **Testing friendly** - Easy to test API without full system
5. **Optional features** - Services can be enabled as needed

### Why Sequential Instead of Parallel?

1. **Resource management** - Prevents CPU spike from parallel initialization
2. **Dependency clarity** - Services only run after dependencies ready
3. **Error diagnosis** - Know exactly which service failed
4. **Graceful degradation** - Can skip failed non-critical services
5. **Monitoring** - Clear startup progression visible in logs

### Why Background Tasks for Heavy Services?

1. **Non-blocking startup** - Backend responds while initializing
2. **Progressive initialization** - Start essential, add features later
3. **Flexibility** - Can disable if not needed
4. **Reliability** - Failures don't crash entire system

## Future Improvements

- [ ] Health check dashboard showing startup progress
- [ ] Automatic feature detection (enable services only if available)
- [ ] Graceful shutdown for long-running tasks
- [ ] Service dependency configuration file
- [ ] Metrics on initialization performance
- [ ] Automatic restart of failed services
- [ ] Load testing of initialization sequence
- [ ] Documentation of breaking points

## Related Files

- [`scripts/canonical/system/start_ultrasimple.sh`](../../scripts/canonical/system/start_ultrasimple.sh) - Ultra-fast lean mode
- [`scripts/canonical/system/start_sequential.sh`](../../scripts/canonical/system/start_sequential.sh) - Sequential initialization wrapper
- [`scripts/canonical/system/init_sequential_services.py`](../../scripts/canonical/system/init_sequential_services.py) - Sequential init manager
- [`scripts/canonical/system/run_cluster.sh`](../../scripts/canonical/system/run_cluster.sh) - Backend cluster startup (fixed)
- [`web/backend/main.py`](../../web/backend/main.py) - Backend main app (modified for delayed init)

---

**Last Updated**: 2025-12-09
**Status**: Verified and working - High CPU issue resolved
