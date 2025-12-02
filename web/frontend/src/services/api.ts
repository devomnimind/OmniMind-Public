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
    const defaultUser = import.meta.env.VITE_DASHBOARD_USER;
    const defaultPass = import.meta.env.VITE_DASHBOARD_PASS;

    if (
      typeof defaultUser === 'string' &&
      defaultUser &&
      typeof defaultPass === 'string' &&
      defaultPass
    ) {
      this.setCredentials(defaultUser, defaultPass);
    }
  }

  private getAuthHeader(): string {
    const credentials = btoa(`${this.username}:${this.password}`);
    return `Basic ${credentials}`;
  }

  getHeaders(): HeadersInit {
    return {
      'Authorization': this.getAuthHeader(),
      'Content-Type': 'application/json',
    };
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers = {
      'Authorization': this.getAuthHeader(),
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
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

  async resetMetrics(): Promise<{ message: string }> {
    return this.request('/daemon/reset-metrics', { method: 'POST' });
  }

  // ============================================================================
  // NEW ENDPOINTS (Phase 8.2 Dashboard Integration)
  // ============================================================================

  async getHealthStatus(): Promise<any> {
    return this.get('/health/');
  }

  async getSecurityOverview(): Promise<any> {
    return this.get('/api/security/');
  }

  async getSecurityStatus(): Promise<any> {
    return this.get('/api/security/status');
  }

  async getSecurityEvents(
    eventType?: string,
    severity?: string,
    limit?: number
  ): Promise<any> {
    const params = new URLSearchParams();
    if (eventType) params.append('event_type', eventType);
    if (severity) params.append('severity', severity);
    if (limit) params.append('limit', limit.toString());

    const query = params.toString();
    return this.get(`/api/security/events${query ? '?' + query : ''}`);
  }

  async getMetacognitionOverview(): Promise<any> {
    return this.get('/api/metacognition/');
  }

  async getMetacognitionInsights(): Promise<any> {
    return this.get('/api/metacognition/insights');
  }

  async getMetricsData(): Promise<any> {
    return this.get('/api/metrics');
  }

  async getAgents(): Promise<any> {
    return this.get('/api/agents/');
  }

  async getTasks(): Promise<any> {
    return this.get('/api/tasks/');
  }

  async getWebSocketInfo(): Promise<any> {
    return this.get('/ws');
  }

  async getTribunalActivity(): Promise<any> {
    return this.get('/api/tribunal/activity');
  }
}

export const apiService = new ApiService();
apiService.setDefaultCredentials();
