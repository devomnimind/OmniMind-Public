# API Endpoints Integration Status

## Backend Endpoints (Port 8000)

### ✅ Core Endpoints (Implemented & Working)
- `GET /health/` - System health check (all components)
- `GET /api/agents/` - List of agents
- `GET /api/tasks/` - List of tasks

### ✅ Security Endpoints (NEW - Phase 8.2)
- `GET /api/security/` - Security overview with status
- `GET /api/security/status` - Current security status (CRITICAL/HIGH/MEDIUM/NORMAL)
- `GET /api/security/events` - List security events with filters
- `GET /api/security/events/stats` - Security statistics
- `GET /api/security/analytics` - Comprehensive security analytics
- `GET /api/security/monitoring/dashboard` - Real-time security dashboard

### ✅ Metacognition Endpoints (NEW - Phase 8.2)
- `GET /api/metacognition/` - Metacognition system overview
- `GET /api/metacognition/insights` - Key insights from analysis
- `GET /api/metacognition/health` - Quick health check
- `GET /api/metacognition/suggestions` - Top optimization suggestions
- `GET /api/metacognition/stats` - Analysis statistics
- `GET /api/metacognition/goals/generate` - Generate improvement goals
- `GET /api/metacognition/homeostasis/status` - Homeostatic metrics

### ✅ Metrics Endpoints (NEW - Phase 8.2)
- `GET /api/metrics` - Public metrics (no auth required)
- `GET /metrics` - Full metrics (auth required)

### ✅ WebSocket Endpoints (NEW - Phase 8.2)
- `GET /ws` - WebSocket info and available channels
- `WS /ws` - Real-time updates via WebSocket (auth required)
- `GET /ws/stats` - WebSocket connection statistics (auth required)

## Frontend Integration (Port 3000)

### API Service Methods (src/services/api.ts)
```typescript
// New methods added for Phase 8.2:
apiService.getHealthStatus()           // GET /health/
apiService.getSecurityOverview()       // GET /api/security/
apiService.getSecurityStatus()         // GET /api/security/status
apiService.getSecurityEvents()         // GET /api/security/events
apiService.getMetacognitionOverview()  // GET /api/metacognition/
apiService.getMetacognitionInsights()  // GET /api/metacognition/insights
apiService.getMetricsData()            // GET /api/metrics
apiService.getAgents()                 // GET /api/agents/
apiService.getTasks()                  // GET /api/tasks/
apiService.getWebSocketInfo()          // GET /ws
```

## Dashboard Components Using Endpoints

### Currently Integrated
- `DaemonStatus` - Uses `/daemon/status`
- `SystemMetrics` - Uses system metrics endpoint
- `TaskList` - Uses `/daemon/tasks`
- `AgentStatus` - Uses agent endpoints
- `ConsciousnessMetrics` - Uses consciousness metrics
- `RealtimeAnalytics` - Uses WebSocket for real-time data

### Ready for Integration (Phase 8.2)
- `SecurityDashboard` - Should use `/api/security/` endpoints
- `MetacognitionPanel` - Should use `/api/metacognition/` endpoints
- `HealthMonitor` - Should use `/health/` endpoint
- `MetricsView` - Should use `/api/metrics` endpoint

## Environment Configuration

### Frontend (.env or .env.local)
```
VITE_API_URL=http://localhost:8000
VITE_DASHBOARD_USER=admin
VITE_DASHBOARD_PASS=admin
```

### Backend (config/omnimind.yaml or env vars)
```
OMNIMIND_API_HOST=0.0.0.0
OMNIMIND_API_PORT=8000
OMNIMIND_DASHBOARD_AUTH_FILE=config/dashboard_auth.json
```

## Testing Endpoints

### Quick Verification Script
```bash
# Backend health
curl -s http://localhost:8000/health/ | python -m json.tool

# Security overview
curl -s http://localhost:8000/api/security/ | python -m json.tool

# Metacognition insights
curl -s http://localhost:8000/api/metacognition/insights | python -m json.tool

# Public metrics
curl -s http://localhost:8000/api/metrics | python -m json.tool

# Frontend dashboard
open http://localhost:3000
```

## Known Issues & Workarounds

### 503 Metacognition Response
- Means orchestrator is initializing
- Retry after 5-10 seconds
- Normal behavior on startup

### 404 on New Endpoints After Deploy
- Server needs restart to load new routes
- Kill and restart uvicorn process

### CORS Issues
- Frontend CORS middleware configured in backend
- Check `fastapi.middleware.cors.CORSMiddleware` in main.py

## Next Steps for Phase 8.2+

1. Create `SecurityDashboardPanel` component
   - Fetch `/api/security/` and `/api/security/status`
   - Display threat level with color-coded status
   - Show recent events list

2. Create `MetacognitionPanel` component
   - Fetch `/api/metacognition/insights`
   - Display key suggestions and insights
   - Show system health indicators

3. Enhance existing components
   - Add health endpoint to connection status
   - Use real metrics in ConsciousnessMetrics
   - Subscribe to WebSocket channels for updates

4. Add error handling
   - Graceful degradation when endpoints unavailable
   - Retry logic with exponential backoff
   - User-friendly error messages
