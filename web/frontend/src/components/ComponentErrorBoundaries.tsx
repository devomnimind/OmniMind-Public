/**
 * Component-Specific Error Boundaries for OmniMind
 * 
 * Provides granular error handling for each major component with:
 * - Component-specific fallback UIs
 * - Error recovery strategies
 * - Telemetry integration
 * - User-friendly error messages
 */

import { ReactNode } from 'react';
import { AdvancedErrorBoundary, ErrorReport } from './AdvancedErrorBoundary';

interface ComponentErrorBoundaryProps {
  children: ReactNode;
}

/**
 * Error Boundary for Dashboard Component
 */
export function DashboardErrorBoundary({ children }: ComponentErrorBoundaryProps) {
  const handleError = (error: ErrorReport) => {
    console.error('[Dashboard Error]:', error);
    // Could integrate with error tracking service here
  };

  const fallback = (error: ErrorReport, retry: () => void) => (
    <div className="min-h-screen bg-dark-300 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-gray-800 rounded-lg p-8 border-2 border-red-500">
        <div className="flex items-center gap-3 mb-4">
          <svg className="w-12 h-12 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <h1 className="text-2xl font-bold text-white">Dashboard Error</h1>
            <p className="text-gray-400">Something went wrong loading the dashboard</p>
          </div>
        </div>

        <div className="bg-gray-900/50 rounded p-4 mb-4">
          <p className="text-white font-mono text-sm">{error.userMessage}</p>
          {error.error && (
            <details className="mt-2">
              <summary className="text-gray-400 text-xs cursor-pointer hover:text-gray-300">
                Technical Details
              </summary>
              <pre className="mt-2 text-xs text-red-300 overflow-auto">
                {error.error.message}
              </pre>
            </details>
          )}
        </div>

        <div className="flex gap-3">
          <button
            onClick={retry}
            className="flex-1 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-semibold transition-all duration-200 hover:shadow-cyan-glow"
          >
            Retry
          </button>
          <button
            onClick={() => window.location.reload()}
            className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded font-semibold transition-all duration-200"
          >
            Reload Page
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <AdvancedErrorBoundary
      name="Dashboard"
      fallback={fallback}
      onError={handleError}
      maxRetries={3}
      enableAutoRecovery={true}
    >
      {children}
    </AdvancedErrorBoundary>
  );
}

/**
 * Error Boundary for Task Components
 */
export function TaskErrorBoundary({ children }: ComponentErrorBoundaryProps) {
  const fallback = (error: ErrorReport, retry: () => void) => (
    <div className="bg-gray-800 rounded-lg p-6 border-2 border-yellow-500">
      <div className="flex items-center gap-3 mb-3">
        <svg className="w-8 h-8 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <h3 className="text-lg font-bold text-white">Task Component Error</h3>
          <p className="text-sm text-gray-400">{error.userMessage}</p>
        </div>
      </div>
      <button
        onClick={retry}
        className="px-4 py-2 bg-yellow-600 hover:bg-yellow-500 text-white rounded text-sm font-medium transition-all duration-200"
      >
        Retry
      </button>
    </div>
  );

  return (
    <AdvancedErrorBoundary
      name="Tasks"
      fallback={fallback}
      maxRetries={2}
      enableAutoRecovery={true}
    >
      {children}
    </AdvancedErrorBoundary>
  );
}

/**
 * Error Boundary for Agent Status Components
 */
export function AgentErrorBoundary({ children }: ComponentErrorBoundaryProps) {
  const fallback = (_error: ErrorReport, retry: () => void) => (
    <div className="bg-gray-800 rounded-lg p-6 border-2 border-orange-500">
      <div className="flex items-center gap-3 mb-3">
        <svg className="w-8 h-8 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <div>
          <h3 className="text-lg font-bold text-white">Agent Status Error</h3>
          <p className="text-sm text-gray-400">Unable to load agent status</p>
        </div>
      </div>
      <button
        onClick={retry}
        className="px-4 py-2 bg-orange-600 hover:bg-orange-500 text-white rounded text-sm font-medium transition-all duration-200"
      >
        Retry
      </button>
    </div>
  );

  return (
    <AdvancedErrorBoundary
      name="AgentStatus"
      fallback={fallback}
      maxRetries={3}
      retryDelay={1000}
      enableAutoRecovery={true}
    >
      {children}
    </AdvancedErrorBoundary>
  );
}

/**
 * Error Boundary for Metrics Components
 */
export function MetricsErrorBoundary({ children }: ComponentErrorBoundaryProps) {
  const fallback = (_error: ErrorReport, retry: () => void) => (
    <div className="bg-gray-800 rounded-lg p-6 border-2 border-purple-500">
      <div className="flex items-center gap-3 mb-3">
        <svg className="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <div>
          <h3 className="text-lg font-bold text-white">Metrics Error</h3>
          <p className="text-sm text-gray-400">Metrics data temporarily unavailable</p>
        </div>
      </div>
      <button
        onClick={retry}
        className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded text-sm font-medium transition-all duration-200"
      >
        Retry
      </button>
    </div>
  );

  return (
    <AdvancedErrorBoundary
      name="Metrics"
      fallback={fallback}
      maxRetries={3}
      enableAutoRecovery={true}
      gracefulDegradation={true}
    >
      {children}
    </AdvancedErrorBoundary>
  );
}

/**
 * Error Boundary for Health Dashboard
 */
export function HealthErrorBoundary({ children }: ComponentErrorBoundaryProps) {
  const fallback = (_error: ErrorReport, retry: () => void) => (
    <div className="bg-gray-800 rounded-lg p-6 border-2 border-red-500">
      <div className="flex items-center gap-3 mb-3">
        <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
        <div>
          <h3 className="text-lg font-bold text-white">Health Check Error</h3>
          <p className="text-sm text-gray-400">Unable to load health status</p>
        </div>
      </div>
      <button
        onClick={retry}
        className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded text-sm font-medium transition-all duration-200"
      >
        Retry
      </button>
    </div>
  );

  return (
    <AdvancedErrorBoundary
      name="Health"
      fallback={fallback}
      maxRetries={2}
      retryDelay={2000}
      enableAutoRecovery={false}
    >
      {children}
    </AdvancedErrorBoundary>
  );
}

/**
 * Error Boundary for WebSocket Components
 */
export function WebSocketErrorBoundary({ children }: ComponentErrorBoundaryProps) {
  const fallback = (_error: ErrorReport, retry: () => void) => (
    <div className="bg-gray-800 rounded-lg p-4 border border-blue-500">
      <div className="flex items-center gap-2 mb-2">
        <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
        </svg>
        <div>
          <h3 className="text-sm font-bold text-white">Connection Error</h3>
          <p className="text-xs text-gray-400">Real-time updates paused</p>
        </div>
      </div>
      <button
        onClick={retry}
        className="px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-medium transition-all duration-200"
      >
        Reconnect
      </button>
    </div>
  );

  return (
    <AdvancedErrorBoundary
      name="WebSocket"
      fallback={fallback}
      maxRetries={5}
      retryDelay={3000}
      enableAutoRecovery={true}
      gracefulDegradation={true}
    >
      {children}
    </AdvancedErrorBoundary>
  );
}
