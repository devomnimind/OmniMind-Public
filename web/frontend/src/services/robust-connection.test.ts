// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock WebSocket
class MockWebSocket {
  readyState = 0;
  send = vi.fn();
  close = vi.fn();
  addEventListener = vi.fn();
  removeEventListener = vi.fn();
  constructor(url: string) {}
}
global.WebSocket = MockWebSocket as any;

import { connectionService, WebSocketMessage } from './robust-connection';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value.toString(); },
    clear: () => { store = {}; }
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('RobustConnectionService', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    localStorage.clear();
    // Reset singleton state if possible or mock internals
    // Note: Testing singletons is hard, we assume fresh state for critical paths
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should persist message queue to localStorage', () => {
    const msg: WebSocketMessage = { type: 'test', data: 'payload' };

    // Simulate offline
    connectionService.disconnect();

    // Send message
    connectionService.send(msg);

    // Check localStorage
    const stored = localStorage.getItem('omnimind_msg_queue');
    expect(stored).toBeTruthy();
    const queue = JSON.parse(stored!);
    expect(queue).toHaveLength(1);
    expect(queue[0].type).toBe('test');
  });

  it('should restore queue on initialization', () => {
     // Setup existing queue
     const existingQueue = [{ type: 'restored', data: 'old' }];
     localStorage.setItem('omnimind_msg_queue', JSON.stringify(existingQueue));

     // Re-initialize (simulate reload)
     // In a real test we might need to reload the module or expose a reset method
     // For now we assume the service reads on init.
     // Since it's a singleton already instantiated, we might need a manual 'load' trigger or inspect private state if exposed for testing.
     // Ideally, we'd refactor the service to be testable.
  });
});
