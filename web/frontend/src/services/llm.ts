/**
 * LLM Service - Frontend integration with backend LLM router
 * Handles all LLM API calls with error handling and fallback
 */

export interface LLMInvokeRequest {
  prompt: string;
  tier?: 'fast' | 'balanced' | 'high_quality';
  provider?: string;
}

export interface LLMInvokeResponse {
  success: boolean;
  text: string;
  provider: string;
  model: string;
  latency_ms: number;
  tokens_used?: number;
  error?: string;
}

export interface LLMStatus {
  providers: Record<string, boolean>;
  metrics: Record<string, any>;
}

export interface LLMModels {
  tiers: string[];
  providers: string[];
  default_tier: string;
}

class LLMService {
  private baseUrl = '/api/v1';
  private auth: { username: string; password: string } | null = null;

  constructor() {
    // Get auth from store
    const stored = localStorage.getItem('auth');
    if (stored) {
      try {
        this.auth = JSON.parse(stored);
      } catch {
        this.auth = null;
      }
    }
  }

  /**
   * Get Basic auth header
   */
  private getAuthHeader(): string {
    if (!this.auth) {
      const username = localStorage.getItem('omnimind_user') || '';
      const password = localStorage.getItem('omnimind_pass') || '';
      return 'Basic ' + btoa(`${username}:${password}`);
    }
    const { username, password } = this.auth;
    return 'Basic ' + btoa(`${username}:${password}`);
  }

  /**
   * Invoke LLM with automatic fallback
   */
  async invoke(request: LLMInvokeRequest): Promise<LLMInvokeResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/llm/invoke`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': this.getAuthHeader(),
        },
        body: JSON.stringify({
          prompt: request.prompt,
          tier: request.tier || 'balanced',
          provider: request.provider || null,
        }),
      });

      if (!response.ok) {
        throw new Error(`LLM invoke failed: ${response.statusText}`);
      }

      const data = await response.json() as LLMInvokeResponse;
      return data;
    } catch (error) {
      console.error('LLM invoke error:', error);
      return {
        success: false,
        text: '',
        provider: 'error',
        model: '',
        latency_ms: 0,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * Get LLM router status
   */
  async getStatus(): Promise<LLMStatus> {
    try {
      const response = await fetch(`${this.baseUrl}/llm/status`, {
        method: 'GET',
        headers: {
          'Authorization': this.getAuthHeader(),
        },
      });

      if (!response.ok) {
        throw new Error(`LLM status failed: ${response.statusText}`);
      }

      return await response.json() as LLMStatus;
    } catch (error) {
      console.error('LLM status error:', error);
      return {
        providers: {},
        metrics: {},
      };
    }
  }

  /**
   * Get available LLM models and tiers
   */
  async getModels(): Promise<LLMModels> {
    try {
      const response = await fetch(`${this.baseUrl}/llm/models`, {
        method: 'GET',
        headers: {
          'Authorization': this.getAuthHeader(),
        },
      });

      if (!response.ok) {
        throw new Error(`LLM models failed: ${response.statusText}`);
      }

      return await response.json() as LLMModels;
    } catch (error) {
      console.error('LLM models error:', error);
      return {
        tiers: ['fast', 'balanced', 'high_quality'],
        providers: ['ollama', 'huggingface', 'openrouter'],
        default_tier: 'balanced',
      };
    }
  }

  /**
   * Analyze consciousness metrics using LLM
   */
  async analyzeMetrics(metrics: Record<string, any>): Promise<string> {
    const prompt = `
Analyze the following consciousness metrics and provide insights:

Metrics:
- Phi (Integrated Information): ${metrics.phi || 0}
- ICI (Integrated Coherence Index): ${metrics.ici || 0}
- PRS (Panarchic Resonance Score): ${metrics.prs || 0}
- Anxiety: ${metrics.anxiety || 0}
- Flow: ${metrics.flow || 0}
- Entropy: ${metrics.entropy || 0}

Please provide a brief interpretation of what these metrics indicate about the system's consciousness state.
    `.trim();

    const response = await this.invoke({
      prompt,
      tier: 'balanced',
    });

    return response.success ? response.text : 'Analysis unavailable';
  }

  /**
   * Analyze module activity using LLM
   */
  async analyzeModuleActivity(activity: Record<string, number>): Promise<string> {
    const prompt = `
Analyze the following module activity levels and provide insights:

Module Activity:
${Object.entries(activity)
  .map(([module, level]) => `- ${module}: ${(level * 100).toFixed(1)}%`)
  .join('\n')}

Please identify which modules are most active and provide brief analysis of the system's operational state.
    `.trim();

    const response = await this.invoke({
      prompt,
      tier: 'balanced',
    });

    return response.success ? response.text : 'Analysis unavailable';
  }

  /**
   * Generate system insights using LLM
   */
  async generateInsights(systemState: Record<string, any>): Promise<string> {
    const prompt = `
Generate insights about the current system state:

System State:
- Overall Status: ${systemState.overall_status || 'unknown'}
- CPU Usage: ${systemState.cpu_percent || 0}%
- Memory Usage: ${systemState.memory_percent || 0}%
- Uptime: ${systemState.uptime_seconds || 0} seconds
- Active Tasks: ${systemState.active_tasks || 0}

Please provide brief, actionable insights about the system's current state.
    `.trim();

    const response = await this.invoke({
      prompt,
      tier: 'balanced',
    });

    return response.success ? response.text : 'Insights unavailable';
  }
}

// Export singleton instance
export const llmService = new LLMService();
