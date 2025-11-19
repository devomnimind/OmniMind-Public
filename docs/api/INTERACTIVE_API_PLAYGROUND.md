# Interactive API Playground Guide

## Overview

OmniMind provides an interactive API playground for exploring and testing API endpoints without writing code. This guide covers how to use the Swagger UI interface and Postman collections.

## Accessing the API Playground

### Swagger UI (Built-in)

The interactive API documentation is available at:

```
http://localhost:8000/docs
```

When the backend server is running, navigate to this URL to access the full interactive API playground.

### Alternative: ReDoc

For a different documentation style, access ReDoc at:

```
http://localhost:8000/redoc
```

## Using Swagger UI

### 1. Authentication

Most endpoints require Basic Authentication:

1. Click the **"Authorize"** button at the top right
2. Enter your credentials:
   - Username: Your dashboard username
   - Password: Your dashboard password
3. Click **"Authorize"**
4. Click **"Close"**

### 2. Exploring Endpoints

Endpoints are organized by tags:

- **System**: Health checks and system information
- **Tasks**: Task management and orchestration
- **Agents**: Agent status and control
- **Security**: Security events and monitoring
- **Metacognition**: AI self-reflection insights

### 3. Testing Endpoints

To test an endpoint:

1. Click on the endpoint to expand it
2. Click **"Try it out"**
3. Fill in required parameters
4. Click **"Execute"**
5. View the response below

### 4. Example Requests

Each endpoint includes example requests and responses. Click on "Example Value" to see sample data.

## Postman Collections

### Importing the Collection

1. Generate the Postman collection:
   ```bash
   python -c "from src.security.api_documentation import APIDocumentationGenerator; gen = APIDocumentationGenerator(); gen.generate_postman_collection()"
   ```

2. Import into Postman:
   - Open Postman
   - Click **"Import"**
   - Select `docs/api/OmniMind_API.postman_collection.json`
   - Click **"Import"**

### Setting Up Environment Variables

Create a Postman environment with these variables:

```json
{
  "name": "OmniMind Local",
  "values": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "enabled": true
    },
    {
      "key": "username",
      "value": "your_username",
      "enabled": true
    },
    {
      "key": "password",
      "value": "your_password",
      "enabled": true,
      "type": "secret"
    }
  ]
}
```

### Using the Collection

1. Select the "OmniMind Local" environment
2. Navigate to the desired request folder
3. Click on a request
4. Click **"Send"**
5. View the response

## Common API Workflows

### 1. Health Check

```bash
GET /health
```

No authentication required. Returns system health status.

### 2. Submit a Task

```bash
POST /tasks/orchestrate
Authorization: Basic <credentials>

{
  "task": "Analyze system performance",
  "max_iterations": 3
}
```

### 3. Check Task Status

```bash
GET /tasks/{task_id}
Authorization: Basic <credentials>
```

### 4. View Metrics

```bash
GET /metrics
Authorization: Basic <credentials>
```

### 5. Get Security Events

```bash
GET /security/events
Authorization: Basic <credentials>
```

## API Rate Limits

Currently, there are no hard rate limits, but consider:

- Maximum 100 concurrent requests
- Websocket connections: 50 simultaneous connections
- Task orchestration: 10 concurrent tasks

## Response Formats

All responses are in JSON format:

### Success Response
```json
{
  "status": "success",
  "data": { ... }
}
```

### Error Response
```json
{
  "error": "Error description",
  "detail": "Detailed error message",
  "code": "ERROR_CODE"
}
```

## Advanced Features

### WebSocket Testing

For real-time updates, use the WebSocket endpoint:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    channels: ['tasks', 'agents', 'security']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

### Batch Operations

Some endpoints support batch operations:

```bash
POST /tasks/batch
Authorization: Basic <credentials>

{
  "tasks": [
    {"description": "Task 1", "priority": "high"},
    {"description": "Task 2", "priority": "medium"}
  ]
}
```

## Troubleshooting

### Authentication Errors

**Error:** 401 Unauthorized

**Solution:**
1. Verify credentials in `config/dashboard_auth.json`
2. Check environment variables:
   ```bash
   echo $OMNIMIND_DASHBOARD_USER
   echo $OMNIMIND_DASHBOARD_PASS
   ```

### Connection Refused

**Error:** Connection refused to localhost:8000

**Solution:**
1. Start the backend server:
   ```bash
   source scripts/start_dashboard.sh
   ```
2. Verify server is running:
   ```bash
   curl http://localhost:8000/health
   ```

### CORS Errors

**Error:** CORS policy blocked

**Solution:**
The server allows all origins by default. If you're having issues:
1. Check that you're accessing from the correct origin
2. Verify the server configuration in `web/backend/main.py`

## SDK Code Examples

### Python

```python
from omnimind_sdk import OmniMindClient

client = OmniMindClient(
    base_url="http://localhost:8000",
    username="your_username",
    password="your_password"
)

# Submit task
task = client.submit_task(
    description="Analyze security vulnerabilities",
    priority="high"
)

# Get task status
status = client.get_task(task['task_id'])
print(f"Task status: {status['status']}")

# List all tasks
tasks = client.list_tasks(status="running")
```

### JavaScript

```javascript
import { OmniMindClient } from './omnimind-sdk';

const client = new OmniMindClient({
  baseUrl: 'http://localhost:8000',
  username: 'your_username',
  password: 'your_password'
});

// Submit task
const task = await client.submitTask({
  description: 'Analyze security vulnerabilities',
  priority: 'high'
});

// Get task status
const status = await client.getTask(task.task_id);
console.log(`Task status: ${status.status}`);

// List all tasks
const tasks = await client.listTasks({ status: 'running' });
```

## Additional Resources

- [API Reference](./API_DOCUMENTATION.md)
- [Authentication Guide](./AUTHENTICATION.md)
- [WebSocket Guide](./WEBSOCKET_GUIDE.md)
- [Performance Tuning](./PERFORMANCE_TUNING.md)
- [Troubleshooting](./TROUBLESHOOTING.md)
