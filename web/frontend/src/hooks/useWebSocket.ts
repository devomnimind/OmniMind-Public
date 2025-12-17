import { useEffect, useState, useCallback } from 'react';
import { connectionService, type WebSocketMessage, type ConnectionMetrics } from '../services/robust-connection';

/**
 * Custom hook for WebSocket connection management
 * Wraps the robust connection service for React components
 */
export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<string>('disconnected');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  // Handle connection state changes
  useEffect(() => {
    // Get initial state
    const initialMetrics = connectionService.getMetrics();
    setIsConnected(initialMetrics.isConnected);
    setConnectionState(initialMetrics.mode);

    const unsubscribe = connectionService.subscribeToMetrics((metrics: ConnectionMetrics) => {
      setIsConnected(metrics.isConnected);
      setConnectionState(metrics.mode);
    });

    return unsubscribe;
  }, []);

  // Handle incoming messages
  useEffect(() => {
    // CORREÇÃO (2025-12-09): Usar função estável para evitar re-subscriptions
    let isMounted = true;

    const unsubscribe = connectionService.subscribe((message: WebSocketMessage) => {
      // Só atualizar se componente ainda estiver montado
      if (isMounted) {
        setLastMessage(message);
      }
    });

    return () => {
      isMounted = false;
      unsubscribe();
    };
  }, []);

  // Note: We do NOT auto-connect/disconnect here anymore because connectionService is a Singleton
  // that manages its own lifecycle. We just subscribe to it.

  const send = useCallback((message: any) => {
    connectionService.send(message);
  }, []);

  const reconnect = useCallback(() => {
    connectionService.reconnect();
  }, []);

  return {
    isConnected,
    connectionState,
    lastMessage,
    send,
    reconnect,
  };
}
