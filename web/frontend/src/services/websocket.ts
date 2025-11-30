/**
 * WebSocket service for real-time updates from OmniMind daemon
 * Features:
 * - Auto-reconnect on connection loss
 * - Exponential backoff retry strategy
 * - Event-based message handling
 * - Connection state tracking
 */

import { apiService } from './api';

export interface WebSocketMessage {
  type: string;
  data?: any;
  channel?: string;
  channels?: string[];
  client_id?: string;
  timestamp?: number;
}

export type ConnectionState = { isConnected: boolean; error: string | null };

class WebSocketService {
  private static instance: WebSocketService;
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout: number | null = null;
  private listeners: Set<(msg: WebSocketMessage) => void> = new Set();
  private connectionStateListeners: Set<(state: ConnectionState) => void> = new Set();
  private state: ConnectionState = { isConnected: false, error: null };
  private messageQueue: string[] = [];

  private constructor() {
    this.connect();
  }

  public static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService();
    }
    return WebSocketService.instance;
  }

  private connect() {
    if (this.ws?.readyState === WebSocket.OPEN || this.ws?.readyState === WebSocket.CONNECTING) return;

    const token = apiService.getAuthToken(); // Use existing apiService for token
    // Use window.location.hostname to work in both local and network environments
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    // Assume backend is on port 8000 for now, or use env var
    const port = '8000';

    let url = `${protocol}//${host}:${port}/ws`;
    if (token) {
      url += `?auth_token=${encodeURIComponent(token)}`;
    }

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('[WebSocket] Connected');
      this.updateState({ isConnected: true, error: null });
      this.reconnectAttempts = 0;
      this.processMessageQueue();
    };

    this.ws.onclose = () => {
      console.log('[WebSocket] Disconnected');
      this.updateState({ isConnected: false, error: null });
      this.attemptReconnect();
    };

    this.ws.onerror = (error) => {
      console.debug('[WebSocket] Error:', error);
      this.updateState({ isConnected: false, error: 'Connection error' });
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.notifyListeners(message);
      } catch (e) {
        console.error('[WebSocket] Failed to parse message:', e);
      }
    };
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.debug('[WebSocket] Max reconnect attempts reached');
      return;
    }

    if (this.reconnectTimeout) {
        window.clearTimeout(this.reconnectTimeout);
    }

    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);
    this.reconnectTimeout = window.setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  private updateState(newState: Partial<ConnectionState>) {
    this.state = { ...this.state, ...newState };
    this.notifyConnectionStateListeners();
  }

  private notifyListeners(message: WebSocketMessage) {
    this.listeners.forEach(listener => listener(message));
  }

  private notifyConnectionStateListeners() {
    this.connectionStateListeners.forEach(listener => listener(this.state));
  }

  private processMessageQueue() {
      while (this.messageQueue.length > 0 && this.ws?.readyState === WebSocket.OPEN) {
          const msg = this.messageQueue.shift();
          if (msg) this.ws.send(msg);
      }
  }

  public subscribe(listener: (msg: WebSocketMessage) => void) {
    this.listeners.add(listener);
    return () => { this.listeners.delete(listener); };
  }

  public subscribeToConnectionState(listener: (state: ConnectionState) => void) {
    this.connectionStateListeners.add(listener);
    // Immediately notify current state
    listener(this.state);
    return () => { this.connectionStateListeners.delete(listener); };
  }

  public send(message: unknown): void {
    const msgString = JSON.stringify(message);
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(msgString);
    } else {
      console.debug('[WebSocket] Queuing message - not connected');
      this.messageQueue.push(msgString);
    }
  }

  public reconnect() {
    this.reconnectAttempts = 0;
    if (this.ws) {
        this.ws.close();
    } else {
        this.connect();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  public disconnect(): void {
    console.log('[WebSocket] Disconnecting...');
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Singleton instance
export const wsService = WebSocketService.getInstance();
