import { useDaemonStore } from '../store/daemonStore';

export function DaemonStatus() {
  const status = useDaemonStore((state) => state.status);

  if (!status) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-700 rounded w-3/4"></div>
          <div className="h-4 bg-gray-700 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  const uptimeHours = Math.floor(status.uptime_seconds / 3600);
  const uptimeMinutes = Math.floor((status.uptime_seconds % 3600) / 60);

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Daemon Status</h2>
        <div className={`px-4 py-2 rounded-full font-semibold ${
          status.running ? 'bg-green-900/50 text-green-400' : 'bg-red-900/50 text-red-400'
        }`}>
          {status.running ? '● Running' : '○ Stopped'}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-1">Uptime</div>
          <div className="text-white text-lg font-semibold">
            {uptimeHours}h {uptimeMinutes}m
          </div>
        </div>

        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-1">Tasks</div>
          <div className="text-white text-lg font-semibold">{status.task_count}</div>
        </div>

        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-1">Completed</div>
          <div className="text-green-400 text-lg font-semibold">{status.completed_tasks}</div>
        </div>

        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="text-gray-400 text-sm mb-1">Failed</div>
          <div className="text-red-400 text-lg font-semibold">{status.failed_tasks}</div>
        </div>
      </div>
    </div>
  );
}
