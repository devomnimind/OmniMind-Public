import { useDaemonStore } from '../store/daemonStore';

export function BaselineComparison() {
  const status = useDaemonStore((state) => state.status);

  if (!status?.baseline_comparison) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-6">Baseline Comparison</h2>
        <div className="text-gray-400 text-center py-8">
          Baseline comparison data not available
        </div>
      </div>
    );
  }

  const comparison = status.baseline_comparison;

  const getChangeColor = (change: number) => {
    if (Math.abs(change) < 1) return 'text-gray-400';
    return change > 0 ? 'text-green-400' : 'text-red-400';
  };

  const getChangeIcon = (change: number) => {
    if (Math.abs(change) < 1) return '→';
    return change > 0 ? '↗️' : '↘️';
  };

  const formatChange = (change: number) => {
    const sign = change > 0 ? '+' : '';
    return `${sign}${change.toFixed(1)}%`;
  };

  const metrics = [
    { key: 'phi' as keyof typeof comparison, name: 'Phi (Φ)', icon: 'Φ' },
    { key: 'ici' as keyof typeof comparison, name: 'ICI', icon: '🧠' },
    { key: 'prs' as keyof typeof comparison, name: 'PRS', icon: '🎯' },
    { key: 'anxiety' as keyof typeof comparison, name: 'Anxiety', icon: '😰' },
    { key: 'flow' as keyof typeof comparison, name: 'Flow', icon: '🌊' },
    { key: 'entropy' as keyof typeof comparison, name: 'Entropy', icon: '🔄' },
  ];

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Baseline Comparison</h2>
        <div className="text-sm text-gray-400">
          vs Yesterday's Average
        </div>
      </div>

      <div className="space-y-4">
        {metrics.map((metric) => {
          const data = comparison[metric.key];
          if (!data) return null;

          const changePercent = data.change;
          const isSignificant = Math.abs(changePercent) > 5;

          return (
            <div key={metric.key} className="bg-gray-700/30 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-lg">{metric.icon}</span>
                  <div>
                    <div className="text-white font-medium">{metric.name}</div>
                    <div className="text-gray-400 text-xs">Current vs Baseline</div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-white font-semibold">
                    {data.current.toFixed(3)}
                  </div>
                  <div className="text-gray-400 text-xs">
                    vs {data.baseline.toFixed(3)}
                  </div>
                </div>
              </div>

              <div className="mt-3 flex items-center justify-between">
                <div className={`flex items-center gap-2 text-sm font-medium ${getChangeColor(changePercent)}`}>
                  <span>{getChangeIcon(changePercent)}</span>
                  <span>{formatChange(changePercent)}</span>
                  {isSignificant && <span className="text-xs">(Significant)</span>}
                </div>

                <div className="text-xs text-gray-400">
                  {changePercent > 0 ? 'Above' : changePercent < 0 ? 'Below' : 'At'} baseline
                </div>
              </div>

              {/* Progress bar showing the change */}
              <div className="mt-2 w-full bg-gray-600 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${
                    changePercent > 0 ? 'bg-green-500' : changePercent < 0 ? 'bg-red-500' : 'bg-gray-500'
                  }`}
                  style={{
                    width: `${Math.min(Math.abs(changePercent), 100)}%`,
                    marginLeft: changePercent < 0 ? `${100 - Math.min(Math.abs(changePercent), 100)}%` : '0%'
                  }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-700">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>Baseline: Yesterday's 24h average</span>
          <div className="flex items-center gap-2">
            <span>Significant change: ±5%</span>
            <button className="btn-outline-neon text-xs px-3 py-1">
              📅 Change Period
            </button>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="mt-4 bg-gray-700/50 rounded-lg p-3">
        <div className="text-sm text-gray-300">
          <strong>Summary:</strong> {
            Object.values(comparison).filter(m => m && Math.abs(m.change) > 5).length > 0
              ? `${Object.values(comparison).filter(m => m && Math.abs(m.change) > 5).length} metrics show significant changes from baseline.`
              : 'All metrics are within normal range compared to baseline.'
          }
        </div>
      </div>
    </div>
  );
}