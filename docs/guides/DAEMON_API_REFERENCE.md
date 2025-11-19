# OmniMind Daemon API Reference

## Overview

The OmniMind Daemon exposes a REST API through the FastAPI backend. All endpoints require Basic Authentication.

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints require HTTP Basic Authentication:

```bash
curl -u <username>:<password> http://localhost:8000/daemon/status
```

Credentials are either:
- Set via environment variables: `OMNIMIND_DASHBOARD_USER` and `OMNIMIND_DASHBOARD_PASS`
- Auto-generated and stored in: `config/dashboard_auth.json`

## Endpoints

### 1. Get Daemon Status

**Endpoint:** `GET /daemon/status`

**Description:** Returns the current state of the daemon and system metrics.

**Response:**
```json
{
  "state": "idle",
  "running": true,
  "tasks_registered": 4,
  "tasks_pending": 2,
  "metrics": {
    "cpu_percent": 15.2,
    "memory_percent": 45.8,
    "is_idle": true,
    "is_sleep_time": false
  },
  "cloud_enabled": true,
  "workspace": "/home/fabricio/projects/omnimind"
}
```

**State Values:**
- `initializing` - Daemon is starting up
- `idle` - Daemon is running but no tasks executing
- `working` - Currently executing a task
- `sleeping` - Sleep mode (low-priority tasks active)
- `shutting_down` - Daemon is stopping
- `error` - Daemon encountered an error

### 2. List All Tasks

**Endpoint:** `GET /daemon/tasks`

**Description:** Returns all registered daemon tasks with their execution statistics.

**Response:**
```json
{
  "tasks": [
    {
      "task_id": "code_analysis",
      "name": "Code Analysis",
      "description": "Analyze codebase for issues and improvements",
      "priority": "HIGH",
      "execution_count": 12,
      "success_count": 11,
      "failure_count": 1,
      "last_execution": "2025-11-19T02:30:00Z",
      "repeat_interval": "2:00:00"
    },
    {
      "task_id": "test_optimization",
      "name": "Test Optimization",
      "description": "Optimize test suite performance",
      "priority": "LOW",
      "execution_count": 5,
      "success_count": 5,
      "failure_count": 0,
      "last_execution": "2025-11-19T03:00:00Z",
      "repeat_interval": "1 day, 0:00:00"
    }
  ],
  "total_tasks": 2
}
```

### 3. Add Custom Task

**Endpoint:** `POST /daemon/tasks/add`

**Description:** Dynamically add a custom task to the daemon.

**Request Body:**
```json
{
  "task_id": "my_custom_task",
  "name": "My Custom Task",
  "description": "Does something useful",
  "priority": "MEDIUM",
  "code": "def execute():\n    print('Running custom task')\n    return {'status': 'done', 'result': 42}",
  "repeat_hours": 4
}
```

**Parameters:**
- `task_id` (string, required): Unique identifier for the task
- `name` (string, required): Human-readable task name
- `description` (string, required): Task description
- `priority` (string, required): One of `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`
- `code` (string, required): Python code defining an `execute()` function
- `repeat_hours` (integer, optional): Hours between task executions

**Response:**
```json
{
  "status": "task_added",
  "task_id": "my_custom_task",
  "message": "Task 'My Custom Task' added successfully"
}
```

**Error Responses:**

400 Bad Request - Invalid priority:
```json
{
  "detail": "Invalid priority: INVALID"
}
```

400 Bad Request - Missing execute function:
```json
{
  "detail": "Code must define an 'execute()' function"
}
```

### 4. Start Daemon

**Endpoint:** `POST /daemon/start`

**Description:** Start the daemon in background mode.

**Response:**
```json
{
  "status": "started",
  "message": "Daemon started successfully"
}
```

If already running:
```json
{
  "status": "already_running",
  "message": "Daemon is already running"
}
```

### 5. Stop Daemon

**Endpoint:** `POST /daemon/stop`

**Description:** Stop the daemon gracefully.

**Response:**
```json
{
  "status": "stopped",
  "message": "Daemon stopped successfully"
}
```

If not running:
```json
{
  "status": "not_running",
  "message": "Daemon is not running"
}
```

## Task Priority Levels

| Priority | Value | When Executed |
|----------|-------|---------------|
| CRITICAL | 0 | Always, immediately |
| HIGH | 1 | When system is idle (CPU < 20%) |
| MEDIUM | 2 | During low-activity periods |
| LOW | 3 | During sleep hours (00:00-06:00) |

## Custom Task Code Requirements

When adding custom tasks via `/daemon/tasks/add`, the code must:

1. Define an `execute()` function
2. Return a dictionary (optional but recommended)
3. Be valid Python 3.12+ code

**Example 1: Simple Task**
```python
def execute():
    print("Hello from custom task!")
    return {"status": "completed"}
```

**Example 2: Task with Logic**
```python
def execute():
    import os
    workspace = os.getenv("OMNIMIND_WORKSPACE", ".")
    file_count = len(os.listdir(workspace))
    
    return {
        "status": "completed",
        "workspace": workspace,
        "file_count": file_count
    }
```

**Example 3: Async Task**
```python
async def execute():
    import asyncio
    await asyncio.sleep(1)
    return {"status": "completed", "waited": "1 second"}
```

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid credentials
- `500 Internal Server Error` - Server error

Error responses include a `detail` field:
```json
{
  "detail": "Error message here"
}
```

## Rate Limiting

Currently no rate limiting is implemented. For production use, consider adding rate limiting at the reverse proxy level.

## WebSocket Support

**Coming in Phase 9.3:** Real-time daemon status updates via WebSocket.

```javascript
// Future implementation
const ws = new WebSocket('ws://localhost:8000/daemon/ws');
ws.onmessage = (event) => {
  const status = JSON.parse(event.data);
  console.log('Daemon state:', status.state);
};
```

## Integration Examples

### Python Client

```python
import requests
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth('username', 'password')
base_url = 'http://localhost:8000'

# Get status
response = requests.get(f'{base_url}/daemon/status', auth=auth)
status = response.json()
print(f"Daemon state: {status['state']}")

# List tasks
response = requests.get(f'{base_url}/daemon/tasks', auth=auth)
tasks = response.json()
print(f"Total tasks: {tasks['total_tasks']}")

# Add custom task
new_task = {
    "task_id": "backup_db",
    "name": "Database Backup",
    "description": "Backup PostgreSQL database",
    "priority": "HIGH",
    "code": """
def execute():
    import subprocess
    result = subprocess.run(['pg_dump', 'mydb'], capture_output=True)
    return {'status': 'completed', 'size': len(result.stdout)}
    """,
    "repeat_hours": 24
}

response = requests.post(
    f'{base_url}/daemon/tasks/add',
    json=new_task,
    auth=auth
)
print(response.json())
```

### JavaScript/TypeScript Client

```typescript
const baseUrl = 'http://localhost:8000';
const auth = btoa('username:password');

async function getDaemonStatus() {
  const response = await fetch(`${baseUrl}/daemon/status`, {
    headers: {
      'Authorization': `Basic ${auth}`
    }
  });
  
  return await response.json();
}

async function addCustomTask(task) {
  const response = await fetch(`${baseUrl}/daemon/tasks/add`, {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${auth}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(task)
  });
  
  return await response.json();
}

// Usage
const status = await getDaemonStatus();
console.log('Daemon state:', status.state);
```

### cURL Examples

```bash
# Get status
curl -u username:password http://localhost:8000/daemon/status

# List tasks
curl -u username:password http://localhost:8000/daemon/tasks

# Add task
curl -u username:password \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "my_task",
    "name": "My Task",
    "description": "Example task",
    "priority": "MEDIUM",
    "code": "def execute():\n    return {\"status\": \"done\"}",
    "repeat_hours": 2
  }' \
  http://localhost:8000/daemon/tasks/add

# Start daemon
curl -u username:password -X POST http://localhost:8000/daemon/start

# Stop daemon
curl -u username:password -X POST http://localhost:8000/daemon/stop
```

## Security Considerations

### Authentication

- Always use HTTPS in production
- Rotate credentials regularly
- Store credentials in environment variables, never in code

### Custom Task Code

- Custom task code is executed with full Python privileges
- **This is safe for single-user local deployment**
- **DO NOT expose `/daemon/tasks/add` to untrusted users**
- For multi-user scenarios, implement sandboxing (e.g., RestrictedPython, Docker containers)

### Network Access

- Bind to `127.0.0.1` (localhost) for maximum security
- Use reverse proxy (nginx/caddy) for external access
- Implement IP whitelisting at firewall level

## Monitoring and Observability

### Metrics Endpoint

The daemon integrates with the existing `/metrics` endpoint:

```bash
curl -u username:password http://localhost:8000/metrics
```

Includes daemon-specific metrics in future updates.

### Logging

All daemon activity is logged to:
- systemd journal: `sudo journalctl -u omnimind-daemon`
- Structured JSON logs (when configured)

## Changelog

### Version 0.1.0 (Phase 9 - November 2025)

- Initial daemon API implementation
- Status endpoint
- Task listing endpoint
- Custom task addition
- Start/stop endpoints
- Basic authentication

### Planned Features (Phase 9.2+)

- WebSocket support for real-time updates
- Task execution history endpoint
- Task cancellation endpoint
- Batch task operations
- Advanced filtering and sorting
- Prometheus metrics export

---

**Note:** This API is designed for local single-user deployment. For multi-user or cloud deployments, additional security measures are required.
