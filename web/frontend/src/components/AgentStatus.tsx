import { useEffect } from 'react';
import { useDaemonStore } from '../store/daemonStore';

const AGENT_TYPE_ICONS = {
  orchestrator: '🪃',
  code: '💻',
  architect: '🏗️',
  debug: '🪲',
  reviewer: '⭐',
  psychoanalyst: '🧠',
} as const;

const AGENT_TYPE_COLORS = {
  orchestrator: 'border-purple-500 bg-purple-900/20',
  code: 'border-blue-500 bg-blue-900/20',
  architect: 'border-yellow-500 bg-yellow-900/20',
  debug: 'border-red-500 bg-red-900/20',
  reviewer: 'border-green-500 bg-green-900/20',
  psychoanalyst: 'border-indigo-500 bg-indigo-900/20',
} as const;

const STATUS_COLORS = {
  idle: 'bg-gray-500 text-gray-200',
  working: 'bg-green-500 text-green-200 animate-pulse',
  error: 'bg-red-500 text-red-200',
  offline: 'bg-gray-600 text-gray-400',
} as const;

export function AgentStatus() {
  const agents = useDaemonStore((state) => state.agents);
  const setAgents = useDaemonStore((state) => state.setAgents);

  useEffect(() => {
    // Initialize with mock agents for demonstration
    // In production, this would fetch from API
    if (agents.length === 0) {
      setAgents([
        {
          agent_id: 'orchestrator_1',
          name: 'Orchestrator Agent',
          type: 'orchestrator',
          status: 'idle',
          tasks_completed: 42,
          tasks_failed: 2,
          uptime_seconds: 86400,
          metrics: {
            avg_response_time_ms: 250,
            success_rate: 95.5,
            memory_usage_mb: 512,
          },
        },
        {
          agent_id: 'code_1',
          name: 'Code Agent',
          type: 'code',
          status: 'working',
          current_task: 'Implementing feature #123',
          tasks_completed: 28,
          tasks_failed: 1,
          uptime_seconds: 82800,
          last_active: new Date().toISOString(),
          metrics: {
            avg_response_time_ms: 1850,
            success_rate: 96.6,
            memory_usage_mb: 768,
          },
        },
        {
          agent_id: 'architect_1',
          name: 'Architect Agent',
          type: 'architect',
          status: 'idle',
          tasks_completed: 15,
          tasks_failed: 0,
          uptime_seconds: 79200,
          metrics: {
            avg_response_time_ms: 420,
            success_rate: 100,
            memory_usage_mb: 384,
          },
        },
        {
          agent_id: 'reviewer_1',
          name: 'Reviewer Agent',
          type: 'reviewer',
          status: 'idle',
          tasks_completed: 35,
          tasks_failed: 3,
          uptime_seconds: 86400,
          metrics: {
            avg_response_time_ms: 650,
            success_rate: 92.1,
            memory_usage_mb: 448,
          },
        },
      ]);
    }
  }, [agents.length, setAgents]);

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours >= 24) {
      const days = Math.floor(hours / 24);
      return `${days}d ${hours % 24}h`;
    }
    return `${hours}h ${minutes}m`;
  };

  const formatTimestamp = (timestamp?: string) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Agent Status</h2>
        <div className="text-sm text-gray-400">
          {agents.filter((a) => a.status === 'working').length} working / {agents.length} total
        </div>
      </div>

      {agents.length === 0 ? (
        <div className="text-center text-gray-400 py-8">
          <div className="text-4xl mb-2">🤖</div>
          <p>No agents active</p>
        </div>
      ) : (
        <div className="space-y-4">
          {agents.map((agent) => (
            <div
              key={agent.agent_id}
              className={`border-l-4 rounded-lg p-4 ${AGENT_TYPE_COLORS[agent.type]}`}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{AGENT_TYPE_ICONS[agent.type]}</span>
                  <div>
                    <h3 className="text-white font-semibold text-lg">{agent.name}</h3>
                    <p className="text-gray-400 text-xs">ID: {agent.agent_id}</p>
                  </div>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-semibold ${STATUS_COLORS[agent.status]}`}>
                  {agent.status.toUpperCase()}
                </div>
              </div>

              {/* Current Task */}
              {agent.current_task && (
                <div className="mb-3 bg-gray-900/50 rounded p-2 text-sm">
                  <span className="text-gray-400">Current Task: </span>
                  <span className="text-white">{agent.current_task}</span>
                </div>
              )}

              {/* Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                <div className="bg-gray-900/30 rounded p-2">
                  <div className="text-gray-400 text-xs mb-1">Completed</div>
                  <div className="text-green-400 font-semibold">{agent.tasks_completed}</div>
                </div>

                <div className="bg-gray-900/30 rounded p-2">
                  <div className="text-gray-400 text-xs mb-1">Failed</div>
                  <div className="text-red-400 font-semibold">{agent.tasks_failed}</div>
                </div>

                <div className="bg-gray-900/30 rounded p-2">
                  <div className="text-gray-400 text-xs mb-1">Uptime</div>
                  <div className="text-white font-semibold text-sm">{formatUptime(agent.uptime_seconds)}</div>
                </div>

                <div className="bg-gray-900/30 rounded p-2">
                  <div className="text-gray-400 text-xs mb-1">Last Active</div>
                  <div className="text-white font-semibold text-sm">{formatTimestamp(agent.last_active)}</div>
                </div>
              </div>

              {/* Metrics */}
              {agent.metrics && (
                <div className="grid grid-cols-3 gap-3 text-xs">
                  <div>
                    <div className="text-gray-400 mb-1">Avg Response</div>
                    <div className="text-blue-400 font-semibold">
                      {agent.metrics.avg_response_time_ms}ms
                    </div>
                  </div>

                  <div>
                    <div className="text-gray-400 mb-1">Success Rate</div>
                    <div className="text-green-400 font-semibold">
                      {agent.metrics.success_rate.toFixed(1)}%
                    </div>
                  </div>

                  <div>
                    <div className="text-gray-400 mb-1">Memory</div>
                    <div className="text-purple-400 font-semibold">
                      {agent.metrics.memory_usage_mb}MB
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Legend */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <h4 className="text-sm font-semibold text-gray-300 mb-3">Agent Types</h4>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs">
          <div className="flex items-center gap-2 text-gray-400">
            <span>{AGENT_TYPE_ICONS.orchestrator}</span>
            <span>Orchestrator - Task coordination</span>
          </div>
          <div className="flex items-center gap-2 text-gray-400">
            <span>{AGENT_TYPE_ICONS.code}</span>
            <span>Code - Development tasks</span>
          </div>
          <div className="flex items-center gap-2 text-gray-400">
            <span>{AGENT_TYPE_ICONS.architect}</span>
            <span>Architect - Documentation</span>
          </div>
          <div className="flex items-center gap-2 text-gray-400">
            <span>{AGENT_TYPE_ICONS.debug}</span>
            <span>Debug - Diagnostics</span>
          </div>
          <div className="flex items-center gap-2 text-gray-400">
            <span>{AGENT_TYPE_ICONS.reviewer}</span>
            <span>Reviewer - Code review</span>
          </div>
          <div className="flex items-center gap-2 text-gray-400">
            <span>{AGENT_TYPE_ICONS.psychoanalyst}</span>
            <span>Psychoanalyst - Analysis</span>
          </div>
        </div>
      </div>
    </div>
  );
}
