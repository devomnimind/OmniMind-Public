import { useDaemonStore } from '../store/daemonStore';

const PRIORITY_COLORS = {
  CRITICAL: 'bg-red-900/50 text-red-400 border-red-500',
  HIGH: 'bg-orange-900/50 text-orange-400 border-orange-500',
  MEDIUM: 'bg-yellow-900/50 text-yellow-400 border-yellow-500',
  LOW: 'bg-blue-900/50 text-blue-400 border-blue-500',
};

export function TaskList() {
  const tasks = useDaemonStore((state) => state.tasks);

  const formatInterval = (seconds: number | null) => {
    if (!seconds) return 'One-time';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `Every ${hours}h ${minutes}m`;
    return `Every ${minutes}m`;
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'Never';
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-2xl font-bold text-white mb-6">Tasks</h2>

      {tasks.length === 0 ? (
        <div className="text-center text-gray-400 py-8">
          No tasks registered
        </div>
      ) : (
        <div className="space-y-4">
          {tasks.map((task, index) => (
            <div
              key={`${task.task_id}-${task.stats.last_execution ?? task.stats.total_executions}-${index}`}
              className="bg-gray-700/50 rounded-lg p-4 border border-gray-600"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-white font-semibold text-lg mb-1">{task.name}</h3>
                  <p className="text-gray-400 text-sm">{task.description}</p>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-semibold border ${PRIORITY_COLORS[task.priority]}`}>
                  {task.priority}
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div>
                  <div className="text-gray-400 mb-1">Interval</div>
                  <div className="text-white">{formatInterval(task.repeat_interval_seconds)}</div>
                </div>

                <div>
                  <div className="text-gray-400 mb-1">Executions</div>
                  <div className="text-white">{task.stats.total_executions}</div>
                </div>

                <div>
                  <div className="text-gray-400 mb-1">Success Rate</div>
                  <div className="text-green-400">
                    {task.stats.total_executions > 0
                      ? `${((task.stats.successful_executions / task.stats.total_executions) * 100).toFixed(0)}%`
                      : 'N/A'}
                  </div>
                </div>

                <div>
                  <div className="text-gray-400 mb-1">Last Run</div>
                  <div className="text-white text-xs">{formatDate(task.stats.last_execution)}</div>
                </div>
              </div>

              {task.stats.last_failure && (
                <div className="mt-3 bg-red-900/30 border border-red-500/50 rounded p-2 text-xs text-red-300">
                  Last failure: {formatDate(task.stats.last_failure)}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
