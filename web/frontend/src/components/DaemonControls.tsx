import { useState } from 'react';
import { apiService } from '../services/api';
import { useDaemonStore } from '../store/daemonStore';

export function DaemonControls() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const status = useDaemonStore((state) => state.status);

  const handleStart = async () => {
    setLoading(true);
    setMessage('');
    try {
      const result = await apiService.startDaemon();
      setMessage(result.message);
    } catch (err) {
      setMessage(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    setMessage('');
    try {
      const result = await apiService.stopDaemon();
      setMessage(result.message);
    } catch (err) {
      setMessage(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-2xl font-bold text-white mb-6">Daemon Controls</h2>

      <div className="flex gap-4 mb-4">
        <button
          onClick={handleStart}
          disabled={loading || status?.running}
          className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors"
        >
          {loading ? 'Starting...' : 'Start Daemon'}
        </button>

        <button
          onClick={handleStop}
          disabled={loading || !status?.running}
          className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors"
        >
          {loading ? 'Stopping...' : 'Stop Daemon'}
        </button>
      </div>

      {message && (
        <div className={`p-4 rounded-lg ${
          message.includes('Error') 
            ? 'bg-red-900/50 border border-red-500 text-red-200'
            : 'bg-green-900/50 border border-green-500 text-green-200'
        }`}>
          {message}
        </div>
      )}

      <div className="mt-6 text-sm text-gray-400 space-y-2">
        <p>💡 <strong>Note:</strong> The daemon also runs as a systemd service.</p>
        <p className="font-mono text-xs bg-gray-700 p-2 rounded">
          sudo systemctl start/stop omnimind-daemon
        </p>
      </div>
    </div>
  );
}
