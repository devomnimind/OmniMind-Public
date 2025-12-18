# 🚀 OMNIMIND PRODUCTION DEPLOYMENT GUIDE

## ✅ Pre-Deployment Checklist

### Security
- [ ] All secrets in `.env` (never in code)
- [ ] TLS/SSL certificates configured
- [ ] Firewall rules in place (allow 4321-4360 internally only)
- [ ] Rate limiting enabled on endpoints
- [ ] API authentication configured

### Configuration
- [ ] `OMNIMIND_ENV=production` set
- [ ] Database credentials verified
- [ ] Redis connectivity tested
- [ ] Backup paths configured and tested
- [ ] Log rotation configured

### Infrastructure
- [ ] 4GB+ RAM available
- [ ] 4+ CPU cores
- [ ] 500GB+ storage
- [ ] Network connectivity verified
- [ ] DNS records configured

### Monitoring
- [ ] Health check endpoints tested
- [ ] Prometheus scraping configured
- [ ] Grafana dashboards created
- [ ] Alert rules configured
- [ ] Log aggregation (ELK/Datadog/etc) configured

## 🚀 Deployment Steps

### 1. Prepare System

```bash
# Create omnimind user
sudo useradd -r -s /bin/bash -d /opt/omnimind omnimind

# Create directories
sudo mkdir -p /opt/omnimind/{logs,data,backups,config}
sudo chown -R omnimind:omnimind /opt/omnimind

# Set permissions
sudo chmod 700 /opt/omnimind
```

### 2. Install OmniMind

```bash
# Clone/pull repository
cd /opt/omnimind
git clone https://github.com/your-org/omnimind .

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-prod.txt

# Create .env
cp .env.example .env
# Edit with production values
nano .env
```

### 3. Configure Systemd

```bash
# Copy service file
sudo cp config/systemd/omnimind.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable omnimind.service
sudo systemctl start omnimind.service

# Verify
sudo systemctl status omnimind.service
```

### 4. Configure Backup

```bash
# Make script executable
chmod +x scripts/production/backup_omnimind.sh

# Add to crontab (daily at 00:00)
sudo -u omnimind crontab -e

# Add:
0 0 * * * /opt/omnimind/scripts/production/backup_omnimind.sh
```

### 5. Configure Monitoring

```bash
# Copy prometheus config
cp config/prometheus/omnimind.yml /etc/prometheus/

# Reload Prometheus
sudo systemctl reload prometheus

# Verify metrics
curl http://127.0.0.1:9090/api/v1/query?query=omnimind_up
```

### 6. Health Check Verification

```bash
# Test endpoints
curl http://127.0.0.1:4360/health
curl http://127.0.0.1:4360/ready
curl http://127.0.0.1:4350/status
curl http://127.0.0.1:4350/dashboard
```

## 📊 Post-Deployment Validation

### Service Status
```bash
systemctl status omnimind.service
journalctl -u omnimind.service -f
```

### MCP Status
```bash
curl -s http://127.0.0.1:4350/status | python -m json.tool
```

### Health Check
```bash
curl -s http://127.0.0.1:4360/health | python -m json.tool
```

### Dashboard
```
Open browser: http://your-server:4350/dashboard
```

## 🔄 Monitoring & Alerting

### Prometheus Queries

```promql
# Availability
omnimind_up

# MCP Health
omnimind_health_mcps_up

# Response Time
histogram_quantile(0.99, omnimind_response_time_ms)

# Error Rate
increase(omnimind_errors_total[5m])
```

### Key Dashboards

1. **Overview**: System health, uptime, throughput
2. **Performance**: Latency percentiles, error rates
3. **Resources**: CPU, memory, disk, network
4. **MCPs**: Individual MCP status and metrics

## 🚨 Incident Response

### If Service Down

```bash
# 1. Check status
systemctl status omnimind.service

# 2. View logs
journalctl -u omnimind.service -n 100

# 3. Restart (if needed)
systemctl restart omnimind.service

# 4. Health check
curl http://127.0.0.1:4360/health
```

### If Performance Degraded

```bash
# Check resource usage
top -u omnimind

# Check MCP status
curl http://127.0.0.1:4350/metrics | python -m json.tool

# Check disk space
df -h /opt/omnimind

# Restart if needed
systemctl restart omnimind.service
```

## 🔄 Backup & Recovery

### Manual Backup
```bash
/opt/omnimind/scripts/production/backup_omnimind.sh
```

### List Backups
```bash
ls -lh /opt/omnimind/backups/
```

### Restore from Backup
```bash
cd /opt/omnimind
tar -xzf backups/omnimind_backup_YYYYMMDD_HHMMSS.tar.gz
systemctl restart omnimind.service
```

## 📈 Scaling

### Horizontal Scaling (Multiple Instances)
1. Set up load balancer (nginx/haproxy)
2. Deploy additional instances
3. Update health check endpoints
4. Configure shared data store (Redis/Postgres)

### Vertical Scaling (Bigger Instance)
1. Increase memory: Edit systemd config
2. Increase CPU: Update resource limits
3. Increase storage: Expand disk/add volumes

## 🔐 Security Best Practices

- ✅ Run as non-root user (omnimind)
- ✅ Restrict network access (firewall)
- ✅ Use TLS for all external communication
- ✅ Rotate secrets regularly
- ✅ Enable audit logging
- ✅ Monitor for unauthorized access
- ✅ Keep dependencies updated

## 📚 Useful Commands

```bash
# Service management
systemctl start omnimind.service
systemctl stop omnimind.service
systemctl restart omnimind.service
systemctl reload omnimind.service

# Monitoring
journalctl -u omnimind.service -f
journalctl -u omnimind.service --since "1 hour ago"

# Health checks
curl http://127.0.0.1:4360/health
curl http://127.0.0.1:4360/ready

# Database
curl -X POST http://127.0.0.1:4334/backup

# Restart individual MCP
systemctl restart omnimind-mcp-4321.service  # if using per-MCP services
```

---

**Version**: 1.0
**Date**: 2025-12-17
**Maintainer**: OmniMind DevOps Team
