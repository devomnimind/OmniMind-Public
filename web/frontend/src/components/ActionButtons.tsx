import { useState } from 'react';
import { useDaemonStore } from '../store/daemonStore';
import { apiService } from '../services/api';

export function ActionButtons() {
  const [isExporting, setIsExporting] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const status = useDaemonStore((state) => state.status);

  const handleExport = async (format: 'json' | 'csv') => {
    setIsExporting(true);
    try {
      // Mock export functionality
      const data = {
        timestamp: new Date().toISOString(),
        system_status: status,
        export_format: format,
      };

      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json'
      });

      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `omnimind-metrics-${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const handleDeepDive = () => {
    // Open detailed analysis modal or navigate to detailed view
    console.log('Opening deep dive analysis...');
  };

  const handleAdjustThresholds = () => {
    // Open threshold configuration modal
    console.log('Opening threshold configuration...');
  };

  const handleResetMetrics = async () => {
    if (confirm('Are you sure you want to reset all metrics? This action cannot be undone.')) {
      try {
        await apiService.resetMetrics();
        console.log('Metrics reset successfully');
      } catch (error) {
        console.error('Failed to reset metrics:', error);
      }
    }
  };

  const handleStartRecording = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      console.log('Started session recording...');
    } else {
      console.log('Stopped session recording...');
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
        🎛️ Debug & Control Panel
        <span className="text-sm text-gray-400 font-normal">(Advanced Actions)</span>
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Export Actions */}
        <div className="bg-gray-700/30 rounded-lg p-4">
          <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
            📊 Export Metrics
          </h3>
          <div className="space-y-2">
            <button
              onClick={() => handleExport('json')}
              disabled={isExporting}
              className="w-full btn-outline-neon text-sm disabled:opacity-50"
            >
              {isExporting ? '📤 Exporting...' : '📄 Export JSON'}
            </button>
            <button
              onClick={() => handleExport('csv')}
              disabled={isExporting}
              className="w-full btn-outline-neon text-sm disabled:opacity-50"
            >
              {isExporting ? '📤 Exporting...' : '📊 Export CSV'}
            </button>
          </div>
        </div>

        {/* Analysis Actions */}
        <div className="bg-gray-700/30 rounded-lg p-4">
          <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
            🔍 Deep Analysis
          </h3>
          <div className="space-y-2">
            <button
              onClick={handleDeepDive}
              className="w-full btn-outline-neon text-sm"
            >
              🔬 Deep Dive
            </button>
            <button
              onClick={handleAdjustThresholds}
              className="w-full btn-outline-neon text-sm"
            >
              ⚙️ Adjust Thresholds
            </button>
          </div>
        </div>

        {/* System Actions */}
        <div className="bg-gray-700/30 rounded-lg p-4">
          <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
            🔧 System Control
          </h3>
          <div className="space-y-2">
            <button
              onClick={handleResetMetrics}
              className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
            >
              🔄 Reset Metrics
            </button>
            <button
              onClick={handleStartRecording}
              className={`w-full px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
                isRecording
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'btn-outline-neon'
              }`}
            >
              {isRecording ? '⏹️ Stop Recording' : '🎥 Start Recording'}
            </button>
          </div>
        </div>
      </div>

      {/* Status Indicators */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-gray-500'}`}></div>
              <span className="text-gray-400">
                Recording: {isRecording ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500"></div>
              <span className="text-gray-400">
                Auto-export: Enabled
              </span>
            </div>
          </div>

          <div className="text-gray-400">
            Last action: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Quick Commands */}
      <div className="mt-4 bg-gray-700/50 rounded-lg p-3">
        <h4 className="text-white font-semibold mb-2">Quick Commands</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
          <button className="btn-outline-neon px-2 py-1">🔍 Inspect</button>
          <button className="btn-outline-neon px-2 py-1">📋 Copy Logs</button>
          <button className="btn-outline-neon px-2 py-1">📈 Generate Report</button>
          <button className="btn-outline-neon px-2 py-1">🔔 Send Alert</button>
        </div>
      </div>
    </div>
  );
}