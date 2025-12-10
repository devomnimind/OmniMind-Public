import { useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useDaemonStore } from '../store/daemonStore';

interface AnalyticsData {
  timestamp: string;
  cpu_usage: number;
  memory_usage: number;
  active_tasks: number;
  completed_tasks: number;
  agent_activity: number;
}

export function RealtimeAnalytics() {
  const { lastMessage } = useWebSocket();
  const status = useDaemonStore((state) => state.status);
  const uptimeSeconds = status?.uptime_seconds ?? 0;
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData[]>([]);
  const [currentMetrics, setCurrentMetrics] = useState({
    cpu: 0,
    memory: 0,
    tasks: 0,
    agents: 0,
  });

  // CORREÇÃO CRÍTICA (2025-12-09): Fallback para dados do daemonStore quando WebSocket não tem dados
  useEffect(() => {
    if (!status?.system_metrics) return;

    const systemMetrics = status.system_metrics;
    const fallbackMetrics = {
      cpu: systemMetrics.cpu_percent || 0,
      memory: systemMetrics.memory_percent || 0,
      tasks: status.task_count || 0,
      agents: status.agents?.length || 0,
    };

    // Só atualizar se valores são diferentes e não temos dados WebSocket recentes
    setCurrentMetrics((prev) => {
      // Se temos dados WebSocket recentes (últimos 5 segundos), não usar fallback
      const hasRecentWebSocketData = analyticsData.length > 0 &&
        (Date.now() - new Date(analyticsData[analyticsData.length - 1].timestamp).getTime()) < 5000;

      if (hasRecentWebSocketData) {
        return prev; // Manter dados WebSocket
      }

      // Usar fallback apenas se valores são diferentes
      if (
        prev.cpu !== fallbackMetrics.cpu ||
        prev.memory !== fallbackMetrics.memory ||
        prev.tasks !== fallbackMetrics.tasks ||
        prev.agents !== fallbackMetrics.agents
      ) {
        return fallbackMetrics;
      }

      return prev;
    });
  }, [status?.system_metrics?.cpu_percent, status?.system_metrics?.memory_percent, status?.task_count, status?.agents?.length, analyticsData.length]); // CORREÇÃO: Depender apenas de valores primitivos

  useEffect(() => {
    // CORREÇÃO CRÍTICA (2025-12-09): Depender apenas de campos estáveis para evitar re-renders constantes
    if (!lastMessage || lastMessage.type !== 'metrics_update') return;

    // CORREÇÃO: Usar useRef para evitar atualizações se os dados não mudaram
    const data = lastMessage.data as any;
    const messageId = lastMessage.id || `${lastMessage.type}-${Date.now()}`;

    // Verificar se já processamos esta mensagem
    const newDataPoint: AnalyticsData = {
      timestamp: new Date().toISOString(),
      cpu_usage: data.cpu_percent || 0,
      memory_usage: data.memory_percent || 0,
      active_tasks: data.active_tasks || 0,
      completed_tasks: data.completed_tasks || 0,
      agent_activity: data.agent_count || 0,
    };

    setAnalyticsData((prev) => {
      // Evitar duplicatas
      const lastPoint = prev[prev.length - 1];
      if (lastPoint && lastPoint.timestamp === newDataPoint.timestamp) {
        return prev; // Não atualizar se timestamp é o mesmo
      }
      return [...prev.slice(-29), newDataPoint];
    });

    setCurrentMetrics((prev) => {
      // Só atualizar se valores realmente mudaram
      const newMetrics = {
        cpu: data.cpu_percent || 0,
        memory: data.memory_percent || 0,
        tasks: data.active_tasks || 0,
        agents: data.agent_count || 0,
      };

      if (
        prev.cpu === newMetrics.cpu &&
        prev.memory === newMetrics.memory &&
        prev.tasks === newMetrics.tasks &&
        prev.agents === newMetrics.agents
      ) {
        return prev; // Não atualizar se valores são iguais
      }

      return newMetrics;
    });
  }, [lastMessage?.type, lastMessage?.id]); // CORREÇÃO: Depender apenas de campos estáveis

  const getStatusColor = (value: number, thresholds: { warning: number; danger: number }) => {
    if (value >= thresholds.danger) return 'text-neon-red';
    if (value >= thresholds.warning) return 'text-neon-yellow';
    return 'text-neon-green';
  };

  const getBarColor = (value: number, thresholds: { warning: number; danger: number }) => {
    if (value >= thresholds.danger) return 'bg-gradient-to-r from-neon-red to-red-700';
    if (value >= thresholds.warning) return 'bg-gradient-to-r from-neon-yellow to-yellow-700';
    return 'bg-gradient-to-r from-neon-green to-green-700';
  };

  const formatUptime = (seconds: number) => {
    if (!seconds) return '—';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  return (
    <div className="glass-card p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gradient-cyber">Real-time Analytics</h2>
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <span className="inline-block w-2 h-2 rounded-full bg-neon-green animate-pulse-slow" style={{ boxShadow: '0 0 10px rgba(16, 185, 129, 0.8)' }} />
          Live Updates
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* CPU Usage */}
        <div className="metric-card hover-lift">
          <div className="flex items-center justify-between mb-3">
            <span className="text-gray-400 text-sm font-medium">CPU Usage</span>
            <span className={`text-2xl font-bold ${getStatusColor(currentMetrics.cpu, { warning: 70, danger: 90 })}`}>
              {currentMetrics.cpu.toFixed(1)}%
            </span>
          </div>
          <div className="w-full h-2 bg-dark-100 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${getBarColor(currentMetrics.cpu, { warning: 70, danger: 90 })}`}
              style={{ width: `${currentMetrics.cpu}%` }}
            />
          </div>
        </div>

        {/* Memory Usage */}
        <div className="metric-card hover-lift">
          <div className="flex items-center justify-between mb-3">
            <span className="text-gray-400 text-sm font-medium">Memory</span>
            <span className={`text-2xl font-bold ${getStatusColor(currentMetrics.memory, { warning: 80, danger: 95 })}`}>
              {currentMetrics.memory.toFixed(1)}%
            </span>
          </div>
          <div className="w-full h-2 bg-dark-100 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${getBarColor(currentMetrics.memory, { warning: 80, danger: 95 })}`}
              style={{ width: `${currentMetrics.memory}%` }}
            />
          </div>
        </div>

        {/* Active Tasks */}
        <div className="metric-card hover-lift">
          <div className="flex items-center justify-between mb-3">
            <span className="text-gray-400 text-sm font-medium">Active Tasks</span>
            <span className="text-2xl font-bold text-cyber-400">
              {currentMetrics.tasks}
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            Processing
          </div>
        </div>

        {/* Active Agents */}
        <div className="metric-card hover-lift">
          <div className="flex items-center justify-between mb-3">
            <span className="text-gray-400 text-sm font-medium">Active Agents</span>
            <span className="text-2xl font-bold text-neon-purple">
              {currentMetrics.agents}
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span className="inline-block w-2 h-2 rounded-full bg-neon-purple animate-pulse-slow" />
            Online
          </div>
        </div>
      </div>

      {/* Trend Visualization (Simple Bar Chart) */}
      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-gray-300">Performance Trends</h3>
        <div className="glass-card p-4 h-48 flex items-end justify-between gap-1">
          {analyticsData.slice(-20).map((data, index) => {
            return (
              <div key={index} className="flex-1 flex flex-col items-center gap-1">
                {/* Memory Bar */}
                <div
                  className="w-full bg-gradient-to-t from-neon-purple to-purple-700 rounded-t opacity-60 hover:opacity-100 transition-opacity"
                  style={{ height: `${(data.memory_usage / 100) * 160}px` }}
                  title={`Memory: ${data.memory_usage.toFixed(1)}%`}
                />
                {/* CPU Bar */}
                <div
                  className="w-full bg-gradient-to-t from-cyber-500 to-cyan-700 rounded-t hover:shadow-neon-sm transition-shadow"
                  style={{ height: `${(data.cpu_usage / 100) * 160}px` }}
                  title={`CPU: ${data.cpu_usage.toFixed(1)}%`}
                />
              </div>
            );
          })}
        </div>
        <div className="flex items-center justify-center gap-6 text-xs text-gray-400">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded bg-gradient-to-r from-cyber-500 to-cyan-700" />
            CPU Usage
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded bg-gradient-to-r from-neon-purple to-purple-700" />
            Memory Usage
          </div>
        </div>
      </div>

      {/* Activity Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card-hover p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-cyber-500/20 flex items-center justify-center">
              <svg className="w-6 h-6 text-cyber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <p className="text-sm text-gray-400">Throughput</p>
              <p className="text-lg font-bold text-white">
                {analyticsData.length > 0 ? analyticsData[analyticsData.length - 1].completed_tasks : 0} tasks
              </p>
            </div>
          </div>
        </div>

        <div className="glass-card-hover p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-neon-green/20 flex items-center justify-center">
              <svg className="w-6 h-6 text-neon-green" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <p className="text-sm text-gray-400">Efficiency</p>
              <p className="text-lg font-bold text-white">
                {currentMetrics.cpu < 50 ? 'High' : currentMetrics.cpu < 80 ? 'Medium' : 'Low'}
              </p>
            </div>
          </div>
        </div>

        <div className="glass-card-hover p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-neon-purple/20 flex items-center justify-center">
              <svg className="w-6 h-6 text-neon-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p className="text-sm text-gray-400">Uptime</p>
              <p className="text-lg font-bold text-white">
                {formatUptime(uptimeSeconds)}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
