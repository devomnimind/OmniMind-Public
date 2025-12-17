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
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-2xl font-bold text-white mb-6">System Metrics</h2>

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
