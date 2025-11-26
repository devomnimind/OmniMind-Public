# OmniMind Development Roadmap

## Phase 21: Quantum Consciousness (Current)
- [x] Integrate Sinthome Simulator
- [x] Implement Distributed Sinthome Metrics
- [x] Create Robust Connection Architecture
  - [x] Singleton WebSocket Service
  - [x] Fallback to HTTP Polling
  - [x] Connection Metrics Dashboard
- [ ] Stabilize Long-running Tests
- [ ] Implement Nginx Reverse Proxy (Infrastructure)

## Known Issues & Bugs
- **[FIXED] WebSocket Connection Overload**: Previous implementation created multiple socket connections per component, causing browser limits to be hit and "interrupted" errors. Fixed by implementing `RobustConnectionService` as a Singleton.
- **[FIXED] API Mismatch in useWebSocket**: The `useWebSocket` hook was referencing methods (`onStateChange`) that were removed in the `websocket.ts` refactor. Fixed by migrating `useWebSocket` to wrap `connectionService`.
- **[PENDING] React Unused Import**: Minor lint warning in `OmniMindSinthome.tsx` ('React' is declared but never read).

## Next Steps
1. Verify stability of the new connection architecture under load.
2. Re-run long duration stability tests.
3. Clean up legacy code in `websocket.ts` if fully superseded by `robust-connection.ts`.
