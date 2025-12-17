import { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { useAuthStore } from '../store/authStore';

interface TribunalData {
  status: string;
  activity_score: number;
  proposals: Array<{
    id: string;
    title: string;
    description: string;
    severity: 'info' | 'success' | 'warning' | 'error';
  }>;
  metrics: {
    attacks_count: number;
    duration_hours: number;
  };
}

export function TribunalStatus() {
  const [data, setData] = useState<TribunalData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // CORREÇÃO CRÍTICA (2025-12-10): Verificar autenticação antes de fazer fetch
    const isAuthenticated = useAuthStore.getState().isAuthenticated;
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    const fetchTribunal = async () => {
      // Verificar autenticação antes de cada fetch
      if (!useAuthStore.getState().isAuthenticated) {
        return;
      }

      try {
        const result = await apiService.getTribunalActivity();
        setData(result);
        setError(null);
      } catch (err) {
        // CORREÇÃO (2025-12-10): Não mostrar erro se não há autenticação
        const errorMessage = err instanceof Error ? err.message : 'Failed to load Tribunal status';
        if (errorMessage !== 'Not authenticated') {
          setError('Failed to load Tribunal status');
          console.error(err);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchTribunal();
    // CORREÇÃO (2025-12-09): Aumentar intervalo para 30s (métricas importantes)
    const interval = setInterval(fetchTribunal, 30000); // Atualizar a cada 30s
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="glass-card p-6 animate-pulse">Loading Tribunal...</div>;
  if (error) return <div className="glass-card p-6 text-red-500">{error}</div>;
  if (!data) return null;

  // Null-safe status with fallback
  const status = data.status || 'unknown';
  const activityScore = data.activity_score ?? 0;
  const proposals = data.proposals || [];

  return (
    <div className="glass-card p-6 relative overflow-hidden group hover:shadow-neon-red transition-all duration-300">
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
        <span className="text-6xl">⚖️</span>
      </div>

      <h2 className="text-xl font-bold text-gradient-neon mb-4 flex items-center gap-2">
        <span>⚖️</span> Tribunal do Diabo
      </h2>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-dark-200/50 p-3 rounded-lg">
          <div className="text-sm text-gray-400">Status</div>
          <div className={`font-mono font-bold ${status === 'running' ? 'text-yellow-400 animate-pulse' : status === 'finished' ? 'text-green-400' : 'text-gray-400'}`}>
            {status.toUpperCase()}
          </div>
        </div>
        <div className="bg-dark-200/50 p-3 rounded-lg">
          <div className="text-sm text-gray-400">Activity Score</div>
          <div className="font-mono font-bold text-neon-blue">
            {(activityScore * 100).toFixed(0)}%
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-gray-300">Proposals</h3>
        {proposals.length === 0 ? (
          <div className="text-sm text-gray-500 italic">No active proposals</div>
        ) : (
          proposals.map((prop) => (
            <div key={prop.id} className={`p-3 rounded border ${
              prop.severity === 'success' ? 'border-green-500/30 bg-green-500/10' :
              prop.severity === 'warning' ? 'border-yellow-500/30 bg-yellow-500/10' :
              'border-blue-500/30 bg-blue-500/10'
            }`}>
              <div className="font-bold text-sm mb-1">{prop.title}</div>
              <div className="text-xs text-gray-400">{prop.description}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
