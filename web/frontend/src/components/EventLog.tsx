import { useDaemonStore } from '../store/daemonStore';

export function EventLog() {
  const status = useDaemonStore((state) => state.status);

  if (!status?.event_log || status.event_log.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-6">Event Log</h2>
        <div className="text-gray-400 text-center py-8">
          No events recorded yet
        </div>
      </div>
    );
  }

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'SUCCESS':
        return '✅';
      case 'WARNING':
        return '⚠️';
      case 'ERROR':
        return '❌';
      case 'INFO':
      default:
        return '📊';
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'SUCCESS':
        return 'text-green-400 border-green-500/20';
      case 'WARNING':
        return 'text-yellow-400 border-yellow-500/20';
      case 'ERROR':
        return 'text-red-400 border-red-500/20';
      case 'INFO':
      default:
        return 'text-blue-400 border-blue-500/20';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const formatValueChange = (oldValue?: number, newValue?: number) => {
    if (oldValue === undefined || newValue === undefined) return '';
    const change = newValue - oldValue;
    const percent = Math.abs(change / oldValue) * 100;
    const symbol = change > 0 ? '↑' : change < 0 ? '↓' : '→';
    return `${oldValue.toFixed(2)} → ${newValue.toFixed(2)} (${symbol}${percent.toFixed(1)}%)`;
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Event Log</h2>
        <div className="text-sm text-gray-400">
          Last {status.event_log.length} events
        </div>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {status.event_log.slice(0, 10).map((event, index) => (
          <div
            key={index}
            className={`border-l-4 rounded-lg p-3 bg-gray-700/30 ${getEventColor(event.type)}`}
          >
            <div className="flex items-start gap-3">
              <span className="text-lg">{getEventIcon(event.type)}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-white font-medium text-sm">
                    {event.metric ? `${event.metric} ${event.type}` : event.type}
                  </span>
                  <span className="text-gray-400 text-xs">
                    {formatTimestamp(event.timestamp)}
                  </span>
                </div>

                <p className="text-gray-300 text-sm mb-2">
                  {event.message}
                </p>

                {event.old_value !== undefined && event.new_value !== undefined && (
                  <div className="text-xs text-gray-400 bg-gray-800/50 rounded px-2 py-1 inline-block">
                    {formatValueChange(event.old_value, event.new_value)}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {status.event_log.length > 10 && (
        <div className="mt-4 text-center">
          <button className="btn-outline-neon text-sm">
            📜 View All Events ({status.event_log.length})
          </button>
        </div>
      )}
    </div>
  );
}