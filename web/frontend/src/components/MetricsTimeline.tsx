import { useDaemonStore } from '../store/daemonStore';
import { useState } from 'react';

export function MetricsTimeline() {
  const status = useDaemonStore((state) => state.status);
  const [selectedMetric, setSelectedMetric] = useState<string>('phi');

  if (!status?.consciousness_metrics?.history) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-6">Metrics Timeline</h2>
        <div className="text-gray-400 text-center py-8">
          Historical metrics data not available
        </div>
      </div>
    );
  }

  const history = status.consciousness_metrics.history;
  const metrics = ['phi', 'anxiety', 'flow', 'entropy'] as const;

  const getCurrentValue = (metric: string) => {
    const consciousness = status.consciousness_metrics;
    if (!consciousness) return 0;

    switch (metric) {
      case 'phi':
        return consciousness.phi || 0;
      case 'anxiety':
        return consciousness.anxiety || 0;
      case 'flow':
        return consciousness.flow || 0;
      case 'entropy':
        return consciousness.entropy || 0;
      default:
        return 0;
    }
  };

  const getMetricData = (metric: string) => {
    const data = history[metric as keyof typeof history] as number[] | undefined;
    return data || [];
  };

  const getMetricColor = (metric: string) => {
    switch (metric) {
      case 'phi':
        return 'text-purple-400 border-purple-500/20';
      case 'anxiety':
        return 'text-red-400 border-red-500/20';
      case 'flow':
        return 'text-blue-400 border-blue-500/20';
      case 'entropy':
        return 'text-orange-400 border-orange-500/20';
      default:
        return 'text-gray-400 border-gray-500/20';
    }
  };

  const getTrend = (data: number[]) => {
    if (data.length < 2) return '→';
    const recent = data.slice(-5);
    const avgRecent = recent.reduce((a, b) => a + b, 0) / recent.length;
    const avgOlder = data.slice(-10, -5).reduce((a, b) => a + b, 0) / Math.min(5, data.slice(-10, -5).length) || avgRecent;

    if (avgRecent > avgOlder * 1.05) return '↗️';
    if (avgRecent < avgOlder * 0.95) return '↘️';
    return '→';
  };

  const formatTimeAgo = (index: number, total: number) => {
    const minutesAgo = (total - index - 1) * 10; // Assuming 10-minute intervals
    if (minutesAgo === 0) return 'Now';
    if (minutesAgo < 60) return `${minutesAgo}m ago`;
    const hours = Math.floor(minutesAgo / 60);
    return `${hours}h ago`;
  };

  const selectedData = getMetricData(selectedMetric);
  const currentValue = getCurrentValue(selectedMetric);

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Metrics Timeline</h2>
        <div className="text-sm text-gray-400">
          Last 30 minutes
        </div>
      </div>

      {/* Metric Selector */}
      <div className="flex gap-2 mb-6 overflow-x-auto">
        {metrics.map((metric) => {
          const data = getMetricData(metric);
          const trend = getTrend(data);
          const isSelected = selectedMetric === metric;

          return (
            <button
              key={metric}
              onClick={() => setSelectedMetric(metric)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                isSelected
                  ? `bg-gray-700 ${getMetricColor(metric)}`
                  : 'bg-gray-700/50 text-gray-400 hover:bg-gray-700/70'
              }`}
            >
              {metric.toUpperCase()} {trend}
            </button>
          );
        })}
      </div>

      {/* Timeline Visualization */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-white font-semibold">
            {selectedMetric.toUpperCase()} Timeline
          </h3>
          <div className={`text-xl font-bold ${getMetricColor(selectedMetric)}`}>
            {currentValue.toFixed(3)} ← Current
          </div>
        </div>

        <div className="flex items-end gap-1 h-32 bg-gray-900/30 rounded-lg p-4 overflow-x-auto">
          {selectedData.slice(-6).map((value, index) => {
            const height = Math.max((value * 100), 5); // Minimum height of 5%
            const isCurrent = index === selectedData.slice(-6).length - 1;

            return (
              <div key={index} className="flex flex-col items-center gap-2 flex-shrink-0">
                <div
                  className={`w-8 rounded-t transition-all duration-300 ${
                    isCurrent ? 'bg-gradient-to-t from-blue-500 to-blue-400' : 'bg-gray-600'
                  }`}
                  style={{ height: `${height}%` }}
                ></div>
                <div className="text-xs text-gray-400 text-center">
                  {formatTimeAgo(index, selectedData.slice(-6).length)}
                </div>
              </div>
            );
          })}
        </div>

        <div className="flex justify-between text-xs text-gray-400 mt-2">
          <span>T-30min</span>
          <span>Now</span>
        </div>
      </div>

      {/* Trend Analysis */}
      <div className="bg-gray-700/30 rounded-lg p-4">
        <h4 className="text-white font-semibold mb-3">Trend Analysis</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-400">Current</div>
            <div className={`font-semibold ${getMetricColor(selectedMetric)}`}>
              {currentValue.toFixed(3)}
            </div>
          </div>
          <div>
            <div className="text-gray-400">5min Avg</div>
            <div className="text-white font-semibold">
              {(selectedData.slice(-5).reduce((a, b) => a + b, 0) / Math.min(5, selectedData.slice(-5).length)).toFixed(3)}
            </div>
          </div>
          <div>
            <div className="text-gray-400">Trend</div>
            <div className="text-white font-semibold">
              {getTrend(selectedData)} {Math.abs(
                (selectedData.slice(-5).reduce((a, b) => a + b, 0) / Math.min(5, selectedData.slice(-5).length)) -
                (selectedData.slice(-10, -5).reduce((a, b) => a + b, 0) / Math.min(5, selectedData.slice(-10, -5).length) || 0)
              ).toFixed(3)}
            </div>
          </div>
          <div>
            <div className="text-gray-400">Volatility</div>
            <div className="text-white font-semibold">
              {selectedData.length > 1 ?
                (selectedData.slice(-10).reduce((acc, val, i, arr) => {
                  if (i === 0) return acc;
                  return acc + Math.abs(val - arr[i-1]);
                }, 0) / (selectedData.slice(-10).length - 1)).toFixed(3) : '0.000'
              }
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}