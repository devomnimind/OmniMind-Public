import { apiService } from './api';

export type ConnectionMode = 'websocket' | 'polling' | 'offline';

export interface ConnectionMetrics {
  mode: ConnectionMode;
  isConnected: boolean;
  latency_ms: number;
  uptime_sec: number;
  reconnect_attempts: number;
  last_error: string | null;
  message_queue_length: number;
  total_messages_sent: number;
  total_messages_received: number;
  connection_stability: number; // 0-100, % time connected
}

export interface WebSocketMessage {
  type: string;
  data?: any;
  channel?: string;
  channels?: string[];
  timestamp?: number;
  id?: string;
}

class RobustConnectionService {
  private static instance: RobustConnectionService;

  // Connection state
  private ws: WebSocket | null = null;
  private currentMode: ConnectionMode = 'offline';
  private isConnected = false;

  // Retry logic
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 15; // Mais tentativas
  private reconnectDelay = 1000;
  private maxReconnectDelay = 30000;
  private reconnectTimeout: number | null = null;

  // Polling fallback
  private pollingInterval: number | null = null;
  private pollDelay = 2000;

  // Message handling
  private listeners: Set<(msg: WebSocketMessage) => void> = new Set();
  private connectionStateListeners: Set<(metrics: ConnectionMetrics) => void> = new Set();
  private messageQueue: WebSocketMessage[] = [];
  private messageQueueMaxSize = 500;

  // Metrics
  private metrics: ConnectionMetrics = {
    mode: 'offline',
    isConnected: false,
    latency_ms: 0,
    uptime_sec: 0,
    reconnect_attempts: 0,
    last_error: null,
    message_queue_length: 0,
    total_messages_sent: 0,
    total_messages_received: 0,
    connection_stability: 0
  };

  private connectionStartTime = 0;
  private totalConnectionTime = 0;
  private heartbeatInterval: number | null = null;
  private healthCheckInterval: number | null = null;

  // Circuit breaker
  private failureCount = 0;
  private circuitBreakerOpen = false;
  private circuitBreakerResetTime = 60000; // 60s

  private constructor() {
    this.initializeMetrics();
    this.start();
  }

  public static getInstance(): RobustConnectionService {
    if (!RobustConnectionService.instance) {
      RobustConnectionService.instance = new RobustConnectionService();
    }
    return RobustConnectionService.instance;
  }

  // ============ INITIALIZATION ============

  private initializeMetrics() {
    this.metrics = {
      mode: 'offline',
      isConnected: false,
      latency_ms: 0,
      uptime_sec: 0,
      reconnect_attempts: 0,
      last_error: null,
      message_queue_length: 0,
      total_messages_sent: 0,
      total_messages_received: 0,
      connection_stability: 0
    };

    // Load persisted queue
    try {
        const savedQueue = localStorage.getItem('omnimind_msg_queue');
        if (savedQueue) {
            this.messageQueue = JSON.parse(savedQueue);
            console.log(`[Connection] Restored ${this.messageQueue.length} messages from persistence`);
        }
    } catch (e) {
        console.error('[Connection] Failed to load persisted queue:', e);
    }
  }

  private persistQueue() {
      try {
          localStorage.setItem('omnimind_msg_queue', JSON.stringify(this.messageQueue));
      } catch (e) {
          console.error('[Connection] Failed to persist queue:', e);
      }
  }

  private start() {
    // Tenta WebSocket primeiro
    this.connectWebSocket();

    // Health check a cada 30s
    this.healthCheckInterval = window.setInterval(() => {
      this.healthCheck();
    }, 30000);

    // Heartbeat para manter conexão viva
    this.heartbeatInterval = window.setInterval(() => {
      this.sendHeartbeat();
    }, 45000);
  }

  // ============ WEBSOCKET CONNECTION ============

  private connectWebSocket() {
    if (this.circuitBreakerOpen) {
      console.log('[Connection] Circuit breaker open, skipping WebSocket');
      this.switchToPolling();
      return;
    }

    if (this.ws?.readyState === WebSocket.OPEN || this.ws?.readyState === WebSocket.CONNECTING) {
      return;
    }

    try {
      const token = apiService.getAuthToken();
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.hostname;

      // Try multiple ports: 8000, 8080, 3001 (fallback)
      const ports = ['8000', '8080', '3001'];
      const port = ports[this.reconnectAttempts % ports.length];

      let url = `${protocol}//${host}:${port}/ws`;
      if (token) {
        url += `?auth_token=${encodeURIComponent(token)}`;
      }

      console.log(`[Connection] Attempting WebSocket on port ${port}...`);

      this.ws = new WebSocket(url);
      this.ws.onopen = () => this.onWebSocketOpen();
      this.ws.onclose = () => this.onWebSocketClose();
      this.ws.onerror = (err) => this.onWebSocketError(err);
      this.ws.onmessage = (event) => this.onWebSocketMessage(event);

    } catch (error) {
      console.error('[Connection] WebSocket creation failed:', error);
      this.recordFailure('WebSocket creation failed');
      this.switchToPolling();
    }
  }

  private onWebSocketOpen() {
    console.log('[Connection] ✅ WebSocket connected');
    this.currentMode = 'websocket';
    this.isConnected = true;
    this.reconnectAttempts = 0;
    this.failureCount = 0;
    this.circuitBreakerOpen = false;
    this.connectionStartTime = Date.now();

    this.metrics.mode = 'websocket';
    this.metrics.isConnected = true;
    this.metrics.last_error = null;

    // Processa fila de mensagens
    this.processMessageQueue();

    // Notifica listeners
    this.notifyConnectionStateListeners();
  }

  private onWebSocketClose() {
    console.log('[Connection] WebSocket disconnected');
    this.isConnected = false;
    this.totalConnectionTime += Date.now() - this.connectionStartTime;

    this.attemptReconnect();
  }

  private onWebSocketError(error: Event) {
    console.error('[Connection] WebSocket error:', error);
    this.recordFailure('WebSocket error');
    this.metrics.last_error = 'WebSocket error';
  }

  private onWebSocketMessage(event: MessageEvent) {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      this.metrics.total_messages_received++;
      this.notifyListeners(message);
    } catch (e) {
      console.error('[Connection] Failed to parse WebSocket message:', e);
    }
  }

  // ============ POLLING FALLBACK ============

  private switchToPolling() {
    if (this.currentMode === 'polling') return;

    console.log('[Connection] Switching to HTTP polling');
    this.currentMode = 'polling';
    this.metrics.mode = 'polling';

    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }

    this.pollingInterval = window.setInterval(() => {
      this.pollBackend();
    }, this.pollDelay);
  }

  private async pollBackend() {
    try {
      const response = await fetch(`/api/omnimind/messages`, {
        headers: {
          'Authorization': `Bearer ${apiService.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const messages: WebSocketMessage[] = await response.json();
      this.isConnected = true;
      this.metrics.isConnected = true;
      this.failureCount = 0;

      messages.forEach(msg => {
        this.metrics.total_messages_received++;
        this.notifyListeners(msg);
      });

      // Processa fila
      this.processMessageQueue();

    } catch (error) {
      console.error('[Connection] Polling failed:', error);
      this.recordFailure('Polling failed');
    }
  }

  // ============ RETRY & RECONNECT ============

  private attemptReconnect() {
    if (this.currentMode === 'polling') {
      // Se já está em polling, não precisa fazer mais
      return;
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('[Connection] Max reconnect attempts reached, switching to polling');
      this.switchToPolling();
      return;
    }

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    // Exponential backoff com jitter
    const delay = Math.min(
      this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts),
      this.maxReconnectDelay
    ) + Math.random() * 1000;

    console.log(`[Connection] Reconnecting in ${delay.toFixed(0)}ms (attempt ${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);

    this.reconnectTimeout = window.setTimeout(() => {
      this.reconnectAttempts++;
      this.metrics.reconnect_attempts = this.reconnectAttempts;
      this.connectWebSocket();
    }, delay);
  }

  private recordFailure(reason: string) {
    this.failureCount++;
    this.metrics.last_error = reason;

    if (this.failureCount >= 3) {
      console.log('[Connection] Circuit breaker opened due to failures');
      this.circuitBreakerOpen = true;

      setTimeout(() => {
        console.log('[Connection] Circuit breaker reset');
        this.circuitBreakerOpen = false;
        this.failureCount = 0;
        this.reconnectAttempts = 0;
        this.connectWebSocket();
      }, this.circuitBreakerResetTime);
    }
  }

  // ============ MESSAGE HANDLING ============

  private processMessageQueue() {
    if (this.messageQueue.length === 0) return;

    console.log(`[Connection] Processing ${this.messageQueue.length} queued messages`);

    const toProcess = [...this.messageQueue];
    this.messageQueue = [];
    this.persistQueue();

    toProcess.forEach(msg => {
      this.sendDirect(msg);
    });
  }

  private sendDirect(message: WebSocketMessage) {
    const msgString = JSON.stringify(message);

    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(msgString);
      this.metrics.total_messages_sent++;
    } else if (this.currentMode === 'polling') {
      // Em polling, envia via HTTP POST
      fetch(`/api/omnimind/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiService.getAuthToken()}`
        },
        body: msgString
      }).catch(err => console.error('[Connection] HTTP POST failed:', err));
      this.metrics.total_messages_sent++;
    }
  }

  private sendHeartbeat() {
    if (this.isConnected) {
      this.sendDirect({
        type: 'heartbeat',
        timestamp: Date.now()
      });
    }
  }

  private healthCheck() {
    // Calcula uptime
    if (this.isConnected) {
      this.metrics.uptime_sec = (this.totalConnectionTime + (Date.now() - this.connectionStartTime)) / 1000;
    }

    // Calcula stability (% do tempo conectado)
    const totalTime = this.totalConnectionTime + (this.isConnected ? (Date.now() - this.connectionStartTime) : 0);
    this.metrics.connection_stability = totalTime > 0 ? Math.min(100, (this.metrics.uptime_sec / (totalTime / 1000)) * 100) : 0;

    // Calcula latência (ping simples)
    if (this.isConnected) {
      const pingStart = Date.now();
      this.sendDirect({
        type: 'ping',
        id: `ping_${pingStart}`,
        timestamp: pingStart
      });
    }

    this.metrics.message_queue_length = this.messageQueue.length;
    this.notifyConnectionStateListeners();

    console.log(`[Connection] Health: ${this.metrics.mode} | Stable: ${this.metrics.connection_stability.toFixed(1)}% | Queue: ${this.metrics.message_queue_length}`);
  }

  // ============ PUBLIC API ============

  public send(message: WebSocketMessage): void {
    if (this.messageQueue.length >= this.messageQueueMaxSize) {
      console.warn('[Connection] Message queue full, dropping oldest message');
      this.messageQueue.shift();
    }

    this.messageQueue.push(message);
    this.persistQueue();

    if (this.isConnected) {
      this.processMessageQueue();
    }
  }

  public subscribe(listener: (msg: WebSocketMessage) => void): () => void {
    this.listeners.add(listener);
    return () => { this.listeners.delete(listener); };
  }

  public subscribeToMetrics(listener: (metrics: ConnectionMetrics) => void): () => void {
    this.connectionStateListeners.add(listener);
    listener(this.metrics); // Notifica imediatamente
    return () => { this.connectionStateListeners.delete(listener); };
  }

  public getMetrics(): ConnectionMetrics {
    return { ...this.metrics };
  }

  public reconnect(): void {
    console.log('[Connection] Manual reconnect requested');
    this.reconnectAttempts = 0;
    this.failureCount = 0;
    this.circuitBreakerOpen = false;

    if (this.ws) {
      this.ws.close();
    }
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }

    this.connectWebSocket();
  }

  public disconnect(): void {
    console.log('[Connection] Disconnecting...');

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.isConnected = false;
    this.metrics.isConnected = false;
  }

  private notifyListeners(message: WebSocketMessage) {
    this.listeners.forEach(listener => {
      try {
        listener(message);
      } catch (e) {
        console.error('[Connection] Listener error:', e);
      }
    });
  }

  private notifyConnectionStateListeners() {
    this.connectionStateListeners.forEach(listener => {
      try {
        listener(this.metrics);
      } catch (e) {
        console.error('[Connection] Metrics listener error:', e);
      }
    });
  }
}

export const connectionService = RobustConnectionService.getInstance();
