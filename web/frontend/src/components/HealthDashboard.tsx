/**
 * Health Dashboard Widget for OmniMind
 * 
 * Displays real-time health status for all system dependencies with:
 * - Visual status indicators (healthy/degraded/unhealthy)
 * - Response time metrics
 * - Health trends and predictions
 * - Remediation suggestions
 * - Auto-refresh
 */

import { useEffect, useState } from 'react';
import { apiService } from '../services/api';

interface HealthCheck {
  name: string;
  dependency_type: string;
  status: 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
  response_time_ms: number;
  details: Record<string, any>;
  error?: string;
  timestamp: number;
  threshold_breached: boolean;
  remediation_suggestion?: string;
}

interface OverallHealth {
  overall_status: string;
  checks: Record<string, HealthCheck>;
  timestamp: number;
  total_checks: number;
  healthy_count: number;
  degraded_count: number;
  unhealthy_count: number;
}

interface HealthTrend {
  check_name: string;
  trend: string;
  prediction: string;
  health_score: number;
  recent_statuses: Record<string, number>;
  avg_response_time_ms: number;
}

const STATUS_COLORS = {
  healthy: 'bg-green-900/30 border-green-500 text-green-400',
  degraded: 'bg-yellow-900/30 border-yellow-500 text-yellow-400',
  unhealthy: 'bg-red-900/30 border-red-500 text-red-400',
  unknown: 'bg-gray-900/30 border-gray-500 text-gray-400',
};

const STATUS_ICONS = {
  healthy: '✓',
  degraded: '⚠',
  unhealthy: '✗',
  unknown: '?',
};

const DEPENDENCY_ICONS: Record<string, string> = {
  database: '🗄️',
  redis: '⚡',
  gpu: '🎮',
  filesystem: '💾',
  memory: '🧠',
  cpu: '⚙️',
  network: '🌐',
  external_api: '🔌',
};

export function HealthDashboard() {
  const [health, setHealth] = useState<OverallHealth | null>(null);
  const [selectedCheck, setSelectedCheck] = useState<string | null>(null);
  const [trend, setTrend] = useState<HealthTrend | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedCheck) {
      fetchTrend(selectedCheck);
    }
  }, [selectedCheck]);

  const fetchHealth = async () => {
    try {
      const response = await fetch('/api/v1/health/', {
        headers: apiService.getHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.statusText}`);
      }
      
      const data = await response.json();
      setHealth(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch health data');
      console.error('Health fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchTrend = async (checkName: string) => {
    try {
      const response = await fetch(`/api/v1/health/${checkName}/trend`, {
        headers: apiService.getHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`Trend fetch failed: ${response.statusText}`);
      }
      
      const data = await response.json();
      setTrend(data);
    } catch (err) {
      console.error('Trend fetch error:', err);
      setTrend(null);
    }
  };

  const getStatusGlow = (status: string) => {
    const glows = {
      healthy: 'shadow-green-glow',
      degraded: 'shadow-yellow-glow',
      unhealthy: 'shadow-red-glow',
      unknown: 'shadow-gray-glow',
    };
    return glows[status as keyof typeof glows] || '';
  };

  if (loading && !health) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 animate-pulse">
        <div className="h-8 bg-gray-700 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="h-16 bg-gray-700 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error && !health) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-4">System Health</h2>
        <div className="bg-red-900/30 border border-red-500/50 rounded p-4 text-red-300">
          <p className="flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </p>
        </div>
      </div>
    );
  }

  if (!health) return null;

  const overallStatusColor = STATUS_COLORS[health.overall_status as keyof typeof STATUS_COLORS] || STATUS_COLORS.unknown;

  return (
    <div className="bg-gray-800 rounded-lg p-6 transition-all duration-300 hover:shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">System Health</h2>
        <div className={`px-4 py-2 rounded-full border-2 ${overallStatusColor} font-semibold text-sm ${getStatusGlow(health.overall_status)}`}>
          {STATUS_ICONS[health.overall_status as keyof typeof STATUS_ICONS]} {health.overall_status.toUpperCase()}
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-3 text-center">
          <div className="text-3xl font-bold text-green-400">{health.healthy_count}</div>
          <div className="text-sm text-green-300">Healthy</div>
        </div>
        <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-3 text-center">
          <div className="text-3xl font-bold text-yellow-400">{health.degraded_count}</div>
          <div className="text-sm text-yellow-300">Degraded</div>
        </div>
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3 text-center">
          <div className="text-3xl font-bold text-red-400">{health.unhealthy_count}</div>
          <div className="text-sm text-red-300">Unhealthy</div>
        </div>
      </div>

      {/* Individual Health Checks */}
      <div className="space-y-3">
        {Object.entries(health.checks).map(([name, check]) => {
          const isSelected = selectedCheck === name;
          const statusColor = STATUS_COLORS[check.status];
          const icon = DEPENDENCY_ICONS[check.dependency_type] || '🔧';

          return (
            <div
              key={name}
              className={`
                bg-gray-700/50 rounded-lg p-4 border cursor-pointer
                transition-all duration-300
                ${statusColor}
                ${isSelected ? 'ring-2 ring-cyan-400 shadow-lg' : 'hover:bg-gray-700/70'}
              `}
              onClick={() => setSelectedCheck(isSelected ? null : name)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  <span className="text-2xl">{icon}</span>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-white capitalize">{name}</h3>
                      <span className="text-xs px-2 py-0.5 bg-gray-600 rounded-full text-gray-300">
                        {check.dependency_type}
                      </span>
                    </div>
                    <div className="text-sm text-gray-400 mt-0.5">
                      Response: {check.response_time_ms.toFixed(2)}ms
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{STATUS_ICONS[check.status]}</span>
                  {check.threshold_breached && (
                    <svg className="w-5 h-5 text-yellow-400 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  )}
                </div>
              </div>

              {/* Error Message */}
              {check.error && (
                <div className="mt-2 bg-red-900/40 border border-red-500/50 rounded p-2 text-xs text-red-300">
                  Error: {check.error}
                </div>
              )}

              {/* Remediation Suggestion */}
              {check.remediation_suggestion && (
                <div className="mt-2 bg-blue-900/30 border border-blue-500/50 rounded p-2 text-xs text-blue-300">
                  💡 {check.remediation_suggestion}
                </div>
              )}

              {/* Expanded Details */}
              {isSelected && (
                <div className="mt-4 pt-4 border-t border-gray-600 space-y-2 animate-fade-in">
                  <h4 className="text-sm font-semibold text-white">Details:</h4>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    {Object.entries(check.details).map(([key, value]) => (
                      <div key={key} className="bg-gray-800/50 rounded p-2">
                        <div className="text-gray-400">{key.replace(/_/g, ' ')}</div>
                        <div className="text-white font-medium">
                          {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Trend Information */}
                  {trend && trend.check_name === name && (
                    <div className="mt-3 bg-gray-800/50 rounded p-3">
                      <h4 className="text-sm font-semibold text-white mb-2">Health Trend:</h4>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>
                          <span className="text-gray-400">Trend:</span>
                          <span className={`ml-2 font-semibold ${
                            trend.trend === 'stable' ? 'text-green-400' :
                            trend.trend === 'degrading' ? 'text-yellow-400' :
                            trend.trend === 'critical' ? 'text-red-400' : 'text-gray-400'
                          }`}>
                            {trend.trend}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-400">Prediction:</span>
                          <span className="ml-2 text-white font-medium">{trend.prediction.replace(/_/g, ' ')}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Health Score:</span>
                          <span className="ml-2 text-white font-medium">{trend.health_score.toFixed(1)}%</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Avg Response:</span>
                          <span className="ml-2 text-white font-medium">{trend.avg_response_time_ms.toFixed(2)}ms</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Timestamp */}
      <div className="mt-4 text-center text-xs text-gray-500">
        Last updated: {new Date(health.timestamp * 1000).toLocaleTimeString()}
      </div>
    </div>
  );
}
