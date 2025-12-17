import { useWebSocket } from '../hooks/useWebSocket';

export function ConnectionStatus() {
  const { isConnected, connectionState, reconnect } = useWebSocket();

  const getStatusColor = () => {
    if (!isConnected) return 'bg-red-500';

    switch (connectionState) {
      case 'websocket':
        return 'bg-green-500';
      case 'polling':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusText = () => {
    if (!isConnected) return 'Disconnected';

    switch (connectionState) {
      case 'websocket':
        return 'WebSocket';
      case 'polling':
        return 'Polling';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${getStatusColor()}`} />
        <span className="text-sm text-gray-400">{getStatusText()}</span>
      </div>

      {!isConnected && connectionState !== 'connecting' && (
        <button
          onClick={reconnect}
          className="text-xs px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
        >
          Reconnect
        </button>
      )}
    </div>
  );
}
