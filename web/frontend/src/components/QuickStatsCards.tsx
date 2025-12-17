import { useDaemonStore } from '../store/daemonStore';
import { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';
import { useAuthStore } from '../store/authStore';

interface AuditStats {
  total_events: number;
  chain_integrity: boolean;
}

interface TrainingMetrics {
  total_iterations: number;
  avg_conflict_quality: number; // percentual 0-100
  repression_events: number;
}

export function QuickStatsCards() {
  const status = useDaemonStore((state) => state.status);
  const [auditStats, setAuditStats] = useState<AuditStats | null>(null);
  const [trainingMetrics, setTrainingMetrics] = useState<TrainingMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchAllMetrics = useCallback(async () => {
    // CORREÇÃO CRÍTICA (2025-12-10): Verificar autenticação antes de fazer fetch
    if (!useAuthStore.getState().isAuthenticated) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const [auditData, trainingData] = await Promise.all([
        apiService.get('/audit/stats').catch((err) => {
          // CORREÇÃO (2025-12-10): Não logar erro se não há autenticação ou timeout
          const errorMessage = err instanceof Error ? err.message : 'Unknown error';
          if (errorMessage !== 'Not authenticated' && !errorMessage.includes('timeout')) {
            console.error('Failed to fetch audit stats:', err);
          }
          return null;
        }),
        apiService.get('/metrics/training').catch((err) => {
          // CORREÇÃO (2025-12-10): Não logar erro se não há autenticação ou timeout
          const errorMessage = err instanceof Error ? err.message : 'Unknown error';
          if (errorMessage !== 'Not authenticated' && !errorMessage.includes('timeout')) {
            console.error('Failed to fetch training metrics:', err);
          }
          return null;
        }),
      ]);

      if (auditData) {
        setAuditStats({
          total_events: auditData?.total_events ?? 0,
          chain_integrity: Boolean(auditData?.chain_integrity),
        });
      }

      if (trainingData) {
        setTrainingMetrics({
          total_iterations: trainingData?.total_iterations ?? 0,
          avg_conflict_quality: Math.round((trainingData?.avg_conflict_quality ?? 0) * 100),
          repression_events: trainingData?.repression_events ?? 0,
        });
      }

      setLastUpdated(new Date());
    } catch (err) {
      // CORREÇÃO (2025-12-10): Não mostrar erro se não há autenticação ou timeout
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      if (errorMessage !== 'Not authenticated' && !errorMessage.includes('timeout')) {
        console.error('Failed to fetch metrics:', err);
        setError('Não foi possível carregar as métricas em tempo real.');
      }
      // Não limpar dados existentes em caso de erro temporário
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // CORREÇÃO CRÍTICA (2025-12-10): Verificar autenticação antes de fazer fetch
    const isAuthenticated = useAuthStore.getState().isAuthenticated;
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    fetchAllMetrics();
    // CORREÇÃO (2025-12-09): Aumentar intervalo para 30s (métricas importantes)
    const interval = setInterval(() => {
      // Verificar autenticação antes de cada fetch
      if (useAuthStore.getState().isAuthenticated) {
        fetchAllMetrics();
      }
    }, 30000); // Atualizar a cada 30s
    return () => clearInterval(interval);
  }, [fetchAllMetrics]); // Dependência em fetchAllMetrics

  if (!status) return null;

  const getStatusColor = (value?: number, total?: number) => {
    if (value === null || value === undefined) return 'text-gray-500';
    if (total) {
      const percentage = (value / total) * 100;
      if (percentage >= 95) return 'text-green-400';
      if (percentage >= 80) return 'text-yellow-400';
      return 'text-red-400';
    }

    if (value >= 90) return 'text-green-400';
    if (value >= 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  const renderValue = (value: number | null | undefined, suffix = '') => {
    if (value === null || value === undefined) {
      return <span className="text-gray-500">—</span>;
    }
    return (
      <span>
        {value}
        {suffix}
      </span>
    );
  };

  return (
    <div className="glass-card p-6">
      <h2 className="text-2xl font-bold text-gradient-cyber mb-6 flex items-center gap-2">
        📈 Quick Stats
        <span className="text-sm text-gray-400 font-normal">(System Overview)</span>
      </h2>

      {error && (
        <div className="mb-4 bg-red-900/30 border border-red-500/40 text-red-200 text-sm rounded-lg p-3 flex items-center justify-between">
          <span>{error}</span>
          <button
            onClick={fetchAllMetrics}
            className="btn-outline-neon text-xs px-3 py-1"
          >
            Tentar novamente
          </button>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-8">
          <div className="spinner-cyber w-8 h-8" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Training Iterations */}
          <div className="bg-gray-700/30 rounded-lg p-4 text-center hover-lift">
            <div className="text-2xl mb-2">🧠</div>
            <div className="text-gray-400 text-xs mb-1">Training Runs</div>
            <div className="text-xl font-bold text-cyber-400">
              {renderValue(trainingMetrics?.total_iterations)}
            </div>
            <div className="text-xs text-cyber-400">
              ✅ Iterations
            </div>
          </div>

          {/* Conflict Quality */}
          <div className="bg-gray-700/30 rounded-lg p-4 text-center hover-lift">
            <div className="text-2xl mb-2">🎯</div>
            <div className="text-gray-400 text-xs mb-1">Avg Quality</div>
            <div
              className={`text-xl font-bold ${
                trainingMetrics?.avg_conflict_quality !== undefined
                  ? getStatusColor(trainingMetrics?.avg_conflict_quality)
                  : 'text-gray-500'
              }`}
            >
              {trainingMetrics?.avg_conflict_quality !== undefined
                ? `${trainingMetrics?.avg_conflict_quality}%`
                : '—'}
            </div>
            <div
              className={`text-xs ${
                trainingMetrics?.avg_conflict_quality !== undefined
                  ? getStatusColor(trainingMetrics?.avg_conflict_quality)
                  : 'text-gray-500'
              }`}
            >
              {trainingMetrics?.avg_conflict_quality !== undefined
                ? trainingMetrics.avg_conflict_quality >= 80
                  ? '✅ Good'
                  : trainingMetrics.avg_conflict_quality >= 60
                  ? '⚠️ Fair'
                  : '❌ Low'
                : 'Sem dados'}
            </div>
          </div>

          {/* Audit Chain */}
          <div className="bg-gray-700/30 rounded-lg p-4 text-center hover-lift">
            <div className="text-2xl mb-2">🔗</div>
            <div className="text-gray-400 text-xs mb-1">Audit Events</div>
            <div className="text-xl font-bold text-blue-400">
              {auditStats ? auditStats.total_events.toLocaleString() : '—'}
            </div>
            <div className="text-xs text-blue-400">
              {auditStats
                ? auditStats.chain_integrity
                  ? '✅ Intact'
                  : '⚠️ Check'
                : 'Sem dados'}
            </div>
          </div>

          {/* Repressed Memories */}
          <div className="bg-gray-700/30 rounded-lg p-4 text-center hover-lift">
            <div className="text-2xl mb-2">🔐</div>
            <div className="text-gray-400 text-xs mb-1">Repressed</div>
            <div className="text-xl font-bold text-purple-400">
              {renderValue(trainingMetrics?.repression_events)}
            </div>
            <div className="text-xs text-purple-400">
              Encrypted
            </div>
          </div>

          {/* System Uptime */}
          <div className="bg-gray-700/30 rounded-lg p-4 text-center hover-lift">
            <div className="text-2xl mb-2">⏱️</div>
            <div className="text-gray-400 text-xs mb-1">Uptime</div>
            <div className="text-xl font-bold text-green-400">
              {Math.floor((status?.uptime_seconds || 0) / 3600)}h
            </div>
            <div className="text-xs text-green-400">
              ✅ Stable
            </div>
          </div>
        </div>
      )}

      <div className="mt-6 pt-4 border-t border-gray-700">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>
            Last Updated:{' '}
            {lastUpdated ? lastUpdated.toLocaleTimeString() : '—'}
          </span>
          <div className="flex gap-2">
            <button className="btn-outline-neon text-xs px-3 py-1">
              📊 Export
            </button>
            <button
              onClick={fetchAllMetrics}
              className="btn-outline-neon text-xs px-3 py-1"
            >
              🔄 Refresh
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
