import { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';
import { useAuthStore } from '../store/authStore';

interface DecisionSummary {
  action: string;
  timestamp: number;
  can_execute: boolean;
  reason: string;
  trust_level: number;
  success: boolean | null;
}

interface DecisionDetail extends DecisionSummary {
  context: Record<string, any>;
  permission_result: Record<string, any>;
  alternatives_considered: string[];
  expected_impact: Record<string, any>;
  risk_assessment: Record<string, any>;
  decision_rationale: string;
  error?: string;
}

interface DecisionStats {
  total_decisions: number;
  successful_decisions: number;
  failed_decisions: number;
  success_rate: number;
  average_trust_level: number;
  decisions_by_action: Record<string, number>;
  decisions_by_reason: Record<string, number>;
}

export function DecisionsDashboard() {
  const [decisions, setDecisions] = useState<DecisionSummary[]>([]);
  const [selectedDecision, setSelectedDecision] = useState<DecisionDetail | null>(null);
  const [stats, setStats] = useState<DecisionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filtros
  const [filters, setFilters] = useState({
    action: '',
    success: null as boolean | null,
    min_trust_level: 0,
    limit: 100,
  });

  const fetchDecisions = useCallback(async () => {
    // CORREÇÃO CRÍTICA (2025-12-10): Verificar autenticação antes de fazer fetch
    if (!useAuthStore.getState().isAuthenticated) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getDecisions();
      // Defensive check to ensure data is an array
      if (Array.isArray(data)) {
        setDecisions(data);
      } else {
        console.error('Expected array from getDecisions, got:', typeof data, data);
        setDecisions([]);
      }
    } catch (err) {
      // CORREÇÃO (2025-12-10): Não mostrar erro se não há autenticação
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar decisões';
      if (errorMessage !== 'Not authenticated') {
        setError(errorMessage);
        console.error('Error fetching decisions:', err);
      }
      setDecisions([]);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const fetchStats = useCallback(async () => {
    // CORREÇÃO CRÍTICA (2025-12-10): Verificar autenticação antes de fazer fetch
    if (!useAuthStore.getState().isAuthenticated) {
      return;
    }

    try {
      const data = await apiService.getDecisionStats();
      // Validate stats object
      if (data && typeof data === 'object') {
        setStats(data as DecisionStats);
      } else {
        setStats(null);
      }
    } catch (err) {
      // CORREÇÃO (2025-12-10): Não mostrar erro se não há autenticação
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar estatísticas';
      if (errorMessage !== 'Not authenticated') {
        console.error('Error fetching stats:', err);
      }
      setStats(null);
    }
  }, []);

  const fetchDecisionDetail = useCallback(async () => {
    // CORREÇÃO CRÍTICA (2025-12-10): Verificar autenticação antes de fazer fetch
    if (!useAuthStore.getState().isAuthenticated) {
      return;
    }

    try {
      const data = await apiService.getDecisionDetail();
      // Validate that data is an object with expected fields
      if (data && typeof data === 'object' && 'action' in data) {
        setSelectedDecision(data as DecisionDetail);
      } else {
        setSelectedDecision(null);
      }
    } catch (err) {
      // CORREÇÃO (2025-12-10): Não logar erro se não há autenticação
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      if (errorMessage !== 'Not authenticated') {
        console.error('Error fetching decision detail:', err);
      }
      setSelectedDecision(null);
    }
  }, []);

  const handleExport = useCallback(async () => {
    try {
      const data = await apiService.exportDecisions();

      // Criar download
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `decisions_export_${new Date().toISOString()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error exporting decisions:', err);
      alert('Erro ao exportar decisões');
    }
  }, [filters]);

  useEffect(() => {
    // CORREÇÃO CRÍTICA (2025-12-10): Verificar autenticação antes de fazer fetch
    const isAuthenticated = useAuthStore.getState().isAuthenticated;
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    const fetchData = () => {
      // Verificar autenticação antes de cada fetch
      if (!useAuthStore.getState().isAuthenticated) {
        return;
      }
      // Usar as funções diretamente, não como callbacks para evitar re-execução
      fetchDecisions().catch(() => {}); // Silenciar erros já tratados nas funções
      fetchStats().catch(() => {}); // Silenciar erros já tratados nas funções
    };

    fetchData();

    // Atualizar a cada 30 segundos
    const interval = setInterval(() => {
      // Verificar autenticação antes de cada intervalo
      if (useAuthStore.getState().isAuthenticated) {
        fetchData();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, []); // CORREÇÃO CRÍTICA: Array vazio - executa apenas uma vez na montagem

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString('pt-BR');
  };

  const getTrustLevelColor = (trust: number) => {
    if (trust >= 0.7) return 'text-green-600';
    if (trust >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSuccessBadge = (success: boolean | null) => {
    if (success === null) return <span className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">N/A</span>;
    if (success) return <span className="px-2 py-1 bg-green-900/50 text-green-300 rounded text-xs border border-green-500/30">✓ Sucesso</span>;
    return <span className="px-2 py-1 bg-red-900/50 text-red-300 rounded text-xs border border-red-500/30">✗ Falhou</span>;
  };

  if (loading && decisions.length === 0) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-700 rounded w-1/4"></div>
          <div className="h-64 bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">Dashboard de Decisões</h2>
        <button
          onClick={handleExport}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          Exportar JSON
        </button>
      </div>

      {error && (
        <div className="bg-red-900/50 border border-red-500 text-red-300 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Estatísticas */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="glass-card p-4">
            <div className="text-sm text-gray-400">Total de Decisões</div>
            <div className="text-2xl font-bold text-white">{stats.total_decisions}</div>
          </div>
          <div className="glass-card p-4">
            <div className="text-sm text-gray-400">Taxa de Sucesso</div>
            <div className="text-2xl font-bold text-green-400">{(stats.success_rate * 100).toFixed(1)}%</div>
          </div>
          <div className="glass-card p-4">
            <div className="text-sm text-gray-400">Confiança Média</div>
            <div className="text-2xl font-bold text-blue-400">{(stats.average_trust_level * 100).toFixed(1)}%</div>
          </div>
          <div className="glass-card p-4">
            <div className="text-sm text-gray-400">Decisões Falhadas</div>
            <div className="text-2xl font-bold text-red-400">{stats.failed_decisions}</div>
          </div>
        </div>
      )}

      {/* Filtros */}
      <div className="glass-card p-4">
        <h3 className="text-lg font-semibold mb-4 text-white">Filtros</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Ação</label>
            <input
              type="text"
              value={filters.action}
              onChange={(e) => setFilters({ ...filters, action: e.target.value })}
              placeholder="Filtrar por ação..."
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Status</label>
            <select
              value={filters.success === null ? '' : filters.success.toString()}
              onChange={(e) => setFilters({ ...filters, success: e.target.value === '' ? null : e.target.value === 'true' })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todos</option>
              <option value="true">Sucesso</option>
              <option value="false">Falhou</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Confiança Mínima</label>
            <input
              type="number"
              min="0"
              max="1"
              step="0.1"
              value={filters.min_trust_level}
              onChange={(e) => setFilters({ ...filters, min_trust_level: parseFloat(e.target.value) || 0 })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Limite</label>
            <input
              type="number"
              min="1"
              max="1000"
              value={filters.limit}
              onChange={(e) => setFilters({ ...filters, limit: parseInt(e.target.value) || 100 })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <button
          onClick={fetchDecisions}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          Aplicar Filtros
        </button>
      </div>

      {/* Lista de Decisões */}
      <div className="glass-card overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700">
          <h3 className="text-lg font-semibold text-white">Histórico de Decisões ({decisions.length})</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-700">
            <thead className="bg-gray-800/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Ação</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Data/Hora</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Confiança</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Razão</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {decisions.map((decision, index) => (
                <tr key={index} className="hover:bg-gray-800/30 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-white">{decision.action}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-400">{formatTimestamp(decision.timestamp)}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getSuccessBadge(decision.success)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className={`text-sm font-medium ${getTrustLevelColor(decision.trust_level)}`}>
                      {(decision.trust_level * 100).toFixed(1)}%
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-400">{decision.reason}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => fetchDecisionDetail()}
                      className="text-blue-400 hover:text-blue-300 text-sm transition-colors"
                    >
                      Ver Detalhes
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {decisions.length === 0 && !loading && (
            <div className="text-center py-8 text-gray-400">
              Nenhuma decisão encontrada
            </div>
          )}
        </div>
      </div>

      {/* Detalhes da Decisão Selecionada */}
      {selectedDecision && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">Detalhes da Decisão</h3>
            <button
              onClick={() => setSelectedDecision(null)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          <div className="space-y-4 text-gray-300">
            <div>
              <strong className="text-white">Ação:</strong> <span className="text-gray-300">{selectedDecision.action}</span>
            </div>
            <div>
              <strong className="text-white">Data/Hora:</strong> <span className="text-gray-300">{formatTimestamp(selectedDecision.timestamp)}</span>
            </div>
            <div>
              <strong className="text-white">Status:</strong> {getSuccessBadge(selectedDecision.success)}
            </div>
            <div>
              <strong className="text-white">Confiança:</strong> <span className={getTrustLevelColor(selectedDecision.trust_level)}>
                {(selectedDecision.trust_level * 100).toFixed(1)}%
              </span>
            </div>
            <div>
              <strong className="text-white">Razão:</strong> <span className="text-gray-300">{selectedDecision.reason}</span>
            </div>
            {selectedDecision.decision_rationale && (
              <div>
                <strong className="text-white">Racional:</strong>
                <p className="mt-1 text-sm text-gray-400">{selectedDecision.decision_rationale}</p>
              </div>
            )}
            {selectedDecision.alternatives_considered.length > 0 && (
              <div>
                <strong className="text-white">Alternativas Consideradas:</strong>
                <ul className="mt-1 list-disc list-inside text-sm text-gray-400">
                  {selectedDecision.alternatives_considered.map((alt, i) => (
                    <li key={i}>{alt}</li>
                  ))}
                </ul>
              </div>
            )}
            {selectedDecision.error && (
              <div className="bg-red-900/50 border border-red-500 rounded p-3">
                <strong className="text-red-300">Erro:</strong>
                <p className="text-sm text-red-400 mt-1">{selectedDecision.error}</p>
              </div>
            )}
            <details className="mt-4">
              <summary className="cursor-pointer text-sm font-medium text-gray-300 hover:text-white transition-colors">Contexto Completo</summary>
              <pre className="mt-2 p-4 bg-gray-800 rounded text-xs overflow-auto text-gray-300">
                {JSON.stringify(selectedDecision.context, null, 2)}
              </pre>
            </details>
          </div>
        </div>
      )}
    </div>
  );
}

