import { useDaemonStore } from '../store/daemonStore';

export function SystemMetrics() {
  const status = useDaemonStore((state) => state.status);
  const lastKnownMetrics = useDaemonStore((state) => state.lastKnownMetrics);

  // Use current status if available, otherwise fall back to cached metrics
  const currentMetrics = status?.system_metrics;
  const metrics = (currentMetrics && Object.keys(currentMetrics).length > 0) ? currentMetrics : lastKnownMetrics?.system_metrics;

  if (!metrics) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-6">System Metrics</h2>
        <div className="text-gray-400 text-center py-8">
          <span className="animate-pulse">Loading metrics...</span>
        </div>
      </div>
    );
  }

  const getUsageColor = (percent: number) => {
    if (percent > 80) return 'bg-red-500';
    if (percent > 60) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 shadow-xl border border-gray-700">
      <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
        <span className="text-blue-500">📊</span> System Metrics
      </h2>

      <div className="space-y-6">
        {/* CPU Usage */}
        <div>
          <div className="flex justify-between mb-2">
            <span className="text-gray-300">CPU Usage</span>
            <span className="text-white font-semibold">
              {(metrics.cpu_percent ?? 0).toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${getUsageColor(metrics.cpu_percent ?? 0)}`}
              style={{ width: `${metrics.cpu_percent ?? 0}%` }}
            ></div>
          </div>
        </div>

        {/* Memory Usage */}
        <div>
          <div className="flex justify-between mb-2">
            <span className="text-gray-300">Memory Usage</span>
            <span className="text-white font-semibold">
              {(metrics.memory_percent ?? 0).toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${getUsageColor(metrics.memory_percent ?? 0)}`}
              style={{ width: `${metrics.memory_percent ?? 0}%` }}
            ></div>
          </div>
        </div>

        {/* Disk Usage */}
        <div>
          <div className="flex justify-between mb-2">
            <span className="text-gray-300">Disk Usage</span>
            <span className="text-white font-semibold">
              {(metrics.disk_percent ?? 0).toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${getUsageColor(metrics.disk_percent ?? 0)}`}
              style={{ width: `${metrics.disk_percent ?? 0}%` }}
            ></div>
          </div>
        </div>

        {/* GPU Usage */}
        {metrics.gpu?.available && (
          <div className="pt-2">
            <div className="flex justify-between mb-2">
              <span className="text-gray-300 flex items-center gap-1">
                <span className="text-green-500">⚡</span> GPU ({metrics.gpu.name})
              </span>
              <span className="text-white font-semibold">
                {metrics.gpu.utilization?.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
              <div
                className={`h-full transition-all duration-300 ${getUsageColor(metrics.gpu.utilization ?? 0)}`}
                style={{ width: `${metrics.gpu.utilization ?? 0}%` }}
              ></div>
            </div>
            <div className="text-xs text-gray-400 mt-2 flex justify-between">
              <span>VRAM: {metrics.gpu.memory_allocated_mb?.toFixed(0)}MB / {metrics.gpu.memory_total_mb?.toFixed(0)}MB</span>
              <span>{((metrics.gpu.memory_allocated_mb || 0) / (metrics.gpu.memory_total_mb || 1) * 100).toFixed(0)}%</span>
            </div>
          </div>
        )}

        {/* User Activity */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-700">
          <div className="bg-gray-700/50 rounded-lg p-3">
            <div className="text-gray-400 text-sm mb-1">User Status</div>
            <div className={`font-semibold ${metrics.is_user_active ? 'text-green-400' : 'text-gray-400'}`}>
              {metrics.is_user_active ? '🟢 Active' : '⚪ Idle'}
            </div>
          </div>

          <div className="bg-gray-700/50 rounded-lg p-3">
            <div className="text-gray-400 text-sm mb-1">Idle Time</div>
            <div className="text-white font-semibold">
              {Math.floor((metrics.idle_seconds ?? 0) / 60)}m
            </div>
          </div>
        </div>

        {/* Sentinel & Uptime */}
        <div className="pt-4 border-t border-gray-700 space-y-3">
          <div className="flex justify-between items-center bg-gray-900/40 border border-gray-700 rounded-lg p-3">
            <span className="text-gray-300 text-sm font-medium">Sentinel Watchdog</span>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${status?.sentinel_status?.status === 'active' ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.8)]' : 'bg-red-500 animate-pulse'}`}></div>
              <span className={`text-xs font-bold tracking-wider ${status?.sentinel_status?.status === 'active' ? 'text-green-400' : 'text-red-400'}`}>
                {status?.sentinel_status?.status === 'active' ? 'PROTECTED' : 'UNPROTECTED'}
              </span>
            </div>
          </div>

          <div className="flex justify-between text-[10px] px-1 text-gray-500 uppercase tracking-widest">
            <span>Uptime: {Math.floor((status?.uptime_seconds ?? 0) / 3600)}h {Math.floor(((status?.uptime_seconds ?? 0) % 3600) / 60)}m</span>
            <span>Kernel V3.0-Consolidated</span>
          </div>
        </div>

        {/* Sleep Hours Indicator */}
        {metrics.is_sleep_hours && (
          <div className="bg-blue-900/30 border border-blue-500/50 rounded-lg p-3 text-center">
            <span className="text-blue-400">🌙 Sleep Hours (00:00-06:00)</span>
          </div>
        )}
      </div>
    </div>
  );
}
