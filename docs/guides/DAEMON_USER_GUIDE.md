# OmniMind Daemon - User Guide

## What is the OmniMind Daemon?

The OmniMind Daemon is **NOT a chatbot**. It's a 24/7 autonomous background service that works for you even while you sleep. It monitors your system, executes tasks proactively, and helps maximize your productivity without requiring constant interaction.

### Key Characteristics

- **Always Running:** Works 24/7 in the background
- **Proactive:** Initiates tasks based on system state, not user prompts
- **Smart Scheduling:** Knows when to work (idle time, sleep hours)
- **Local-First:** All processing happens on your machine
- **Cloud-Ready:** Can integrate with Supabase and Qdrant when needed

## Installation

### Prerequisites

- Python 3.12.8
- Linux system with systemd
- Virtual environment set up

### Installation Steps

1. **Install Dependencies:**
   ```bash
   cd ~/projects/omnimind
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Install Daemon Service:**
   ```bash
   ./scripts/install_daemon.sh
   ```

3. **Start the Daemon:**
   ```bash
   sudo systemctl start omnimind-daemon
   ```

4. **Enable Auto-Start:**
   ```bash
   sudo systemctl enable omnimind-daemon
   ```

## Managing the Daemon

### Check Status
```bash
sudo systemctl status omnimind-daemon
```

### View Live Logs
```bash
sudo journalctl -u omnimind-daemon -f
```

### Stop Daemon
```bash
sudo systemctl stop omnimind-daemon
```

### Restart Daemon
```bash
sudo systemctl restart omnimind-daemon
```

## Default Background Tasks

The daemon comes with 4 pre-configured tasks that run automatically:

### 1. Code Analysis (Priority: HIGH)
- **When:** Runs during idle time (CPU < 20%, user inactive)
- **Frequency:** Every 2 hours
- **What it does:**
  - Analyzes codebase for issues
  - Checks for security vulnerabilities
  - Suggests improvements
  - Updates documentation

### 2. Test Optimization (Priority: LOW)
- **When:** Runs during sleep hours (00:00-06:00)
- **Frequency:** Once per day
- **What it does:**
  - Runs test suite
  - Identifies slow tests
  - Suggests performance improvements
  - Generates optimization reports

### 3. Research Paper Reading (Priority: LOW)
- **When:** Runs during sleep hours
- **Frequency:** Once per day
- **What it does:**
  - Fetches recent papers from ArXiv
  - Summarizes key findings
  - Stores insights in knowledge base
  - Suggests relevant papers for your work

### 4. Database Optimization (Priority: MEDIUM)
- **When:** Runs during idle time
- **Frequency:** Every 6 hours
- **What it does:**
  - Analyzes query performance
  - Suggests index improvements
  - Cleans up old data
  - Optimizes database configuration

## Task Priority System

The daemon uses a smart priority system to decide when to execute tasks:

- **CRITICAL (0):** Execute immediately, regardless of system state
- **HIGH (1):** Execute when system is idle (CPU < 20%)
- **MEDIUM (2):** Execute during low-activity periods
- **LOW (3):** Execute during sleep hours (00:00-06:00)

## System Monitoring

The daemon continuously monitors:

- **CPU Usage:** Tracks processor utilization
- **Memory Usage:** Monitors RAM consumption
- **Disk Usage:** Checks available storage
- **User Activity:** Detects when you're actively using the system

It uses this information to make intelligent decisions about when to run tasks.

## API Endpoints

The daemon exposes several REST API endpoints through the FastAPI backend:

### Get Daemon Status
```bash
GET /daemon/status
Authorization: Basic <credentials>
```

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

### List All Tasks
```bash
GET /daemon/tasks
Authorization: Basic <credentials>
```

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
    }
  ],
  "total_tasks": 4
}
```

### Add Custom Task
```bash
POST /daemon/tasks/add
Authorization: Basic <credentials>
Content-Type: application/json

{
  "task_id": "my_custom_task",
  "name": "My Custom Task",
  "description": "Does something useful",
  "priority": "MEDIUM",
  "code": "def execute():\n    return {'status': 'done'}",
  "repeat_hours": 4
}
```

### Start/Stop Daemon via API
```bash
POST /daemon/start
POST /daemon/stop
Authorization: Basic <credentials>
```

## Configuration

### Environment Variables

- `OMNIMIND_WORKSPACE`: Path to your workspace (default: current directory)
- `DAEMON_CHECK_INTERVAL`: How often to check for tasks in seconds (default: 30)
- `OMNIMIND_CLOUD_ENABLED`: Enable cloud integrations (default: true)
- `HUGGINGFACE_TOKEN`: Your Hugging Face Pro API token

### Customizing Sleep Hours

Edit `src/daemon/omnimind_daemon.py`:

```python
def is_sleep_time(self) -> bool:
    """Determine if it's sleep time"""
    hour = self.timestamp.hour
    # Customize these hours as needed
    return 0 <= hour < 6  # Default: 00:00-06:00
```

### Adjusting Idle Thresholds

```python
def is_idle(self) -> bool:
    """Determine if system is idle"""
    return (
        self.cpu_percent < 20.0      # Adjust CPU threshold
        and self.memory_percent < 80.0  # Adjust memory threshold
        and not self.user_active
    )
```

## Troubleshooting

### Daemon Won't Start

1. **Check Python Environment:**
   ```bash
   which python
   python --version  # Should be 3.12.8
   ```

2. **Check Dependencies:**
   ```bash
   pip list | grep -E "(psutil|structlog|fastapi)"
   ```

3. **Check Logs:**
   ```bash
   sudo journalctl -u omnimind-daemon --no-pager -n 50
   ```

### High CPU Usage

The daemon should have minimal CPU impact. If you notice high usage:

1. Check which task is running: Look at logs
2. Adjust task priorities or intervals
3. Increase `DAEMON_CHECK_INTERVAL` to reduce monitoring frequency

### Tasks Not Running

1. **Check system metrics:** Daemon might be waiting for idle time
2. **Check task schedule:** Task might not be due yet
3. **Check logs:** Look for errors in task execution

## Best Practices

### For Development

1. **Test in Safe Mode:** Start daemon manually first before installing service
2. **Monitor Logs:** Keep an eye on logs during initial setup
3. **Incremental Tasks:** Start with simple tasks, add complex ones gradually

### For Production

1. **Set Resource Limits:** Configure systemd service with memory/CPU limits
2. **Regular Monitoring:** Check daemon health weekly
3. **Task Validation:** Test new custom tasks before adding to production daemon
4. **Backup Configuration:** Keep a copy of your custom tasks

## Cloud Integration (Coming in Phase 9.2)

The daemon is ready to integrate with:

- **Supabase Free Tier:** For persistent storage and real-time sync
- **Qdrant Cloud Free Tier:** For vector storage and semantic search
- **Hugging Face Pro:** For advanced model inference when local GPU isn't sufficient

Integration steps will be documented in Phase 9.2.

## Philosophy: Why NOT a Chatbot?

Traditional chatbots are **reactive** - they wait for you to ask questions. The OmniMind Daemon is **proactive** - it works independently, making decisions about what needs to be done and when.

**Chatbot Model:**
```
You: "Analyze my code"
Bot: "Here's the analysis..."
[Waits for next command]
```

**Daemon Model:**
```
[2:00 AM - You're sleeping]
Daemon: *Analyzes code automatically*
Daemon: *Runs tests*
Daemon: *Reads latest research papers*
Daemon: *Optimizes database*

[8:00 AM - You wake up]
You: *Checks dashboard*
Everything is already done! ✨
```

## Contributing

To add new default tasks, edit `src/daemon/omnimind_daemon.py`:

```python
def create_default_tasks() -> List[DaemonTask]:
    tasks = []
    
    # Add your new task here
    def my_new_task():
        logger.info("task.my_new_task.running")
        # Your code here
        return {"status": "completed"}
    
    tasks.append(DaemonTask(
        task_id="my_new_task",
        name="My New Task",
        description="What this task does",
        priority=TaskPriority.MEDIUM,
        execute_fn=my_new_task,
        repeat_interval=timedelta(hours=4),
    ))
    
    return tasks
```

## Support

For issues and questions:

1. Check logs: `sudo journalctl -u omnimind-daemon -f`
2. Check GitHub issues: https://github.com/fabs-devbrain/OmniMind/issues
3. Review documentation: `docs/` directory

---

**Remember:** The daemon is designed to work **for you**, not **with you**. Let it run in the background and focus on your creative work!
