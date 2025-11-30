/**
 * Advanced Error Boundary System for OmniMind
 * 
 * Provides granular error handling with:
 * - Component-level error boundaries
 * - Graceful degradation
 * - Auto-recovery mechanisms
 * - Intelligent error reporting
 * - User-friendly error messages
 */

import { Component, ReactNode, ErrorInfo } from 'react';

export enum ErrorSeverity {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

export enum ErrorCategory {
  NETWORK = 'network',
  API = 'api',
  RENDER = 'render',
  STATE = 'state',
  VALIDATION = 'validation',
  PERMISSION = 'permission',
  UNKNOWN = 'unknown',
}

export interface ErrorReport {
  id: string;
  timestamp: number;
  severity: ErrorSeverity;
  category: ErrorCategory;
  message: string;
  userMessage: string;
  component: string;
  error: Error;
  errorInfo?: ErrorInfo;
  context?: Record<string, any>;
  canRecover: boolean;
  retryCount: number;
}

export interface ErrorBoundaryConfig {
  name: string;
  fallback?: ReactNode | ((error: ErrorReport, retry: () => void) => ReactNode);
  onError?: (error: ErrorReport) => void;
  maxRetries?: number;
  retryDelay?: number;
  enableAutoRecovery?: boolean;
  gracefulDegradation?: boolean;
  reportErrors?: boolean;
}

interface AdvancedErrorBoundaryProps extends ErrorBoundaryConfig {
  children: ReactNode;
}

interface AdvancedErrorBoundaryState {
  error: ErrorReport | null;
  retryCount: number;
  isRecovering: boolean;
}

export class AdvancedErrorBoundary extends Component<
  AdvancedErrorBoundaryProps,
  AdvancedErrorBoundaryState
> {
  private retryTimeout?: NodeJS.Timeout;

  constructor(props: AdvancedErrorBoundaryProps) {
    super(props);
    this.state = {
      error: null,
      retryCount: 0,
      isRecovering: false,
    };
  }

  static getDerivedStateFromError(_error: Error): Partial<AdvancedErrorBoundaryState> {
    // Convert error to ErrorReport in componentDidCatch
    return { error: null };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const errorReport = this.createErrorReport(error, errorInfo);

    this.setState({ error: errorReport });

    // Call custom error handler
    if (this.props.onError) {
      this.props.onError(errorReport);
    }

    // Report to error tracking service
    if (this.props.reportErrors !== false) {
      this.reportError(errorReport);
    }

    // Attempt auto-recovery if enabled
    if (
      this.props.enableAutoRecovery &&
      errorReport.canRecover &&
      this.state.retryCount < (this.props.maxRetries || 3)
    ) {
      this.scheduleRecovery();
    }
  }

  componentWillUnmount() {
    if (this.retryTimeout) {
      clearTimeout(this.retryTimeout);
    }
  }

  createErrorReport(error: Error, errorInfo?: ErrorInfo): ErrorReport {
    const category = this.categorizeError(error);
    const severity = this.determineErrorSeverity(error, category);
    const userMessage = this.getUserFriendlyMessage(error, category);
    const canRecover = this.canRecoverFromError(error, category);

    return {
      id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      severity,
      category,
      message: error.message,
      userMessage,
      component: this.props.name,
      error,
      errorInfo,
      context: this.getErrorContext(),
      canRecover,
      retryCount: this.state.retryCount,
    };
  }

  categorizeError(error: Error): ErrorCategory {
    const message = error.message.toLowerCase();

    if (message.includes('network') || message.includes('fetch')) {
      return ErrorCategory.NETWORK;
    }
    if (message.includes('api') || message.includes('http')) {
      return ErrorCategory.API;
    }
    if (message.includes('render') || error.name === 'TypeError') {
      return ErrorCategory.RENDER;
    }
    if (message.includes('state') || message.includes('undefined')) {
      return ErrorCategory.STATE;
    }
    if (message.includes('validation') || message.includes('invalid')) {
      return ErrorCategory.VALIDATION;
    }
    if (message.includes('permission') || message.includes('forbidden')) {
      return ErrorCategory.PERMISSION;
    }

    return ErrorCategory.UNKNOWN;
  }

  determineErrorSeverity(_error: Error, category: ErrorCategory): ErrorSeverity {
    // Critical errors that require immediate attention
    if (category === ErrorCategory.PERMISSION) {
      return ErrorSeverity.CRITICAL;
    }

    // High severity for network/API failures
    if (category === ErrorCategory.NETWORK || category === ErrorCategory.API) {
      return ErrorSeverity.HIGH;
    }

    // Medium severity for validation errors
    if (category === ErrorCategory.VALIDATION) {
      return ErrorSeverity.MEDIUM;
    }

    // Low severity for render errors (usually recoverable)
    if (category === ErrorCategory.RENDER || category === ErrorCategory.STATE) {
      return ErrorSeverity.LOW;
    }

    return ErrorSeverity.MEDIUM;
  }

  getUserFriendlyMessage(_error: Error, category: ErrorCategory): string {
    const messages: Record<ErrorCategory, string> = {
      [ErrorCategory.NETWORK]: 'Unable to connect to the server. Please check your internet connection and try again.',
      [ErrorCategory.API]: 'The server encountered an error. Please try again in a moment.',
      [ErrorCategory.RENDER]: 'A display error occurred. The page will refresh automatically.',
      [ErrorCategory.STATE]: 'Something went wrong with the application state. Refreshing...',
      [ErrorCategory.VALIDATION]: 'Invalid data detected. Please check your input and try again.',
      [ErrorCategory.PERMISSION]: 'You don\'t have permission to access this resource. Please contact support.',
      [ErrorCategory.UNKNOWN]: 'An unexpected error occurred. Our team has been notified.',
    };

    return messages[category] || messages[ErrorCategory.UNKNOWN];
  }

  canRecoverFromError(_error: Error, category: ErrorCategory): boolean {
    // Network and API errors are usually recoverable with retry
    if (category === ErrorCategory.NETWORK || category === ErrorCategory.API) {
      return true;
    }

    // State errors might be recoverable
    if (category === ErrorCategory.STATE) {
      return true;
    }

    // Permission and unknown errors are not automatically recoverable
    return false;
  }

  getErrorContext(): Record<string, any> {
    return {
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString(),
      component: this.props.name,
    };
  }

  reportError(error: ErrorReport) {
    // Send error to monitoring service (e.g., Sentry, LogRocket)
    console.error('[ErrorBoundary]', {
      component: error.component,
      category: error.category,
      severity: error.severity,
      message: error.message,
      context: error.context,
    });

    // In production, you would send this to an error tracking service
    if (process.env.NODE_ENV === 'production') {
      // Example: Sentry.captureException(error.error, { extra: error });
    }
  }

  scheduleRecovery = () => {
    const delay = this.props.retryDelay || 2000;
    const backoffDelay = delay * Math.pow(2, this.state.retryCount);

    this.setState({ isRecovering: true });

    this.retryTimeout = setTimeout(() => {
      this.handleRetry();
    }, backoffDelay);
  };

  handleRetry = () => {
    this.setState((prevState) => ({
      error: null,
      retryCount: prevState.retryCount + 1,
      isRecovering: false,
    }));
  };

  handleReset = () => {
    this.setState({
      error: null,
      retryCount: 0,
      isRecovering: false,
    });
  };

  renderFallback() {
    const { error } = this.state;
    if (!error) return null;

    // Custom fallback component
    if (this.props.fallback) {
      if (typeof this.props.fallback === 'function') {
        return this.props.fallback(error, this.handleRetry);
      }
      return this.props.fallback;
    }

    // Graceful degradation - show minimal UI
    if (this.props.gracefulDegradation) {
      return (
        <div className="p-4 bg-yellow-900/20 border border-yellow-500/50 rounded-lg">
          <div className="flex items-start gap-3">
            <span className="text-yellow-500 text-xl">⚠️</span>
            <div className="flex-1">
              <h3 className="text-yellow-200 font-semibold mb-1">
                {this.props.name} Unavailable
              </h3>
              <p className="text-yellow-300/70 text-sm">{error.userMessage}</p>
              {error.canRecover && (
                <button
                  onClick={this.handleRetry}
                  className="mt-2 text-xs text-yellow-400 hover:text-yellow-300 underline"
                  disabled={this.state.isRecovering}
                >
                  {this.state.isRecovering ? 'Retrying...' : 'Try Again'}
                </button>
              )}
            </div>
          </div>
        </div>
      );
    }

    // Default error UI
    return (
      <div className="p-6 bg-red-900/20 border border-red-500/50 rounded-lg">
        <div className="text-center">
          <div className="text-4xl mb-4">
            {error.severity === ErrorSeverity.CRITICAL ? '🚨' : '⚠️'}
          </div>
          <h2 className="text-xl font-bold text-red-200 mb-2">
            {error.severity === ErrorSeverity.CRITICAL
              ? 'Critical Error'
              : 'Something Went Wrong'}
          </h2>
          <p className="text-red-300/80 mb-4">{error.userMessage}</p>

          <div className="flex gap-3 justify-center">
            {error.canRecover && (
              <button
                onClick={this.handleRetry}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
                disabled={this.state.isRecovering}
              >
                {this.state.isRecovering ? (
                  <span className="flex items-center gap-2">
                    <span className="spinner w-4 h-4" />
                    Retrying...
                  </span>
                ) : (
                  'Retry'
                )}
              </button>
            )}
            <button
              onClick={this.handleReset}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
            >
              Reset
            </button>
          </div>

          {process.env.NODE_ENV === 'development' && (
            <details className="mt-4 text-left">
              <summary className="text-xs text-red-400 cursor-pointer hover:text-red-300">
                Error Details (Development Only)
              </summary>
              <pre className="mt-2 p-3 bg-black/30 rounded text-xs text-red-300 overflow-x-auto">
                {JSON.stringify(
                  {
                    message: error.message,
                    category: error.category,
                    severity: error.severity,
                    component: error.component,
                    retryCount: error.retryCount,
                  },
                  null,
                  2
                )}
              </pre>
            </details>
          )}
        </div>
      </div>
    );
  }

  render() {
    if (this.state.error) {
      return this.renderFallback();
    }

    return this.props.children;
  }
}

/**
 * Specialized Error Boundary for API calls
 */
export class APIErrorBoundary extends AdvancedErrorBoundary {
  constructor(props: AdvancedErrorBoundaryProps) {
    super({
      ...props,
      name: props.name || 'API',
      enableAutoRecovery: props.enableAutoRecovery !== false,
      maxRetries: props.maxRetries || 3,
      retryDelay: props.retryDelay || 1000,
      gracefulDegradation: props.gracefulDegradation !== false,
    });
  }
}

/**
 * Specialized Error Boundary for Network operations
 */
export class NetworkErrorBoundary extends AdvancedErrorBoundary {
  constructor(props: AdvancedErrorBoundaryProps) {
    super({
      ...props,
      name: props.name || 'Network',
      enableAutoRecovery: true,
      maxRetries: props.maxRetries || 5,
      retryDelay: props.retryDelay || 2000,
      gracefulDegradation: true,
    });
  }
}

/**
 * Utility to create error boundaries easily
 */
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  config: ErrorBoundaryConfig
): React.FC<P> {
  return (props: P) => (
    <AdvancedErrorBoundary {...config}>
      <Component {...props} />
    </AdvancedErrorBoundary>
  );
}
