# Load Testing with k6

## Overview

This directory contains load testing scripts for OmniMind using [k6](https://k6.io/), a modern load testing tool.

## Installation

### Install k6

**macOS:**
```bash
brew install k6
```

**Linux:**
```bash
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-update
sudo apt-get install k6
```

**Windows:**
```powershell
choco install k6
```

**Docker:**
```bash
docker pull grafana/k6
```

## Running Load Tests

### Basic Usage

```bash
# Run load test with default settings
k6 run tests/load_tests/api_load_test.js

# Run with custom environment variables
k6 run --env BASE_URL=http://localhost:8000 \
       --env USERNAME=your_user \
       --env PASSWORD=your_pass \
       tests/load_tests/api_load_test.js
```

### Advanced Options

```bash
# Run with different number of virtual users
k6 run --vus 50 --duration 30s tests/load_tests/api_load_test.js

# Run with custom stages
k6 run --stage 30s:10,1m:50,30s:0 tests/load_tests/api_load_test.js

# Output results to different formats
k6 run --out json=test_results.json tests/load_tests/api_load_test.js
k6 run --out influxdb=http://localhost:8086/k6 tests/load_tests/api_load_test.js
```

### Docker Usage

```bash
# Run test in Docker
docker run --rm -i \
  -v $(pwd)/tests/load_tests:/scripts \
  -e BASE_URL=http://host.docker.internal:8000 \
  grafana/k6 run /scripts/api_load_test.js
```

## Test Scenarios

### api_load_test.js

Main API load test that simulates realistic user behavior:

**Stages:**
1. Ramp up to 10 users over 30s
2. Ramp up to 50 users over 1m
3. Hold at 50 users for 2m
4. Spike to 100 users over 30s
5. Hold at 100 users for 1m
6. Ramp down to 0 users over 30s

**Tested Endpoints:**
- Health check (no auth)
- Metrics (with auth)
- Status (with auth)
- Task orchestration (with auth)
- WebSocket stats (with auth)

**SLA Thresholds:**
- 95% of requests complete under 500ms
- Less than 10% request failure rate
- Less than 10% error rate

## Integration with Grafana

### Setup Grafana + InfluxDB

1. **Start InfluxDB:**
```bash
docker run -d -p 8086:8086 \
  -v influxdb:/var/lib/influxdb \
  influxdb:1.8
```

2. **Create k6 database:**
```bash
curl -i -XPOST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE k6"
```

3. **Run k6 with InfluxDB output:**
```bash
k6 run --out influxdb=http://localhost:8086/k6 tests/load_tests/api_load_test.js
```

4. **Start Grafana:**
```bash
docker run -d -p 3001:3000 grafana/grafana
```

5. **Configure Grafana:**
- Open http://localhost:3001
- Add InfluxDB data source (URL: http://localhost:8086, Database: k6)
- Import k6 dashboard (ID: 2587)

## Continuous Load Testing

### CI/CD Integration

Add to GitHub Actions:

```yaml
name: Load Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Run daily at 2 AM
  workflow_dispatch:

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup k6
        run: |
          sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6
      
      - name: Start Backend
        run: |
          uvicorn web.backend.main:app --port 8000 &
          sleep 5
      
      - name: Run Load Tests
        run: |
          k6 run tests/load_tests/api_load_test.js
      
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: load-test-results
          path: logs/load_test_*.json
```

## Interpreting Results

### Key Metrics

**http_req_duration**: Response time
- avg: Average response time
- p(95): 95th percentile (95% of requests faster than this)
- p(99): 99th percentile

**http_reqs**: Total number of HTTP requests

**http_req_failed**: Percentage of failed requests

**iterations**: Number of test iterations completed

### Good Performance Indicators

✅ p95 response time < 500ms
✅ p99 response time < 1000ms
✅ Error rate < 1%
✅ Successful completion of all stages

### Warning Signs

⚠️ p95 > 1000ms: Response times degrading
⚠️ Error rate > 5%: System under stress
⚠️ Failed requests: Backend issues
⚠️ Timeouts: Resource exhaustion

## Custom Test Scenarios

### Create Custom Test

```javascript
import http from 'k6/http';
import { check } from 'k6';

export const options = {
    vus: 10,
    duration: '30s',
};

export default function () {
    const res = http.get('http://localhost:8000/your-endpoint');
    check(res, {
        'status is 200': (r) => r.status === 200,
    });
}
```

### Run Custom Test

```bash
k6 run your_test.js
```

## Troubleshooting

### Connection Refused

**Problem:** k6 can't connect to backend

**Solution:**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Start backend
uvicorn web.backend.main:app --port 8000
```

### Authentication Errors

**Problem:** 401 Unauthorized errors

**Solution:**
```bash
# Set correct credentials
k6 run --env USERNAME=your_user --env PASSWORD=your_pass tests/load_tests/api_load_test.js
```

### Out of Memory

**Problem:** k6 runs out of memory with many VUs

**Solution:**
```bash
# Reduce virtual users or duration
k6 run --vus 20 --duration 1m tests/load_tests/api_load_test.js

# Or increase system resources
```

## Best Practices

1. **Start Small**: Begin with low load and gradually increase
2. **Monitor Server**: Watch server metrics during tests
3. **Realistic Scenarios**: Model actual user behavior
4. **Regular Testing**: Run load tests regularly to catch regressions
5. **Document Baselines**: Keep records of baseline performance
6. **Test in Isolation**: Avoid running other processes during tests

## Additional Resources

- [k6 Documentation](https://k6.io/docs/)
- [k6 Examples](https://k6.io/docs/examples/)
- [Grafana k6 Cloud](https://k6.io/cloud/)
- [Performance Testing Guide](../../docs/api/PERFORMANCE_TUNING.md)
