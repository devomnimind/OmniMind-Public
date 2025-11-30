# OmniMind Frontend - React TypeScript Dashboard

## Overview

Modern React TypeScript frontend for OmniMind daemon monitoring and task management.

## Tech Stack

- **React 18** - UI framework
- **TypeScript 5.2+** - Type safety
- **Vite 5** - Build tool and dev server
- **Zustand 4.5** - State management
- **TailwindCSS 3.4** - Styling
- **ESLint** - Code quality

## Project Structure

```
web/frontend/
├── src/
│   ├── components/         # React components
│   │   ├── Dashboard.tsx       # Main dashboard layout
│   │   ├── DaemonStatus.tsx    # Daemon status display
│   │   ├── DaemonControls.tsx  # Start/stop controls
│   │   ├── SystemMetrics.tsx   # CPU/Memory metrics
│   │   ├── TaskList.tsx        # Daemon task list
│   │   ├── TaskForm.tsx        # Create new tasks ✨ NEW
│   │   ├── AgentStatus.tsx     # Agent monitoring ✨ NEW
│   │   └── Login.tsx           # Authentication
│   ├── store/              # Zustand stores
│   │   ├── authStore.ts        # Authentication state
│   │   └── daemonStore.ts      # Daemon/Agent/Task state
│   ├── services/           # API clients
│   │   └── api.ts              # REST API service
│   ├── types/              # TypeScript types
│   │   └── daemon.ts           # API type definitions
│   ├── App.tsx             # Root component
│   ├── main.tsx            # Application entry
│   └── index.css           # Global styles
├── package.json            # Dependencies
├── tsconfig.json           # TypeScript config
├── tailwind.config.js      # TailwindCSS config
├── vite.config.ts          # Vite config
└── README.md               # This file

## Getting Started

### Prerequisites

- Node.js 18+ (recommended: 20.x)
- npm 10+

### Installation

```bash
cd web/frontend
npm install
```

### Development

```bash
# Start dev server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Features

### ✅ Implemented Components

#### 1. Dashboard
Main layout orchestrating all components with auto-refresh every 5 seconds.

#### 2. DaemonStatus
Displays daemon running state, uptime, task counts (total, completed, failed).

#### 3. SystemMetrics
Real-time system resource monitoring:
- CPU usage (%)
- Memory usage (%)
- Disk usage (%)
- User activity status
- Idle time tracking
- Sleep hours indicator

#### 4. TaskList
Lists all registered daemon tasks with:
- Task name and description
- Priority badge (CRITICAL/HIGH/MEDIUM/LOW)
- Execution statistics
- Success rate calculation
- Last run timestamp
- Failure indicators

#### 5. DaemonControls
Start/Stop daemon controls with systemd service hint.

#### 6. TaskForm ✨ NEW
Create custom daemon tasks with:
- Task ID validation (lowercase, numbers, underscores)
- Name and description fields
- Priority selection
- Python code editor with syntax highlighting
- Advanced options (collapsible):
  - Repeat interval (seconds)
  - Timeout configuration
- Built-in code examples:
  - Simple task
  - File system task
  - Async task
- Real-time validation
- Success/error feedback

#### 7. AgentStatus ✨ NEW
Monitor OmniMind agents in real-time:
- Agent type indicators:
  - 🪃 Orchestrator (coordination)
  - 💻 Code (development)
  - 🏗️ Architect (documentation)
  - 🪲 Debug (diagnostics)
  - ⭐ Reviewer (code review)
  - 🧠 Psychoanalyst (analysis)
- Status badges (idle/working/error/offline)
- Current task display (when working)
- Task completion statistics
- Uptime tracking
- Performance metrics:
  - Average response time
  - Success rate
  - Memory usage
- Last active timestamp
- Agent type legend

#### 8. Login
HTTP Basic Authentication with credential storage.

## State Management (Zustand)

### DaemonStore

```typescript
interface DaemonState {
  // Core daemon data
  status: DaemonStatus | null;
  tasks: DaemonTask[];
  agents: Agent[];
  activeTasks: Task[];
  
  // UI state
  loading: boolean;
  error: string | null;
  isConnected: boolean;
  
  // Actions
  setStatus(status: DaemonStatus): void;
  setTasks(tasks: DaemonTask[]): void;
  setAgents(agents: Agent[]): void;
  setActiveTasks(tasks: Task[]): void;
  addTask(task: Task): void;
  updateTask(id: string, updates: Partial<Task>): void;
  setLoading(loading: boolean): void;
  setError(error: string | null): void;
  setConnected(connected: boolean): void;
}
```

### AuthStore

```typescript
interface AuthState {
  isAuthenticated: boolean;
  username: string;
  login(username: string, password: string): void;
  logout(): void;
}
```

## API Integration

### REST Endpoints

```typescript
// Daemon status
GET /daemon/status -> DaemonStatus

// Daemon tasks
GET /daemon/tasks -> DaemonTask[]

// Add custom task
POST /daemon/tasks/add -> { message: string, task_id: string }

// Daemon controls
POST /daemon/start -> { message: string }
POST /daemon/stop -> { message: string }
```

### Authentication

All API requests use HTTP Basic Authentication:
- Username/password set via environment or auto-generated
- Credentials stored in `authStore`
- Authorization header: `Basic base64(username:password)`

## Type Definitions

### Agent

```typescript
interface Agent {
  agent_id: string;
  name: string;
  type: 'orchestrator' | 'code' | 'architect' | 'debug' | 'reviewer' | 'psychoanalyst';
  status: 'idle' | 'working' | 'error' | 'offline';
  current_task?: string;
  tasks_completed: number;
  tasks_failed: number;
  last_active?: string;
  uptime_seconds: number;
  metrics?: {
    avg_response_time_ms: number;
    success_rate: number;
    memory_usage_mb: number;
  };
}
```

### Task

```typescript
interface Task {
  task_id: string;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  created_at: string;
  started_at?: string;
  completed_at?: string;
  assigned_agent?: string;
  progress?: number;
  error_message?: string;
}
```

### DaemonStatus

```typescript
interface DaemonStatus {
  running: boolean;
  uptime_seconds: number;
  system_metrics: SystemMetrics;
  task_count: number;
  completed_tasks: number;
  failed_tasks: number;
  cloud_connected: boolean;
}
```

## Environment Variables

```env
# API Base URL (default: http://localhost:8000)
VITE_API_URL=http://localhost:8000
```

## Development Guidelines

### Code Style

- **TypeScript strict mode** - All code must compile with strict checks
- **ESLint** - Zero violations required
- **Functional components** - Use React hooks, no class components
- **Named exports** - No default exports (except App.tsx)
- **Responsive design** - Mobile-first with TailwindCSS

### Component Structure

```typescript
// 1. Imports
import { useState } from 'react';
import { useStore } from '../store';

// 2. Type definitions (if needed)
interface Props {
  // ...
}

// 3. Component
export function ComponentName({ prop }: Props) {
  // 4. Hooks
  const state = useStore();
  const [local, setLocal] = useState();
  
  // 5. Handlers
  const handleClick = () => {
    // ...
  };
  
  // 6. Effects
  useEffect(() => {
    // ...
  }, []);
  
  // 7. Render
  return (
    <div className="...">
      {/* ... */}
    </div>
  );
}
```

### Styling Conventions

- Use TailwindCSS utility classes
- Color scheme:
  - Background: `bg-gray-900` (dark)
  - Cards: `bg-gray-800`
  - Borders: `border-gray-700`
  - Text: `text-white`, `text-gray-400`
  - Accents: `text-blue-400`, `text-green-400`, etc.
- Responsive breakpoints:
  - `sm:` - 640px
  - `md:` - 768px
  - `lg:` - 1024px

## Testing

Currently no tests implemented. Future additions:
- Component unit tests (Vitest + React Testing Library)
- Integration tests for API calls
- E2E tests with Playwright

## Build Output

Production build generates:
- `dist/index.html` - Entry point
- `dist/assets/index-[hash].css` - Minified styles (~15KB)
- `dist/assets/index-[hash].js` - Minified bundle (~178KB)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Troubleshooting

### Build Errors

```bash
# Clear cache and rebuild
rm -rf node_modules dist .vite
npm install
npm run build
```

### Type Errors

```bash
# Check TypeScript compilation
npx tsc --noEmit
```

### Port Already in Use

```bash
# Kill process on port 5173
npx kill-port 5173
npm run dev
```

## Future Enhancements

- [ ] WebSocket integration for real-time updates
- [ ] Workflow visualization component
- [ ] Security event monitoring panel
- [ ] Task progress tracking with progress bars
- [ ] Agent performance charts
- [ ] Dark/light theme toggle
- [ ] Export task execution logs
- [ ] Advanced filtering and search
- [ ] Keyboard shortcuts
- [ ] Accessibility improvements (ARIA labels)

## License

Part of the OmniMind Autonomous Agent System.

## Contributors

- GitHub Copilot Agent (Implementation)
- fabs-devbrain (Architecture & Design)
