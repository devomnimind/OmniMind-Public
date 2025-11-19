# OmniMind Troubleshooting Guide

## Overview

This guide provides comprehensive troubleshooting solutions for common issues and automated diagnostic tools to help identify and resolve problems quickly.

## Quick Diagnostic Tool

Run the automated diagnostic script to check system health:

```bash
python scripts/diagnose.py
```

This will check:
- ✓ Python version compatibility
- ✓ Required dependencies installed
- ✓ Configuration files present
- ✓ Service availability (Qdrant, Ollama)
- ✓ GPU/CUDA availability (if applicable)
- ✓ Network connectivity
- ✓ File permissions
- ✓ Log file integrity

## Common Issues

### 1. Server Won't Start

#### Symptom
```
Error: Address already in use
```

#### Diagnosis
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Or use diagnostic tool
python scripts/diagnose.py --check-ports
```

#### Solution
```bash
# Find and kill the process using port 8000
kill $(lsof -t -i:8000)

# Or use a different port
OMNIMIND_PORT=8001 uvicorn web.backend.main:app
```

### 2. Authentication Failures

#### Symptom
```
401 Unauthorized
```

#### Diagnosis
```bash
# Check credentials file
cat config/dashboard_auth.json

# Verify environment variables
echo $OMNIMIND_DASHBOARD_USER
echo $OMNIMIND_DASHBOARD_PASS
```

#### Solution

**Option 1: Use existing credentials**
```bash
# Check the credentials file
cat config/dashboard_auth.json
```

**Option 2: Set environment variables**
```bash
export OMNIMIND_DASHBOARD_USER="your_username"
export OMNIMIND_DASHBOARD_PASS="your_password"
```

**Option 3: Regenerate credentials**
```bash
rm config/dashboard_auth.json
# Restart server to auto-generate new credentials
```

### 3. Module Import Errors

#### Symptom
```
ModuleNotFoundError: No module named 'xxx'
```

#### Diagnosis
```bash
# Check installed packages
pip list

# Run diagnostic
python scripts/diagnose.py --check-dependencies
```

#### Solution
```bash
# Install missing dependencies
pip install -r requirements.txt

# For GPU support
pip install -r requirements.txt torch torchvision --index-url https://download.pytorch.org/whl/cu124

# For CPU-only
pip install -r requirements-cpu.txt
```

### 4. Database Connection Errors

#### Symptom
```
Connection refused: Qdrant
```

#### Diagnosis
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Or
curl http://localhost:6333/health
```

#### Solution

**Start Qdrant with Docker:**
```bash
docker run -d -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/data/qdrant:/qdrant/storage \
  qdrant/qdrant
```

**Or start with docker-compose:**
```bash
docker-compose up -d qdrant
```

### 5. GPU/CUDA Not Detected

#### Symptom
```
CUDA not available
torch.cuda.is_available() returns False
```

#### Diagnosis
```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA installation
nvcc --version

# Run GPU diagnostic
python scripts/diagnose.py --check-gpu
```

#### Solution

**Reload nvidia_uvm module:**
```bash
# Kill processes using the module
sudo fuser --kill /dev/nvidia-uvm 2>/dev/null || true

# Reload module
sudo modprobe -r nvidia_uvm 2>/dev/null || true
sudo modprobe nvidia_uvm

# Verify
python -c "import torch; print(torch.cuda.is_available())"
```

**Reinstall CUDA-enabled PyTorch:**
```bash
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

### 6. WebSocket Connection Failures

#### Symptom
```
WebSocket connection failed
```

#### Diagnosis
```bash
# Test WebSocket endpoint
wscat -c ws://localhost:8000/ws

# Or use Python
python -c "
import websockets
import asyncio
async def test():
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        await ws.send('{\"type\": \"ping\"}')
        response = await ws.recv()
        print(response)
asyncio.run(test())
"
```

#### Solution

1. **Check server is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Verify WebSocket manager started:**
   ```bash
   # Check logs
   tail -f logs/backend.log | grep "WebSocket"
   ```

3. **Check firewall:**
   ```bash
   # Allow WebSocket connections
   sudo ufw allow 8000/tcp
   ```

### 7. High Memory Usage

#### Symptom
```
Out of memory errors
System becomes slow
```

#### Diagnosis
```bash
# Check memory usage
python scripts/diagnose.py --check-memory

# Monitor in real-time
htop

# Check OmniMind processes
ps aux | grep omnimind
```

#### Solution

**Reduce batch sizes:**
```yaml
# config/agent_config.yaml
orchestrator:
  max_concurrent_tasks: 5  # Reduce from 10
  max_iterations: 3  # Reduce from 5
```

**Clear cache:**
```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +

# Clear model cache
rm -rf ~/.cache/huggingface
```

**Restart with limited memory:**
```bash
# Limit memory for the process
systemd-run --scope -p MemoryLimit=8G uvicorn web.backend.main:app
```

### 8. Slow Performance

#### Symptom
```
API responses taking > 5 seconds
Tasks timing out
```

#### Diagnosis
```bash
# Run performance benchmark
python benchmarks/PHASE7_COMPLETE_BENCHMARK_AUDIT.py

# Check system resources
python scripts/diagnose.py --check-performance
```

#### Solution

See [Performance Tuning Guide](./PERFORMANCE_TUNING.md) for detailed optimization steps.

**Quick fixes:**
```bash
# 1. Reduce logging verbosity
export LOG_LEVEL=WARNING

# 2. Disable debug mode
export OMNIMIND_DEBUG=false

# 3. Use GPU if available
export OMNIMIND_USE_GPU=true

# 4. Increase worker count
uvicorn web.backend.main:app --workers 4
```

### 9. Audit Chain Integrity Errors

#### Symptom
```
Audit chain verification failed
Hash mismatch detected
```

#### Diagnosis
```bash
# Verify audit chain
python -c "from src.audit.immutable_audit import verify_chain; print(verify_chain())"

# Check logs
cat logs/audit_chain.log
```

#### Solution

**Rebuild audit chain:**
```bash
# Backup existing chain
cp logs/audit_chain.log logs/audit_chain.log.backup

# Verify and fix
python scripts/repair_audit_chain.py
```

**If chain is corrupted beyond repair:**
```bash
# Start fresh (only if acceptable to lose audit history)
rm logs/audit_chain.log logs/hash_chain.json
# Restart server to create new chain
```

### 10. Test Failures

#### Symptom
```
pytest failures
Import errors in tests
```

#### Diagnosis
```bash
# Run specific test with verbose output
pytest tests/test_api_documentation.py -vv

# Check test dependencies
python scripts/diagnose.py --check-test-deps
```

#### Solution

**Install test dependencies:**
```bash
pip install pytest pytest-cov pytest-asyncio
```

**Run tests in isolation:**
```bash
# Clear cache
pytest --cache-clear

# Run with fresh imports
pytest --forked tests/
```

## Automated Diagnostic Tools

### System Health Check

```bash
# Full system diagnostic
python scripts/diagnose.py --full

# Quick health check
python scripts/diagnose.py --quick
```

### Component-Specific Diagnostics

```bash
# Database connectivity
python scripts/diagnose.py --check-db

# GPU/CUDA status
python scripts/diagnose.py --check-gpu

# API endpoints
python scripts/diagnose.py --check-api

# File permissions
python scripts/diagnose.py --check-permissions

# Configuration validity
python scripts/diagnose.py --check-config
```

### Log Analysis

```bash
# Analyze error logs
python scripts/analyze_logs.py --errors-only

# Find performance bottlenecks
python scripts/analyze_logs.py --slow-requests

# Security event summary
python scripts/analyze_logs.py --security
```

## Debug Mode

Enable debug mode for detailed logging:

```bash
# Set environment variable
export OMNIMIND_DEBUG=true

# Or in config/omnimind.yaml
debug:
  enabled: true
  log_level: DEBUG
  trace_requests: true
```

View debug logs:
```bash
tail -f logs/debug.log
```

## Getting Help

### Community Support

- GitHub Issues: https://github.com/fabs-devbrain/OmniMind/issues
- Discussions: https://github.com/fabs-devbrain/OmniMind/discussions

### Bug Reports

When reporting bugs, include:

1. **System Information:**
   ```bash
   python scripts/diagnose.py --system-info > debug_info.txt
   ```

2. **Error Logs:**
   ```bash
   tail -n 100 logs/backend.log > error_logs.txt
   ```

3. **Steps to Reproduce:**
   - Exact commands run
   - Configuration used
   - Expected vs actual behavior

### Emergency Recovery

If system is completely broken:

```bash
# 1. Stop all services
pkill -f omnimind
docker-compose down

# 2. Backup data
tar -czf omnimind_backup_$(date +%Y%m%d).tar.gz \
  config/ logs/ data/

# 3. Clean installation
rm -rf .venv/
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4. Restore configuration
# (restore from backup if needed)

# 5. Restart services
source scripts/start_dashboard.sh
```

## Preventive Maintenance

### Regular Health Checks

Add to crontab for automated monitoring:

```cron
# Check system health every hour
0 * * * * /path/to/omnimind/scripts/diagnose.py --quick --alert-on-failure

# Run full diagnostic daily
0 3 * * * /path/to/omnimind/scripts/diagnose.py --full > /var/log/omnimind/diagnostic_$(date +\%Y\%m\%d).log
```

### Log Rotation

Configure log rotation to prevent disk space issues:

```bash
# /etc/logrotate.d/omnimind
/path/to/omnimind/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 omnimind omnimind
    sharedscripts
    postrotate
        systemctl reload omnimind-daemon
    endscript
}
```

## Performance Monitoring

Use built-in monitoring:

```bash
# Real-time metrics
curl -u user:pass http://localhost:8000/metrics

# WebSocket stats
curl -u user:pass http://localhost:8000/ws/stats

# System observability
curl -u user:pass http://localhost:8000/observability
```

## Additional Resources

- [Performance Tuning Guide](./PERFORMANCE_TUNING.md)
- [API Playground](./INTERACTIVE_API_PLAYGROUND.md)
- [System Architecture](../PHASE8_9_IMPLEMENTATION_COMPLETE.md)
- [Hardware Optimization](../HARDWARE_OPTIMIZATION_SUMMARY.md)
