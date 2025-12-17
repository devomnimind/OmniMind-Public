import { useDaemonStore } from '../store/daemonStore';

export function ModuleActivityHeatmap() {
  const status = useDaemonStore((state) => state.status);

  if (!status?.module_activity) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-6">Module Activity</h2>
        <div className="text-gray-400 text-center py-8">
          Module activity data not available
        </div>
      </div>
    );
  }

  const activity = status.module_activity;

  const getActivityColor = (percentage: number) => {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 60) return 'bg-green-400';
    if (percentage >= 40) return 'bg-yellow-400';
    if (percentage >= 20) return 'bg-orange-400';
    return 'bg-red-400';
  };

  const getActivityIntensity = (percentage: number) => {
    return Math.min(percentage / 100, 1);
  };

  const modules = [
    { key: 'orchestrator' as keyof typeof activity, name: 'Orchestrator', icon: '🪃' },
    { key: 'consciousness' as keyof typeof activity, name: 'Consciousness', icon: '🧠' },
    { key: 'audit' as keyof typeof activity, name: 'Audit', icon: '🔍' },
    { key: 'autopoietic' as keyof typeof activity, name: 'Autopoietic', icon: '🔄' },
    { key: 'ethics' as keyof typeof activity, name: 'Ethics', icon: '⚖️' },
    { key: 'attention' as keyof typeof activity, name: 'Attention', icon: '👁️' },
  ];

  const maxActivity = Math.max(...Object.values(activity));

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
        🔥 Module Activity Heatmap
        <span className="text-sm text-gray-400 font-normal">(Real-time)</span>
      </h2>

      <div className="space-y-3">
        {modules.map((module) => {
          const percentage = activity[module.key];
          const intensity = getActivityIntensity(percentage);

          return (
            <div key={module.key} className="flex items-center gap-4">
              <div className="flex items-center gap-3 min-w-0 flex-1">
                <span className="text-2xl">{module.icon}</span>
                <div className="min-w-0 flex-1">
                  <div className="text-white font-medium text-sm truncate">
                    {module.name}
                  </div>
                  <div className="text-gray-400 text-xs">
                    Activity Level
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3 flex-1">
                <div className="flex-1 bg-gray-700 rounded-full h-4 overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 ${getActivityColor(percentage)}`}
                    style={{
                      width: `${percentage}%`,
                      opacity: 0.3 + (intensity * 0.7)
                    }}
                  ></div>
                </div>
                <div className="text-white font-semibold text-sm min-w-[3rem] text-right">
                  {percentage.toFixed(0)}%
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-700">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>Peak Activity: {maxActivity.toFixed(0)}%</span>
          <div className="flex items-center gap-2">
            <span>Low</span>
            <div className="flex gap-1">
              <div className="w-3 h-3 rounded bg-red-400"></div>
              <div className="w-3 h-3 rounded bg-orange-400"></div>
              <div className="w-3 h-3 rounded bg-yellow-400"></div>
              <div className="w-3 h-3 rounded bg-green-400"></div>
              <div className="w-3 h-3 rounded bg-green-500"></div>
            </div>
            <span>High</span>
          </div>
        </div>
      </div>

      <div className="mt-4 text-center">
        <button className="btn-outline-neon text-sm">
          📊 Detailed Module Metrics
        </button>
      </div>
    </div>
  );
}