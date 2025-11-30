export interface SystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  is_user_active: boolean;
  idle_seconds: number;
  is_sleep_hours: boolean;
}

export interface TaskStats {
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  last_execution?: string;
  last_success?: string;
  last_failure?: string;
}

export interface DaemonTask {
  task_id: string;
  name: string;
  description: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  repeat_interval_seconds: number | null;
  timeout_seconds: number;
  last_run?: string;
  next_run?: string;
  stats: TaskStats;
}

export interface ConsciousnessMetrics {
  ICI: number;
  PRS: number;
  phi?: number;
  anxiety?: number;
  flow?: number;
  entropy?: number;
  details: {
    ici_components: {
      temporal_coherence: number;
      marker_integration: number;
      resonance: number;
    };
    prs_components: {
      avg_micro_entropy: number;
      macro_entropy: number;
    };
  };
  interpretation: {
    message: string;
    confidence: string;
    disclaimer: string;
  };
  history?: {
    phi: number[];
    anxiety: number[];
    flow: number[];
    entropy: number[];
    timestamps: string[];
  };
}

export interface ModuleActivity {
  orchestrator: number;
  consciousness: number;
  audit: number;
  autopoietic: number;
  ethics: number;
  attention: number;
}

export interface SystemHealth {
  overall: 'STABLE' | 'WARNING' | 'CRITICAL';
  integration: 'RISING' | 'STABLE' | 'FALLING';
  coherence: 'GOOD' | 'MODERATE' | 'POOR';
  anxiety: 'CALM' | 'MODERATE' | 'HIGH';
  flow: 'NORMAL' | 'BLOCKED' | 'FLUID';
  audit: 'CLEAN' | 'WARNINGS' | 'ISSUES';
}

export interface EventLogEntry {
  timestamp: string;
  type: 'INFO' | 'WARNING' | 'ERROR' | 'SUCCESS';
  message: string;
  metric?: string;
  old_value?: number;
  new_value?: number;
}

export interface DaemonStatus {
  running: boolean;
  uptime_seconds: number;
  system_metrics: SystemMetrics;
  task_count: number;
  completed_tasks: number;
  failed_tasks: number;
  cloud_connected: boolean;
  consciousness_metrics?: ConsciousnessMetrics;
  module_activity?: ModuleActivity;
  system_health?: SystemHealth;
  event_log?: EventLogEntry[];
  baseline_comparison?: {
    phi: { current: number; baseline: number; change: number };
    ici: { current: number; baseline: number; change: number };
    prs: { current: number; baseline: number; change: number };
    anxiety: { current: number; baseline: number; change: number };
    flow: { current: number; baseline: number; change: number };
    entropy: { current: number; baseline: number; change: number };
  };
}

export interface AddTaskRequest {
  task_id: string;
  name: string;
  description: string;
  code: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  repeat_interval_seconds?: number;
  timeout_seconds?: number;
}

export interface Agent {
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

export interface Task {
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
