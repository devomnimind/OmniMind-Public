import { useEffect, useState, useCallback } from 'react';
import { wsService, type WebSocketMessage, type ConnectionState } from '../services/websocket';

/**
 * Custom hook for WebSocket connection management
 * Automatically connects on mount and disconnects on unmount
 */
export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  // Handle connection state changes
  useEffect(() => {
    const unsubscribe = wsService.onStateChange((state) => {
      setConnectionState(state);
      setIsConnected(state === 'connected');
    });

    return unsubscribe;
  }, []);

  // Handle incoming messages
  useEffect(() => {
    const unsubscribe = wsService.onMessage((message) => {
      setLastMessage(message);
    });

    return unsubscribe;
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    wsService.connect();

    return () => {
      wsService.disconnect();
    };
  }, []);

  const send = useCallback((message: unknown) => {
    wsService.send(message);
  }, []);

  const reconnect = useCallback(() => {
    wsService.disconnect();
    setTimeout(() => wsService.connect(), 100);
  }, []);

  return {
    isConnected,
    connectionState,
    lastMessage,
    send,
    reconnect,
  };
}
