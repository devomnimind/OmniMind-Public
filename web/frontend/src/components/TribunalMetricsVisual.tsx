import { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { useAuthStore } from '../store/authStore';

interface MetricsData {
  raw_metrics: {
    attacks_count: number;
    attacks_successful: number;
    attacks_failed: number;
    duration_hours: number;
    consciousness_compatible: boolean;
    status: string;
    last_attack_type: string;
    error_count: number;
    success_rate: number;
  };
  interpretations: {
    threat_level: string;
    performance_status: string;
    recommendations: string[];
    visual_indicators: {
      threat_color: string;
      threat_icon: string;
    };
  };
  visualization: {
    charts: any;
    status_indicators: any;
    summary_metrics: any;
  };
  timestamp: string;
}

export function TribunalMetricsVisual() {
  const [data, setData] = useState<MetricsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // CORREÇÃO CRÍTICA (2025-12-10): Verificar autenticação antes de fazer fetch
    const isAuthenticated = useAuthStore.getState().isAuthenticated;
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    const fetchMetrics = async () => {
      // Verificar autenticação antes de cada fetch
      if (!useAuthStore.getState().isAuthenticated) {
        return;
      }

      try {
        const result = await apiService.getTribunalMetrics();
        setData(result);
        setError(null);
      } catch (err) {
        // CORREÇÃO (2025-12-10): Não mostrar erro se não há autenticação
        const errorMessage = err instanceof Error ? err.message : 'Failed to load Tribunal metrics';
        if (errorMessage !== 'Not authenticated' && !errorMessage.includes('Failed to fetch')) {
          setError('Failed to load Tribunal metrics');
          console.error(err);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="glass-card p-6 animate-pulse">Loading metrics...</div>;
  if (error) return <div className="glass-card p-6 text-red-500">{error}</div>;
  if (!data) return null;

  // CORREÇÃO (2025-12-10): Tratar dados ausentes ou incompletos
  const { raw_metrics, interpretations, visualization } = data;
  if (!visualization || !visualization.status_indicators) {
    return (
      <div className="glass-card p-6">
        <div className="text-yellow-500">⚠️ Tribunal data incomplete. Waiting for report...</div>
      </div>
    );
  }

  const { summary_metrics, status_indicators } = visualization;
  const threatIndicator = status_indicators.threat_level || { value: "unknown", color: "#888", icon: "❓" };
  const perfIndicator = status_indicators.performance || { value: "unknown", color: "#888", icon: "❓" };
  const consIndicator = status_indicators.consciousness_compatibility || { 
    value: "Unknown", 
    color: "#888", 
    icon: "❓" 
  };

  return (
    <div className="space-y-4">
      {/* Main Metrics Card */}
      <div className="glass-card p-6 relative overflow-hidden group hover:shadow-neon-blue transition-all duration-300">
        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
          <span className="text-6xl">📊</span>
        </div>

        <h2 className="text-xl font-bold text-gradient-neon mb-6 flex items-center gap-2">
          <span>📊</span> Tribunal Metrics & Analysis
        </h2>

        {/* Status Indicators Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {/* Threat Level */}
          <div className="bg-dark-200/50 p-4 rounded-lg border border-gray-700/50">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl">{threatIndicator.icon}</span>
              <div>
                <div className="text-xs text-gray-400">Threat Level</div>
                <div
                  className="font-mono font-bold text-sm"
                  style={{ color: threatIndicator.color }}
                >
                  {threatIndicator.value.toUpperCase()}
                </div>
              </div>
            </div>
            <div
              className="h-1 w-full rounded-full"
              style={{ backgroundColor: threatIndicator.color }}
            ></div>
          </div>

          {/* Performance Status */}
          <div className="bg-dark-200/50 p-4 rounded-lg border border-gray-700/50">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl">{perfIndicator.icon}</span>
              <div>
                <div className="text-xs text-gray-400">Performance</div>
                <div
                  className="font-mono font-bold text-sm"
                  style={{ color: perfIndicator.color }}
                >
                  {perfIndicator.value.toUpperCase()}
                </div>
              </div>
            </div>
            <div className="h-1 w-full rounded-full bg-gray-700/50">
              <div
                className="h-full rounded-full"
                style={{
                  backgroundColor: perfIndicator.color,
                  width: `${summary_metrics.success_rate_percent}%`,
                }}
              ></div>
            </div>
          </div>

          {/* Consciousness Compatibility */}
          <div className="bg-dark-200/50 p-4 rounded-lg border border-gray-700/50">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl">{consIndicator.icon}</span>
              <div>
                <div className="text-xs text-gray-400">Consciousness</div>
                <div
                  className="font-mono font-bold text-sm"
                  style={{ color: consIndicator.color }}
                >
                  {consIndicator.value}
                </div>
              </div>
            </div>
            <div
              className="h-1 w-full rounded-full"
              style={{ backgroundColor: consIndicator.color }}
            ></div>
          </div>
        </div>

        {/* Summary Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          <div className="bg-dark-300/50 p-3 rounded-lg">
            <div className="text-xs text-gray-400 mb-1">Total Attacks</div>
            <div className="text-2xl font-bold text-neon-blue">
              {summary_metrics.total_attacks}
            </div>
          </div>
          <div className="bg-dark-300/50 p-3 rounded-lg">
            <div className="text-xs text-gray-400 mb-1">Success Rate</div>
            <div className="text-2xl font-bold text-neon-green">
              {summary_metrics.success_rate_percent}%
            </div>
          </div>
          <div className="bg-dark-300/50 p-3 rounded-lg">
            <div className="text-xs text-gray-400 mb-1">Duration</div>
            <div className="text-2xl font-bold text-neon-purple">
              {summary_metrics.duration_hours}h
            </div>
          </div>
          <div className="bg-dark-300/50 p-3 rounded-lg">
            <div className="text-xs text-gray-400 mb-1">Errors</div>
            <div className="text-2xl font-bold text-neon-red">
              {summary_metrics.error_count}
            </div>
          </div>
        </div>

        {/* Attack Distribution */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-300 mb-3">Attack Distribution</h3>
          <div className="flex items-center gap-4">
            <div className="flex-1 space-y-2">
              <div>
                <div className="flex justify-between text-xs text-gray-400 mb-1">
                  <span>Successful</span>
                  <span>{raw_metrics.attacks_successful}</span>
                </div>
                <div className="h-2 bg-gray-700/50 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-neon-green transition-all duration-500"
                    style={{
                      width: `${
                        raw_metrics.attacks_count > 0
                          ? (raw_metrics.attacks_successful / raw_metrics.attacks_count) * 100
                          : 0
                      }%`,
                    }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs text-gray-400 mb-1">
                  <span>Failed</span>
                  <span>{raw_metrics.attacks_failed}</span>
                </div>
                <div className="h-2 bg-gray-700/50 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-neon-red transition-all duration-500"
                    style={{
                      width: `${
                        raw_metrics.attacks_count > 0
                          ? (raw_metrics.attacks_failed / raw_metrics.attacks_count) * 100
                          : 0
                      }%`,
                    }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Raw Metrics Details */}
        <div className="mb-6 bg-dark-300/30 p-4 rounded-lg border border-gray-700/30">
          <h3 className="text-sm font-semibold text-gray-300 mb-3">Raw Metrics</h3>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex justify-between">
              <span className="text-gray-500">Status:</span>
              <span className="text-gray-300 font-mono">{raw_metrics.status}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Last Attack:</span>
              <span className="text-gray-300 font-mono">{raw_metrics.last_attack_type}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Total:</span>
              <span className="text-gray-300 font-mono">{raw_metrics.attacks_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Success Rate:</span>
              <span className="text-gray-300 font-mono">{(raw_metrics.success_rate * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        {interpretations.recommendations.length > 0 && (
          <div className="bg-dark-300/30 p-4 rounded-lg border border-yellow-500/30">
            <h3 className="text-sm font-semibold text-yellow-300 mb-2">Recommendations</h3>
            <ul className="space-y-1">
              {interpretations.recommendations.map((rec, idx) => (
                <li key={idx} className="text-xs text-gray-300 flex items-start gap-2">
                  <span className="text-yellow-400 mt-0.5">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
