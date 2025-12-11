import type { DaemonStatus, DaemonTask, AddTaskRequest } from '../types/daemon';

interface ApiDaemonTask {
  task_id: string;
  name: string;
  description: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  repeat_interval?: string | null;
  execution_count: number;
  success_count: number;
  failure_count: number;
  last_execution?: string | null;
}

interface DaemonTasksResponse {
  tasks: ApiDaemonTask[];
  total_tasks: number;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  private username: string = '';
  private password: string = '';

  setCredentials(username: string, password: string) {
    this.username = username;
    this.password = password;
  }

  getAuthToken(): string | null {
    if (!this.username || !this.password) {
      return null;
    }
    return btoa(`${this.username}:${this.password}`);
  }

  setDefaultCredentials(): void {
    // Tentar recuperar da sessão anterior
    this.username = localStorage.getItem('omnimind_user') || '';
    this.password = localStorage.getItem('omnimind_pass') || '';
  }

  getAuthHeader(): string {
    if (!this.username || !this.password) {
      return '';
    }
    const credentials = btoa(`${this.username}:${this.password}`);
    return `Basic ${credentials}`;
  }

  getHeaders(): HeadersInit {
    const auth = this.getAuthHeader();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (auth) {
      headers['Authorization'] = auth;
    }
    return headers;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    // Garantir que credenciais estão configuradas
    // CORREÇÃO CRÍTICA (2025-12-10): Verificar autenticação antes de fazer request
    if (!this.getAuthToken()) {
      // Tentar usar credenciais padrão primeiro
      this.setDefaultCredentials();
      // Se ainda não tiver token após setDefaultCredentials, lançar erro
      if (!this.getAuthToken()) {
        throw new Error('Not authenticated');
      }
    }

    const headers = {
      'Authorization': this.getAuthHeader(),
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // CORREÇÃO CRÍTICA (2025-12-10): Timeout adaptativo aumentado
    // Backend pode estar sobrecarregado, aumentar timeouts significativamente
    const criticalEndpoints = ['/daemon/status', '/api/v1/autopoietic/consciousness/metrics'];
    const slowEndpoints = ['/api/v1/autopoietic/status', '/api/v1/autopoietic/cycles', '/api/tribunal', '/api/metacognition'];
    const isCritical = criticalEndpoints.some(ep => endpoint.includes(ep));
    const isSlow = slowEndpoints.some(ep => endpoint.includes(ep));

    // Timeouts aumentados: 30s críticos, 20s lentos, 15s normais
    const timeoutMs = isCritical ? 30000 : (isSlow ? 20000 : 15000);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
        signal: controller.signal,
        // credentials: 'include' removido para simplificar CORS com Basic Auth
        // Apenas necessário para cookies/sessions, não para Authorization header
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text().catch(() => response.statusText);
        console.error(`API Error ${response.status} para ${endpoint}: ${errorText}`);
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error(`Request timeout: ${endpoint}`);
      }
      throw error;
    }
  }

  async get<T = any>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T = any>(endpoint: string, body?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async getDaemonStatus(): Promise<DaemonStatus> {
    return this.request<DaemonStatus>('/daemon/status');
  }

  private parseRepeatInterval(interval?: string | null): number | null {
    if (!interval) return null;
    const normalized = interval.trim();
    if (!normalized || normalized.toLowerCase() === 'none') {
      return null;
    }

    const parts = normalized.split(':').map((part) => Number(part));
    if (parts.some((value) => Number.isNaN(value))) {
      return null;
    }

    let seconds = 0;
    if (parts.length === 3) {
      seconds = parts[0] * 3600 + parts[1] * 60 + parts[2];
    } else if (parts.length === 2) {
      seconds = parts[0] * 60 + parts[1];
    } else if (parts.length === 1) {
      seconds = parts[0];
    }

    return seconds;
  }

  async getDaemonTasks(): Promise<DaemonTask[]> {
    const response = await this.request<DaemonTasksResponse>('/daemon/tasks');
    return response.tasks.map((task) => ({
      task_id: task.task_id,
      name: task.name,
      description: task.description,
      priority: task.priority,
      repeat_interval_seconds: this.parseRepeatInterval(task.repeat_interval ?? null),
      timeout_seconds: 0,
      stats: {
        total_executions: task.execution_count,
        successful_executions: task.success_count,
        failed_executions: task.failure_count,
        last_execution: task.last_execution ?? undefined,
      },
    }));
  }

  async addTask(task: AddTaskRequest): Promise<{ message: string; task_id: string }> {
    return this.request('/daemon/tasks/add', {
      method: 'POST',
      body: JSON.stringify(task),
    });
  }

  async startDaemon(): Promise<{ message: string }> {
    return this.request('/daemon/start', { method: 'POST' });
  }

  async stopDaemon(): Promise<{ message: string }> {
    return this.request('/daemon/stop', { method: 'POST' });
  }

  // ============================================================================
  // CORRECTED ENDPOINTS - Mapped to actual backend routes (Backend has ALL these!)
  // ============================================================================

  async getHealthStatus(): Promise<any> {
    // Backend endpoint: GET /status (autopoietic status)
    return this.get('/api/v1/autopoietic/status');
  }

  async getSecurityOverview(): Promise<any> {
    // Backend endpoint: GET /api/security (security overview with events count)
    return this.get('/api/security');
  }

  async getSecurityStatus(): Promise<any> {
    // Backend endpoint: GET /api/security/status (detailed security status)
    return this.get('/api/security/status');
  }

  async getSecurityEvents(
    eventType?: string,
    severity?: string,
    limit?: number
  ): Promise<any> {
    // Backend endpoint: GET /api/security/events?event_type=...&severity=...&limit=...
    const params = new URLSearchParams();
    if (eventType) params.append('event_type', eventType);
    if (severity) params.append('severity', severity);
    if (limit) params.append('limit', limit.toString());

    const query = params.toString();
    return this.get(`/api/security/events${query ? '?' + query : ''}`);
  }

  async getMetacognitionOverview(): Promise<any> {
    // Backend endpoint: GET /api/metacognition (overview of metacognition system)
    return this.get('/api/metacognition');
  }

  async getMetacognitionInsights(): Promise<any> {
    // Backend endpoint: GET /api/metacognition/insights (detailed insights)
    return this.get('/api/metacognition/insights');
  }

  async getMetricsData(): Promise<any> {
    // Backend endpoint: GET /api/metrics (comprehensive system metrics - public)
    return this.get('/api/metrics');
  }

  async getRealMetrics(): Promise<any> {
    // Backend endpoint: GET /metrics (real-time consciousness metrics from Rhizome)
    return this.get('/metrics');
  }

  async getAgents(): Promise<any> {
    // Backend endpoint: GET /daemon/agents (list of active agents)
    return this.get('/daemon/agents');
  }

  async getTasks(): Promise<any> {
    // Backend endpoint: GET /daemon/tasks (list of daemon tasks)
    return this.get('/daemon/tasks');
  }

  async getWebSocketInfo(): Promise<any> {
    // Backend endpoint: GET /ws/stats (WebSocket connection stats)
    return this.get('/ws/stats');
  }

  async getTribunalActivity(): Promise<any> {
    // Backend endpoint: GET /api/tribunal/activity (tribunal activity with metrics and proposals)
    return this.get('/api/tribunal/activity');
  }

  async getTribunalMetrics(): Promise<any> {
    // Backend endpoint: GET /api/tribunal/metrics (detailed tribunal metrics and visual interpretation)
    return this.get('/api/tribunal/metrics');
  }

  // Autopoietic endpoints (Phase 22) - REAL backend routes!
  async getAutopoieticStatus(): Promise<any> {
    // Backend endpoint: GET /api/v1/autopoietic/status (autopoietic system status)
    return this.get('/api/v1/autopoietic/status');
  }

  async getAutopoieticCycles(limit: number = 50): Promise<any> {
    // Backend endpoint: GET /api/v1/autopoietic/cycles?limit=... (list of cycles)
    return this.get(`/api/v1/autopoietic/cycles?limit=${limit}`);
  }

  async getAutopoieticCycleStats(): Promise<any> {
    // Backend endpoint: GET /api/v1/autopoietic/cycles/stats (cycle statistics)
    return this.get('/api/v1/autopoietic/cycles/stats');
  }

  async getAutopoieticComponents(limit: number = 50): Promise<any> {
    // Backend endpoint: GET /api/v1/autopoietic/components?limit=... (synthesized components)
    return this.get(`/api/v1/autopoietic/components?limit=${limit}`);
  }

  async getAutopoieticHealth(): Promise<any> {
    // Backend endpoint: GET /api/v1/autopoietic/health (autopoietic health check)
    return this.get('/api/v1/autopoietic/health');
  }

  async getConsciousnessMetrics(includeRaw: boolean = false): Promise<any> {
    // Backend endpoint: GET /api/v1/autopoietic/consciousness/metrics?include_raw=...
    // Returns: φ (Phi), anxiety, flow, entropy, ICI, PRS + history + interpretations
    return this.get(`/api/v1/autopoietic/consciousness/metrics?include_raw=${includeRaw}`);
  }

  async getExtendedMetrics(): Promise<any> {
    // Backend endpoint: GET /api/v1/autopoietic/extended/metrics
    // Returns: Phi, Psi, Sigma, Gozo, Delta + history + triad
    return this.get('/api/v1/autopoietic/extended/metrics');
  }

  // Metacognition endpoints with full support
  async getMetacognitionSuggestions(): Promise<any> {
    // Backend endpoint: GET /api/metacognition/suggestions
    return this.get('/api/metacognition/suggestions');
  }

  async getMetacognitionStats(): Promise<any> {
    // Backend endpoint: GET /api/metacognition/stats
    return this.get('/api/metacognition/stats');
  }

  async getMetacognitionLastAnalysis(): Promise<any> {
    // Backend endpoint: GET /api/metacognition/last-analysis
    return this.get('/api/metacognition/last-analysis');
  }

  async getMetacognitionGoals(): Promise<any> {
    // Backend endpoint: GET /api/metacognition/goals/generate
    return this.get('/api/metacognition/goals/generate');
  }

  async getMetacognitionHomeostasis(): Promise<any> {
    // Backend endpoint: GET /api/metacognition/homeostasis/status
    return this.get('/api/metacognition/homeostasis/status');
  }

  // Security endpoints with full support
  async getSecurityAnalytics(): Promise<any> {
    // Backend endpoint: GET /api/security/analytics (security analytics dashboard)
    return this.get('/api/security/analytics');
  }

  async getSecurityMonitoringDashboard(): Promise<any> {
    // Backend endpoint: GET /api/security/monitoring/dashboard
    return this.get('/api/security/monitoring/dashboard');
  }

  async getSecurityCorrelatedEvents(): Promise<any> {
    // Backend endpoint: GET /api/security/events/correlated
    return this.get('/api/security/events/correlated');
  }

  async getSecurityAutomatedResponse(): Promise<any> {
    // Backend endpoint: GET /api/security/response/automated
    return this.get('/api/security/response/automated');
  }

  // API de Explicabilidade (Sessão 6 - Orchestrator) - for future use
  async getDecisions(): Promise<any[]> {
    // Placeholder: Future endpoint for decision logging
    // For now, use metacognition insights
    try {
      const data = await this.get('/api/metacognition/insights');
      // Ensure we always return an array
      if (Array.isArray(data)) {
        return data;
      }
      if (data && typeof data === 'object' && 'decisions' in data && Array.isArray(data.decisions)) {
        return data.decisions;
      }
      if (data && typeof data === 'object' && 'items' in data && Array.isArray(data.items)) {
        return data.items;
      }
      // If data is an object, wrap it in an array
      return data ? [data] : [];
    } catch (err) {
      console.error('Error in getDecisions:', err);
      return [];
    }
  }

  async getDecisionDetail(): Promise<any> {
    // Placeholder: Future endpoint for decision details
    try {
      const data = await this.get('/api/metacognition/last-analysis');
      return data || {};
    } catch (err) {
      console.error('Error in getDecisionDetail:', err);
      return {};
    }
  }

  async getDecisionStats(): Promise<any> {
    // Placeholder: Use metacognition stats as proxy
    try {
      const data = await this.get('/api/metacognition/stats');
      return data || {
        total_decisions: 0,
        successful_decisions: 0,
        failed_decisions: 0,
        success_rate: 0,
        average_trust_level: 0,
        decisions_by_action: {},
        decisions_by_reason: {}
      };
    } catch (err) {
      console.error('Error in getDecisionStats:', err);
      return {
        total_decisions: 0,
        successful_decisions: 0,
        failed_decisions: 0,
        success_rate: 0,
        average_trust_level: 0,
        decisions_by_action: {},
        decisions_by_reason: {}
      };
    }
  }

  async exportDecisions(): Promise<any> {
    // Placeholder: Use security events export
    try {
      const data = await this.get('/api/security/events?limit=1000');
      // Ensure it's an array
      if (Array.isArray(data)) {
        return data;
      }
      if (data && typeof data === 'object' && 'events' in data && Array.isArray(data.events)) {
        return data.events;
      }
      return [];
    } catch (err) {
      console.error('Error in exportDecisions:', err);
      return [];
    }
  }

  async resetMetrics(): Promise<void> {
    // Reset all metrics via API endpoint
    try {
      await this.post('/api/metrics/reset', {});
    } catch (err) {
      console.error('Error resetting metrics:', err);
      throw err;
    }
  }
}

export const apiService = new ApiService();
apiService.setDefaultCredentials();
