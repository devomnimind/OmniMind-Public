/**
 * LLM Analysis Panel - Display AI-generated insights about metrics
 */

import React, { useState } from 'react';
import { llmService } from '../services/llm';
import { useDaemonStore } from '../store/daemonStore';

export const LLMAnalysisPanel: React.FC = () => {
  const [analysis, setAnalysis] = useState<string>('Waiting for analysis...');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tier, setTier] = useState<'fast' | 'balanced' | 'high_quality'>('balanced');

  const status = useDaemonStore((state) => state.status);

  const analyzeMetrics = async () => {
    setLoading(true);
    setError(null);
    try {
      const insights = await llmService.analyzeMetrics(status?.consciousness_metrics || {});
      setAnalysis(insights);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Analysis failed';
      setError(message);
      setAnalysis('Analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  const analyzeModules = async () => {
    setLoading(true);
    setError(null);
    try {
      const moduleActivity = (status?.module_activity as any) || {};
      const insights = await llmService.analyzeModuleActivity(moduleActivity);
      setAnalysis(insights);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Analysis failed';
      setError(message);
      setAnalysis('Analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  const generateSystemInsights = async () => {
    setLoading(true);
    setError(null);
    try {
      const insights = await llmService.generateInsights({
        overall_status: status?.system_health?.overall || 'unknown',
        cpu_percent: status?.system_metrics?.cpu_percent || 0,
        memory_percent: status?.system_metrics?.memory_percent || 0,
        uptime_seconds: 0,
        active_tasks: status?.task_count || 0,
      });
      setAnalysis(insights);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Analysis failed';
      setError(message);
      setAnalysis('Analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 border border-cyan-500 rounded-lg p-6 shadow-lg">
      {/* Header */}
      <div className="mb-4">
        <h3 className="text-xl font-bold text-cyan-400 mb-2">🧠 LLM Analysis</h3>
        <p className="text-gray-400 text-sm">AI-powered insights about your system</p>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap gap-2 mb-4">
        <button
          onClick={analyzeMetrics}
          disabled={loading}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 disabled:bg-gray-600 text-white rounded text-sm font-semibold transition"
        >
          {loading ? '⏳ Analyzing...' : '📊 Analyze Metrics'}
        </button>

        <button
          onClick={analyzeModules}
          disabled={loading}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white rounded text-sm font-semibold transition"
        >
          {loading ? '⏳ Analyzing...' : '🔧 Analyze Modules'}
        </button>

        <button
          onClick={generateSystemInsights}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded text-sm font-semibold transition"
        >
          {loading ? '⏳ Generating...' : '💡 System Insights'}
        </button>

        <select
          value={tier}
          onChange={(e) => setTier(e.target.value as any)}
          disabled={loading}
          className="px-3 py-2 bg-gray-800 text-white rounded text-sm border border-gray-600 hover:border-cyan-500"
        >
          <option value="fast">Fast (Quick)</option>
          <option value="balanced">Balanced (Default)</option>
          <option value="high_quality">High Quality (Slow)</option>
        </select>
      </div>

      {/* Error display */}
      {error && (
        <div className="mb-4 p-3 bg-red-900 border border-red-500 rounded text-red-200 text-sm">
          ❌ {error}
        </div>
      )}

      {/* Analysis text */}
      <div className="bg-gray-800 rounded p-4 text-gray-100 text-sm leading-relaxed min-h-32 max-h-64 overflow-y-auto">
        {analysis}
      </div>

      {/* Status footer */}
      <div className="mt-4 text-xs text-gray-500 flex justify-between">
        <span>Model: {tier}</span>
        <span>{loading ? 'Processing...' : 'Ready'}</span>
      </div>
    </div>
  );
};

export default LLMAnalysisPanel;
