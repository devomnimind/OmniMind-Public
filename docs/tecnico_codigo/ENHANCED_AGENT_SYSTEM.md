# 🤖 Enhanced Agent System - Documentation

## Overview

This document describes the enhanced agent system with advanced code analysis, inter-agent communication, and real-time monitoring capabilities.

## New Features

### 1. AST Parser Tool (`src/tools/ast_parser.py`)

Advanced Python code analysis using Abstract Syntax Tree (AST) parsing.

#### Capabilities

- **Code Parsing**: Complete structural analysis of Python code
- **Syntax Validation**: Check code syntax without execution
- **Security Analysis**: Detect dangerous patterns (eval, exec, etc.)
- **Structure Extraction**: Extract classes, functions, imports
- **Complexity Calculation**: Cyclomatic complexity metrics
- **Code Generation**: Generate class skeletons and templates

#### Usage Example

```python
from src.tools.ast_parser import ASTParser

parser = ASTParser()

# Validate syntax
is_valid, error = parser.validate_syntax(code)

# Analyze file structure
structure = parser.parse_file("src/mymodule.py")
print(f"Classes: {[c.name for c in structure.classes]}")
print(f"Functions: {[f.name for f in structure.functions]}")
print(f"Complexity: {structure.complexity}")

# Security analysis
warnings = parser.analyze_security_issues(code)
if warnings:
    print(f"Security issues found: {warnings}")

# Generate code skeleton
skeleton = parser.generate_skeleton(
    "UserService",
    methods=[
        ("get_user", ["user_id: str"], "User"),
        ("create_user", ["data: dict"], "User"),
    ],
    docstring="User management service"
)
```

### 2. Agent Communication Protocol (`src/agents/agent_protocol.py`)

Standardized message-based communication system for inter-agent coordination.

#### Message Types

- **REQUEST**: Request for action from another agent
- **RESPONSE**: Response to a request
- **NOTIFICATION**: One-way notification
- **TASK_DELEGATION**: Delegate task to another agent
- **TASK_COMPLETE**: Task completion notification
- **STATUS_UPDATE**: Agent status update
- **RESOURCE_REQUEST/GRANT/DENY**: Resource coordination

#### Priority Levels

- **CRITICAL**: Emergency situations (priority 0)
- **HIGH**: Urgent operations (priority 1)
- **MEDIUM**: Normal operations (priority 2)
- **LOW**: Background tasks (priority 3)

#### Usage Example

```python
from src.agents.agent_protocol import (
    AgentMessage,
    MessageType,
    MessagePriority,
    get_message_bus,
)
import uuid

# Get global message bus
bus = get_message_bus()
await bus.start()

# Register agents
bus.register_agent("code-agent-1")
bus.register_agent("architect-agent-1")

# Subscribe to message types
bus.subscribe("code-agent-1", [MessageType.TASK_DELEGATION])

# Send message
message = AgentMessage(
    message_id=str(uuid.uuid4()),
    message_type=MessageType.TASK_DELEGATION,
    sender="architect-agent-1",
    recipient="code-agent-1",
    payload={"task": "implement_feature", "spec": "Feature X"},
    priority=MessagePriority.HIGH,
)

await bus.send_message(message)

# Receive message (with timeout)
received = await bus.receive_message("code-agent-1", timeout=5.0)

# Send and wait for response
response = await bus.send_and_wait(message, timeout=10)

# Broadcast to all subscribed agents
await bus.broadcast(
    sender="orchestrator",
    message_type=MessageType.STATUS_UPDATE,
    payload={"status": "running"},
)
```

### 3. Enhanced CodeAgent

CodeAgent now includes advanced code analysis capabilities.

#### New Methods

**`analyze_code_structure(filepath: str) -> Dict[str, Any]`**
- Analyzes Python file structure
- Returns classes, functions, imports, dependencies, complexity

**`validate_code_syntax(code: str) -> Dict[str, Any]`**
- Validates Python code syntax
- Returns validation result and error message

**`analyze_code_security(code: str) -> Dict[str, Any]`**
- Detects security issues
- Returns warnings and severity level

**`generate_code_skeleton(class_name, methods, docstring) -> str`**
- Generates class template
- Returns formatted Python code

#### Usage Example

```python
from src.agents.code_agent import CodeAgent

agent = CodeAgent("config/agent_config.yaml")

# Analyze code structure
structure = agent.analyze_code_structure("src/mymodule.py")
print(f"Found {len(structure['classes'])} classes")
print(f"Complexity: {structure['complexity']}")

# Validate code
validation = agent.validate_code_syntax("def test(): return 42")
if validation["valid"]:
    print("Code is valid!")

# Check security
security = agent.analyze_code_security(code)
if not security["safe"]:
    print(f"Security warnings: {security['warnings']}")

# Generate code
skeleton = agent.generate_code_skeleton(
    "PaymentProcessor",
    methods=[
        ("process_payment", ["amount: float"], "bool"),
        ("refund", ["transaction_id: str"], "bool"),
    ],
)
```

### 4. Enhanced ArchitectAgent

ArchitectAgent now includes architecture analysis and documentation generation.

#### New Methods

**`analyze_dependencies(directory: str) -> Dict[str, Any]`**
- Analyzes project dependencies
- Scans requirements.txt, package.json
- Returns dependency breakdown

**`create_architecture_diagram(components, connections) -> str`**
- Generates Mermaid diagram
- Returns diagram in markdown format

**`generate_spec_document(title, sections, output_path) -> Dict[str, Any]`**
- Creates technical specification document
- Saves to markdown file
- Returns operation result

#### Usage Example

```python
from src.agents.architect_agent import ArchitectAgent

agent = ArchitectAgent("config/agent_config.yaml")

# Analyze dependencies
deps = agent.analyze_dependencies(".")
print(f"Total dependencies: {deps['total_deps']}")

# Create architecture diagram
diagram = agent.create_architecture_diagram(
    components=["Web UI", "API Server", "Database", "Cache"],
    connections=[
        ("Web UI", "API Server"),
        ("API Server", "Database"),
        ("API Server", "Cache"),
    ],
)

# Generate specification
result = agent.generate_spec_document(
    title="Authentication System",
    sections={
        "Overview": "JWT-based authentication with refresh tokens",
        "Components": "AuthService, TokenManager, UserRepository",
        "Security": "Passwords hashed with bcrypt, tokens expire after 1h",
    },
    output_path="docs/auth_spec.md",
)
```

### 5. Agent Communication Monitor (React Component)

Real-time monitoring interface for agent communication.

#### Features

- **Message Stream**: Live view of inter-agent messages
- **Queue Statistics**: Monitor message queues per agent
- **Conflict Resolution**: View conflict resolution history
- **Agent Filtering**: Filter messages by specific agent
- **Priority Indicators**: Visual priority levels

#### Usage

```tsx
import { AgentCommunicationMonitor } from './components/AgentCommunicationMonitor';

function DashboardPage() {
  return (
    <div>
      <AgentCommunicationMonitor />
    </div>
  );
}
```

## API Endpoints

### Agent Communication

**GET `/api/agents/communication/stats`**
- Returns message bus statistics
- Response: `{ message_bus: {...}, timestamp: number }`

**GET `/api/agents/communication/queue/{agent_id}`**
- Returns queue status for specific agent
- Response: `{ agent_id, queue_size, subscriptions, timestamp }`

**POST `/api/agents/communication/send`**
- Sends message between agents
- Request: `{ sender, recipient, message_type, payload, priority }`
- Response: `{ success, message_id, timestamp }`

### Code Analysis

**GET `/api/agents/ast/analyze/{filepath}`**
- Analyzes code structure
- Response: `{ classes, functions, imports, dependencies, complexity }`

**POST `/api/agents/ast/validate`**
- Validates code syntax
- Request: `{ code: string }`
- Response: `{ valid, error, timestamp }`

**POST `/api/agents/ast/security`**
- Analyzes code security
- Request: `{ code: string }`
- Response: `{ warnings, safe, severity, timestamp }`

## WebSocket Events

### Agent Communication Events

**`agent_message`**
- Triggered when agents exchange messages
- Payload: `{ message_id, message_type, sender, recipient, payload, priority, timestamp }`

**`agent_status`**
- Triggered on agent status updates
- Payload: `{ agent_id, status, timestamp }`

**`queue_stats`**
- Periodic queue statistics
- Payload: Array of `{ agent_id, queue_size, subscriptions }`

**`conflict_resolution`**
- Triggered when conflicts are resolved
- Payload: `{ conflict_id, agents_involved, conflict_type, resolution, winner, timestamp }`

## Testing

### Unit Tests

```bash
# Test AST parser
pytest tests/test_ast_parser.py -v

# Test agent protocol
pytest tests/test_agent_protocol.py -v

# Test integration
pytest tests/test_enhanced_agents_integration.py -v
```

### Coverage

All new features include comprehensive tests with >90% coverage.

## Security Considerations

### AST Parser
- Only analyzes code, never executes
- Detects dangerous patterns (eval, exec, subprocess)
- Safe to use on untrusted code

### Agent Communication
- Messages are logged for audit trail
- Priority-based queue prevents resource starvation
- Timeout mechanisms prevent deadlocks

### API Endpoints
- File path validation prevents directory traversal
- Only Python files can be analyzed
- Authentication required for all endpoints

## Performance

### AST Parser
- Typical file parsing: <100ms
- Complexity calculation: O(n) where n = number of nodes
- Caching for repeated analyses

### Message Bus
- Message delivery: <1ms average
- Queue operations: O(1) for send/receive
- Broadcast: O(n) where n = number of subscribers

## Future Enhancements

1. **Code Generation**
   - AI-powered code completion
   - Automatic refactoring suggestions
   - Pattern detection and recommendations

2. **Advanced Communication**
   - Message encryption
   - Priority escalation
   - Workflow orchestration

3. **Monitoring**
   - Performance metrics per agent
   - Communication pattern analysis
   - Anomaly detection

## Troubleshooting

### Common Issues

**"Message bus not running"**
- Ensure `await message_bus.start()` is called
- Check if lifespan is properly configured

**"Agent not registered"**
- Call `message_bus.register_agent(agent_id)` before use
- Verify agent_id is unique

**"File not found" on AST analysis**
- Verify file path is absolute
- Check file permissions
- Ensure file has .py extension

## Contributing

When adding new agent features:

1. Update relevant agent class
2. Add comprehensive tests
3. Update API documentation
4. Add frontend components if needed
5. Update this documentation

## References

- [Python AST Documentation](https://docs.python.org/3/library/ast.html)
- [Async/Await Best Practices](https://docs.python.org/3/library/asyncio.html)
- [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)
- [React Hooks](https://react.dev/reference/react)
