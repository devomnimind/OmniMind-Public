import { useDaemonStore } from '../store/daemonStore';

export function SystemHealthSummary() {
  const status = useDaemonStore((state) => state.status);

  if (!status?.system_health) return null;

  const health = status.system_health;

  const getHealthColor = (status: string) => {
    switch (status.toUpperCase()) {
      case 'STABLE':
      case 'GOOD':
      case 'NORMAL':
      case 'CALM':
      case 'CLEAN':
        return 'text-green-400';
      case 'WARNING':
      case 'MODERATE':
      case 'FLUID':
        return 'text-yellow-400';
      case 'CRITICAL':
      case 'POOR':
      case 'HIGH':
      case 'BLOCKED':
      case 'ISSUES':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const getHealthIcon = (status: string) => {
    switch (status.toUpperCase()) {
      case 'STABLE':
      case 'GOOD':
      case 'NORMAL':
      case 'CALM':
      case 'CLEAN':
        return '🟢';
      case 'WARNING':
      case 'MODERATE':
      case 'FLUID':
        return '🟡';
      case 'CRITICAL':
      case 'POOR':
      case 'HIGH':
      case 'BLOCKED':
      case 'ISSUES':
        return '🔴';
      default:
        return '⚪';
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
        🏥 System Health Summary
        <span className="text-sm text-gray-400 font-normal">(Real-time Status)</span>
      </h2>

      <div className="bg-gray-900/50 rounded-lg p-4 mb-6">
        <div className="text-center">
          <div className={`text-3xl font-bold mb-2 ${getHealthColor(health.overall)}`}>
            {getHealthIcon(health.overall)} {health.overall}
          </div>
          <p className="text-gray-400 text-sm">Overall System Status</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div className="bg-gray-700/30 rounded-lg p-3 text-center">
          <div className="text-gray-400 text-xs mb-1">Integration</div>
          <div className={`font-semibold ${getHealthColor(health.integration)}`}>
            {getHealthIcon(health.integration)} {health.integration}
          </div>
        </div>

        <div className="bg-gray-700/30 rounded-lg p-3 text-center">
          <div className="text-gray-400 text-xs mb-1">Coherence</div>
          <div className={`font-semibold ${getHealthColor(health.coherence)}`}>
            {getHealthIcon(health.coherence)} {health.coherence}
          </div>
        </div>

        <div className="bg-gray-700/30 rounded-lg p-3 text-center">
          <div className="text-gray-400 text-xs mb-1">Anxiety</div>
          <div className={`font-semibold ${getHealthColor(health.anxiety)}`}>
            {getHealthIcon(health.anxiety)} {health.anxiety}
          </div>
        </div>

        <div className="bg-gray-700/30 rounded-lg p-3 text-center">
          <div className="text-gray-400 text-xs mb-1">Flow</div>
          <div className={`font-semibold ${getHealthColor(health.flow)}`}>
            {getHealthIcon(health.flow)} {health.flow}
          </div>
        </div>

        <div className="bg-gray-700/30 rounded-lg p-3 text-center">
          <div className="text-gray-400 text-xs mb-1">Audit</div>
          <div className={`font-semibold ${getHealthColor(health.audit)}`}>
            {getHealthIcon(health.audit)} {health.audit}
          </div>
        </div>

        <div className="bg-gray-700/30 rounded-lg p-3 text-center">
          <div className="text-gray-400 text-xs mb-1">Last Check</div>
          <div className="text-white font-semibold text-xs">
            {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>

      <div className="mt-6 text-center">
        <button className="btn-outline-neon text-sm">
          🔍 Detailed Health Report
        </button>
      </div>
    </div>
  );
}