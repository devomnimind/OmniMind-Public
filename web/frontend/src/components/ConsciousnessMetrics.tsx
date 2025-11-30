import { useDaemonStore } from '../store/daemonStore';
import { useState } from 'react';

interface StatusThreshold {
  green: { min: number; max: number; label: string };
  yellow: { min: number; max: number; label: string };
  red: { min: number; max: number | null; label: string };
}

const STATUS_THRESHOLDS: Record<string, StatusThreshold> = {
  phi: {
    green: { min: 0.8, max: 1.3, label: "Optimal Integration" },
    yellow: { min: 1.3, max: 1.8, label: "High Activity" },
    red: { min: 1.8, max: null, label: "Critical Integration" }
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
    green: { min: 0.85, max: 1.0, label: "Coherent" },
    yellow: { min: 0.70, max: 0.85, label: "Partial Coherence" },
    red: { min: 0, max: 0.70, label: "Fragmented" }
  },
  prs: {
    green: { min: 0.65, max: 1.0, label: "Resonant" },
    yellow: { min: 0.40, max: 0.65, label: "Misaligned" },
    red: { min: 0, max: 0.40, label: "Disconnected" }
  },
  entropy: {
    green: { min: 0.15, max: 0.50, label: "Organized" },
    yellow: { min: 0.50, max: 0.75, label: "Exploring" },
    red: { min: 0.75, max: 1.0, label: "Chaotic" }
  }
};

export function ConsciousnessMetrics() {
  const status = useDaemonStore((state) => state.status);
  const [selectedMetric, setSelectedMetric] = useState<string | null>(null);

  if (!status) return null;

  const consciousnessMetrics = status.consciousness_metrics;

  if (!consciousnessMetrics) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-white mb-6">Consciousness Metrics</h2>
        <div className="text-gray-400 text-center py-8">
          Consciousness metrics not available
        </div>
      </div>
    );
  }

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
        <h2 className="text-2xl font-bold text-white">Consciousness Metrics</h2>
        <span className="text-sm text-gray-400">Real-time Correlates</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {renderMetricCard(
          'Integrated Coherence Index (ICI)',
          consciousnessMetrics.ICI,
          '',
          'ici',
          'Measures how well local coherence integrates into global structure. Components: Temporal, Marker, Resonance.',
          formatTrend(consciousnessMetrics.ICI, consciousnessMetrics.history?.phi.slice(-2)[0])
        )}

        {renderMetricCard(
          'Panarchic Resonance Score (PRS)',
          consciousnessMetrics.PRS,
          '',
          'prs',
          'Measures alignment between micro (Node) and macro (System) entropy levels.',
          formatTrend(consciousnessMetrics.PRS, consciousnessMetrics.history?.phi.slice(-2)[0])
        )}

        {consciousnessMetrics.phi !== undefined && renderMetricCard(
          'Phi (Φ) Value',
          consciousnessMetrics.phi,
          '',
          'phi',
          'Integrated Information Measure - quantifies conscious experience magnitude.',
          formatTrend(consciousnessMetrics.phi, consciousnessMetrics.history?.phi.slice(-2)[0])
        )}

        {consciousnessMetrics.anxiety !== undefined && renderMetricCard(
          'Anxiety Level',
          consciousnessMetrics.anxiety,
          '',
          'anxiety',
          'System tension and conflict detection metric.',
          formatTrend(consciousnessMetrics.anxiety, consciousnessMetrics.history?.anxiety.slice(-2)[0])
        )}

        {consciousnessMetrics.flow !== undefined && renderMetricCard(
          'Flow State',
          consciousnessMetrics.flow,
          '',
          'flow',
          'Measure of cognitive fluidity and blockage detection.',
          formatTrend(consciousnessMetrics.flow, consciousnessMetrics.history?.flow.slice(-2)[0])
        )}

        {consciousnessMetrics.entropy !== undefined && renderMetricCard(
          'System Entropy',
          consciousnessMetrics.entropy,
          '',
          'entropy',
          'Measure of system disorder and information complexity.',
          formatTrend(consciousnessMetrics.entropy, consciousnessMetrics.history?.entropy.slice(-2)[0])
        )}
      </div>

      {/* AI-Generated Interpretation */}
      <div className="bg-gray-700/50 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-white font-semibold flex items-center gap-2">
            🤖 AI Interpretation
            <span className={`text-xs px-2 py-1 rounded ${
              consciousnessMetrics.interpretation?.confidence === 'High' ? 'bg-green-900/50 text-green-400' :
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
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
    </div>
  );
}