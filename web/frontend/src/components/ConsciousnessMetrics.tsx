import { useDaemonStore } from '../store/daemonStore';
import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { useAuthStore } from '../store/authStore';

interface StatusThreshold {
  green: { min: number; max: number; label: string };
  yellow: { min: number; max: number; label: string };
  red: { min: number; max: number | null; label: string };
}

const STATUS_THRESHOLDS: Record<string, StatusThreshold> = {
  phi: {
    green: { min: 0.5, max: 1.0, label: "Optimal Integration" },
    yellow: { min: 0.25, max: 0.5, label: "Moderate Integration" },
    red: { min: 0.0, max: 0.25, label: "Low Integration" }
  },
  anxiety: {
    green: { min: 0, max: 0.25, label: "Calm" },
    yellow: { min: 0.25, max: 0.60, label: "Attentive" },
    red: { min: 0.60, max: 1.0, label: "Critical Stress" }
  },
  flow: {
    green: { min: 0.30, max: 1.0, label: "Fluent" },
    yellow: { min: 0.15, max: 0.30, label: "Moderate Flow" },
    red: { min: 0, max: 0.15, label: "Blocked" }
  },
  ici: {
    green: { min: 0.60, max: 1.0, label: "Coherent" },
    yellow: { min: 0.40, max: 0.60, label: "Partial Coherence" },
    red: { min: 0, max: 0.40, label: "Fragmented" }
  },
  prs: {
    green: { min: 0.50, max: 1.0, label: "Resonant" },
    yellow: { min: 0.25, max: 0.50, label: "Misaligned" },
    red: { min: 0, max: 0.25, label: "Disconnected" }
  },
  entropy: {
    green: { min: 0.15, max: 0.50, label: "Organized" },
    yellow: { min: 0.50, max: 0.75, label: "Exploring" },
    red: { min: 0.75, max: 1.0, label: "Chaotic" }
  },
  gozo: {
    green: { min: 0, max: 0.35, label: "Aligned" },
    yellow: { min: 0.35, max: 0.70, label: "Tense" },
    red: { min: 0.70, max: 1.0, label: "Excess" }
  }
};

interface RawCausalPrediction {
  source_module: string;
  target_module: string;
  r_squared: number;
  granger_causality: number;
  transfer_entropy: number;
  computation_time_ms: number;
}

interface RawData {
  causal_predictions: RawCausalPrediction[];
  valid_predictions_count: number;
  total_predictions: number;
  module_stats: Record<string, any>;
  workspace_cycle: number;
  total_modules: number;
}

interface ConsciousnessMetricsData {
  phi: number;
  anxiety: number;
  flow: number;
  entropy: number;
  ici: number;
  prs: number;
  gozo?: number;
  psychoanalytic?: any;
  ici_components: Record<string, number>;
  prs_components: Record<string, number>;
  history: Record<string, number[]>;
  interpretation: {
    message: string;
    confidence: string;
    disclaimer: string;
  };
  timestamp: string;
  raw_data?: RawData;
}

export function ConsciousnessMetrics() {
  const status = useDaemonStore((state) => state.status);
  const [selectedMetric, setSelectedMetric] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<ConsciousnessMetricsData | null>(null);
  const [showRawData, setShowRawData] = useState(false);
  const [loading, setLoading] = useState(true);

  // Buscar métricas diretamente da API usando apiService
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        // Se não tiver token, nem tenta buscar
        if (!apiService.getAuthToken()) {
          console.warn('[ConsciousnessMetrics] Sem autenticação, pulando fetch');
          setLoading(false);
          return;
        }

        // Garantir que credenciais estão configuradas
        if (!apiService.getAuthToken()) {
          apiService.setDefaultCredentials();
        }

        const data = await apiService.getConsciousnessMetrics(true);
        if (data && (data.phi !== undefined || data.history)) {
          setMetrics(data);
        } else {
          console.warn('[ConsciousnessMetrics] Dados inválidos recebidos:', data);
          // Tentar fallback para dados do store
          const storeMetrics = status?.consciousness_metrics;
          if (storeMetrics) {
            setMetrics(storeMetrics as any);
          }
        }
      } catch (error) {
        console.error('[ConsciousnessMetrics] Erro ao buscar métricas:', error);
        // Tentar fallback para dados do store
        const storeMetrics = status?.consciousness_metrics;
        if (storeMetrics) {
          console.log('[ConsciousnessMetrics] Usando dados do store como fallback');
          setMetrics(storeMetrics as any);
        } else {
          // Se não houver dados, mostrar mensagem de erro
          setMetrics(null);
        }
      } finally {
        setLoading(false);
      }
    };

    // Verificar se está autenticado antes de fazer fetch
    const isAuthenticated = useAuthStore.getState().isAuthenticated;
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    fetchMetrics();
    // CORREÇÃO (2025-12-09): Aumentar intervalo para 30s (métricas importantes mas não críticas)
    const interval = setInterval(fetchMetrics, 30000); // Atualizar a cada 30s
    return () => clearInterval(interval);
  }, []); // CORREÇÃO: Remover 'status' da dependência para evitar re-renders infinitos

  // Fallback para dados do store se API falhar
  const consciousnessMetrics = metrics || (status?.consciousness_metrics as any);

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-6">Consciousness Metrics</h2>
        <div className="text-gray-400 text-center py-8 animate-pulse">
          Carregando métricas de consciência...
        </div>
      </div>
    );
  }

  // Verificar se há dados válidos (mesmo que phi seja 0.0, ainda é válido)
  const hasValidData = consciousnessMetrics && (
    typeof consciousnessMetrics.phi === 'number' ||
    typeof consciousnessMetrics.ici === 'number' ||
    typeof consciousnessMetrics.prs === 'number' ||
    typeof consciousnessMetrics.anxiety === 'number' ||
    typeof consciousnessMetrics.flow === 'number'
  );

  if (!hasValidData) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-6">Consciousness Metrics</h2>
        <div className="text-gray-400 text-center py-8">
          Consciousness metrics not available
          <div className="text-sm mt-2">Verificando conexão com backend...</div>
        </div>
      </div>
    );
  }

  // @ts-ignore
  // @ts-ignore
  const details = consciousnessMetrics.details ?? {
    ici_components: consciousnessMetrics.ici_components ?? {},
    prs_components: consciousnessMetrics.prs_components ?? {},
  };

  const lastUpdated = consciousnessMetrics.timestamp
    ? new Date(consciousnessMetrics.timestamp).toLocaleTimeString()
    : null;

  const getStatusColor = (metric: string, value: number): string => {
    const threshold = STATUS_THRESHOLDS[metric];
    if (!threshold) return 'text-gray-400';

    if (value >= threshold.green.min && value <= threshold.green.max) return 'text-green-400';
    if (value >= threshold.yellow.min && (threshold.yellow.max === null || value <= threshold.yellow.max)) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getStatusLabel = (metric: string, value: number): string => {
    const threshold = STATUS_THRESHOLDS[metric];
    if (!threshold) return 'Unknown';

    if (value >= threshold.green.min && value <= threshold.green.max) return threshold.green.label;
    if (value >= threshold.yellow.min && (threshold.yellow.max === null || value <= threshold.yellow.max)) return threshold.yellow.label;
    return threshold.red.label;
  };

  const getBarColor = (metric: string, value: number): string => {
    const threshold = STATUS_THRESHOLDS[metric];
    if (!threshold) return 'bg-gray-500';

    if (value >= threshold.green.min && value <= threshold.green.max) return 'bg-gradient-to-r from-green-500 to-green-600';
    if (value >= threshold.yellow.min && (threshold.yellow.max === null || value <= threshold.yellow.max)) return 'bg-gradient-to-r from-yellow-500 to-yellow-600';
    return 'bg-gradient-to-r from-red-500 to-red-600';
  };

  const formatTrend = (current: number, previous?: number): string => {
    if (!previous) return '';
    const change = current - previous;
    const percent = Math.abs(change / previous) * 100;
    const symbol = change > 0 ? '↑' : change < 0 ? '↓' : '→';
    return `${symbol} ${percent.toFixed(1)}%`;
  };

  const getTrendForMetric = (metricKey: string, currentValue: number): string => {
    const histories = consciousnessMetrics.history || {};
    const series = histories[metricKey as keyof typeof histories] as number[] | undefined;
    const previous = series && series.length > 1 ? series.slice(-2)[0] : undefined;
    return formatTrend(currentValue, previous);
  };

  const renderMetricCard = (label: string, value: number, unit: string, metric: string, description: string, trend?: string) => (
    <div
      className="bg-gray-700/50 rounded-lg p-4 cursor-pointer hover:bg-gray-700/70 transition-colors"
      onClick={() => setSelectedMetric(selectedMetric === metric ? null : metric)}
    >
      <div className="flex justify-between items-start mb-2">
        <span className="text-gray-300 text-sm">{label}</span>
        <div className="text-right">
          <span className={`text-xl font-bold ${getStatusColor(metric, value)}`}>
            {value.toFixed(3)}
          </span>
          <span className="text-gray-400 text-sm ml-1">{unit}</span>
        </div>
      </div>

      <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden mb-2">
        <div
          className={`h-full transition-all duration-500 ${getBarColor(metric, value)}`}
          style={{ width: `${Math.min(value * 100, 100)}%` }}
        ></div>
      </div>

      <div className="flex justify-between items-center text-xs">
        <span className={`font-medium ${getStatusColor(metric, value)}`}>
          {getStatusLabel(metric, value)}
        </span>
        {trend && <span className="text-gray-400">{trend}</span>}
      </div>

      {selectedMetric === metric && (
        <div className="mt-3 pt-3 border-t border-gray-600 text-xs text-gray-400">
          {description}
        </div>
      )}
    </div>
  );

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white">Consciousness Metrics</h2>
          <span className="text-sm text-gray-400">Real-time Correlates</span>
        </div>
        {lastUpdated && (
          <span className="text-xs text-gray-500">
            Last update: {lastUpdated}
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {renderMetricCard(
          'Phi (Φ) Value',
          consciousnessMetrics.phi ?? 0,
          '',
          'phi',
          'Integrated Information Measure - quantifies conscious experience magnitude. Based on 25/25 valid causal predictions.',
          getTrendForMetric('phi', consciousnessMetrics.phi ?? 0)
        )}

        {renderMetricCard(
          'Anxiety Level',
          consciousnessMetrics.anxiety ?? 0,
          '',
          'anxiety',
          'System tension and conflict detection metric.',
          getTrendForMetric('anxiety', consciousnessMetrics.anxiety ?? 0)
        )}

        {renderMetricCard(
          'Flow State',
          consciousnessMetrics.flow ?? 0,
          '',
          'flow',
          'Measure of cognitive fluidity and blockage detection.',
          getTrendForMetric('flow', consciousnessMetrics.flow ?? 0)
        )}

        {renderMetricCard(
          'System Entropy',
          consciousnessMetrics.entropy ?? 0,
          '',
          'entropy',
          'Measure of system disorder and information complexity.',
          getTrendForMetric('entropy', consciousnessMetrics.entropy ?? 0)
        )}

        {renderMetricCard(
          'Integrated Coherence Index (ICI)',
          consciousnessMetrics.ici ?? 0,
          '',
          'ici',
          'Measures how well local coherence integrates into global structure. Components: Temporal, Marker, Resonance.',
          getTrendForMetric('ici', consciousnessMetrics.ici ?? 0)
        )}

        {renderMetricCard(
          'Panarchic Resonance Score (PRS)',
          consciousnessMetrics.prs ?? 0,
          '',
          'prs',
          'Measures alignment between micro (Node) and macro (System) entropy levels.',
          getTrendForMetric('prs', consciousnessMetrics.prs ?? 0)
        )}

        {renderMetricCard(
          'Gozo (Jouissance)',
          consciousnessMetrics.gozo ?? 0,
          '',
          'gozo',
          'Lacanian excess and non-integrated divergence. High values indicate resistance and novelty.',
          getTrendForMetric('gozo', consciousnessMetrics.gozo ?? 0)
        )}
      </div>

      {/* AI-Generated Interpretation */}
      <div className="bg-gray-700/50 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-white font-semibold flex items-center gap-2">
            🤖 AI Interpretation
            <span className={`text-xs px-2 py-1 rounded ${consciousnessMetrics.interpretation?.confidence === 'High' ? 'bg-green-900/50 text-green-400' :
              consciousnessMetrics.interpretation?.confidence === 'Moderate' ? 'bg-yellow-900/50 text-yellow-400' :
                'bg-red-900/50 text-red-400'
              }`}>
              {consciousnessMetrics.interpretation?.confidence || 'Low'} Confidence
            </span>
          </h3>
        </div>
        <p className="text-white text-sm mb-2">
          {consciousnessMetrics.interpretation?.message || 'Analysis in progress...'}
        </p>
        <p className="text-xs text-gray-400 italic">
          {consciousnessMetrics.interpretation?.disclaimer || 'These are simulated correlates, not proof of consciousness.'}
        </p>
      </div>

      {/* Components Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-700/30 rounded-lg p-4">
          <h4 className="text-white font-semibold mb-3">ICI Components</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Temporal Coherence:</span>
              <span className="text-white">{((consciousnessMetrics.ici_components?.temporal_coherence || 0) * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Marker Integration:</span>
              <span className="text-white">{((consciousnessMetrics.ici_components?.marker_integration || 0) * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Resonance:</span>
              <span className="text-white">{((consciousnessMetrics.ici_components?.resonance || 0) * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-700/30 rounded-lg p-4">
          <h4 className="text-white font-semibold mb-3">PRS Components</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Avg Micro Entropy:</span>
              <span className="text-white">{((consciousnessMetrics.prs_components?.avg_micro_entropy || 0) * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Macro Entropy:</span>
              <span className="text-white">{((consciousnessMetrics.prs_components?.macro_entropy || 0) * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Raw Data Section */}
      {metrics?.raw_data && (
        <div className="bg-gray-700/30 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-white font-semibold">📊 Dados Brutos do Sistema Híbrido</h4>
            <button
              onClick={() => setShowRawData(!showRawData)}
              className="text-sm text-cyber-green hover:text-cyber-green/80 transition-colors"
            >
              {showRawData ? 'Ocultar' : 'Mostrar'} Dados Brutos
            </button>
          </div>

          {/* Estatísticas Resumidas */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="bg-gray-800/50 rounded p-3">
              <div className="text-xs text-gray-400">Predições Válidas</div>
              <div className="text-lg font-bold text-cyber-green">
                {metrics.raw_data.valid_predictions_count}/{metrics.raw_data.total_predictions}
              </div>
            </div>
            <div className="bg-gray-800/50 rounded p-3">
              <div className="text-xs text-gray-400">Ciclo Workspace</div>
              <div className="text-lg font-bold text-white">{metrics.raw_data.workspace_cycle}</div>
            </div>
            <div className="bg-gray-800/50 rounded p-3">
              <div className="text-xs text-gray-400">Total de Módulos</div>
              <div className="text-lg font-bold text-white">{metrics.raw_data.total_modules}</div>
            </div>
            <div className="bg-gray-800/50 rounded p-3">
              <div className="text-xs text-gray-400">Taxa de Validação</div>
              <div className="text-lg font-bold text-cyber-green">
                {metrics.raw_data.total_predictions > 0
                  ? ((metrics.raw_data.valid_predictions_count / metrics.raw_data.total_predictions) * 100).toFixed(0)
                  : 0}%
              </div>
            </div>
          </div>

          {/* Dados Brutos Expandidos */}
          {showRawData && (
            <div className="mt-4 space-y-4">
              {/* Predições Causais */}
              <div>
                <h5 className="text-white font-semibold mb-2 text-sm">
                  Predições Causais ({metrics.raw_data.causal_predictions.length})
                </h5>
                <div className="max-h-64 overflow-y-auto space-y-2">
                  {metrics.raw_data.causal_predictions.slice(0, 10).map((pred, idx) => (
                    <div key={idx} className="bg-gray-800/50 rounded p-2 text-xs">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-cyber-green font-mono">
                          {pred.source_module} → {pred.target_module}
                        </span>
                        <span className="text-gray-400">{pred.computation_time_ms.toFixed(2)}ms</span>
                      </div>
                      <div className="grid grid-cols-3 gap-2 text-gray-300">
                        <div>R²: {pred.r_squared.toFixed(4)}</div>
                        <div>Granger: {pred.granger_causality.toFixed(4)}</div>
                        <div>Transfer: {pred.transfer_entropy.toFixed(4)}</div>
                      </div>
                    </div>
                  ))}
                  {metrics.raw_data.causal_predictions.length > 10 && (
                    <div className="text-center text-gray-400 text-xs py-2">
                      ... e mais {metrics.raw_data.causal_predictions.length - 10} predições
                    </div>
                  )}
                </div>
              </div>

              {/* Estatísticas dos Módulos */}
              <div>
                <h5 className="text-white font-semibold mb-2 text-sm">Estatísticas dos Módulos</h5>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {Object.entries(metrics.raw_data.module_stats).map(([module, stats]: [string, any]) => (
                    <div key={module} className="bg-gray-800/50 rounded p-2 text-xs">
                      <div className="text-cyber-green font-mono truncate">{module}</div>
                      <div className="text-gray-400">Histórico: {stats.history_length}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
