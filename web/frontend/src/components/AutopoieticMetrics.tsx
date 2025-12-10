import { useEffect, useState } from 'react';
import { apiService } from '../services/api';
import { useAuthStore } from '../store/authStore';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

interface CycleData {
  cycle_id: number;
  strategy: string;
  synthesized_components: string[];
  phi_before: number | null;
  phi_after: number | null;
  timestamp: number;
}

interface AutopoieticStatus {
  running: boolean;
  cycle_count: number;
  component_count: number;
  current_phi: number | null;
  phi_threshold: number;
}

interface CycleStats {
  total_cycles: number;
  successful_syntheses: number;
  rejected_before: number;
  rolled_back: number;
  strategies: Record<string, number>;
  phi_before_avg: number;
  phi_after_avg: number;
  phi_delta_avg: number;
}

const COLORS = ['#10b981', '#f59e0b', '#ef4444', '#3b82f6', '#8b5cf6'];

export function AutopoieticMetrics() {
  const [status, setStatus] = useState<AutopoieticStatus | null>(null);
  const [cycles, setCycles] = useState<CycleData[]>([]);
  const [stats, setStats] = useState<CycleStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      // Se não tiver token, nem tenta buscar (evita erro 401 spam)
      if (!apiService.getAuthToken()) {
         return;
      }

      // Garantir que credenciais estão configuradas
      if (!apiService.getAuthToken()) {
        apiService.setDefaultCredentials();
      }

      // Usar apiService que já tem autenticação configurada
      const [statusData, cyclesData, statsData] = await Promise.all([
        apiService.getAutopoieticStatus().catch((err) => {
          // CORREÇÃO (2025-12-10): Não logar erro se não há autenticação
          const errorMessage = err instanceof Error ? err.message : 'Unknown error';
          if (errorMessage !== 'Not authenticated') {
            console.error('Erro ao buscar status:', err);
          }
          return null;
        }),
        apiService.getAutopoieticCycles(50).catch((err) => {
          // CORREÇÃO (2025-12-10): Não logar erro se não há autenticação
          const errorMessage = err instanceof Error ? err.message : 'Unknown error';
          if (errorMessage !== 'Not authenticated') {
            console.error('Erro ao buscar ciclos:', err);
          }
          return { cycles: [], total: 0 };
        }),
        apiService.getAutopoieticCycleStats().catch((err) => {
          // CORREÇÃO (2025-12-10): Não logar erro se não há autenticação
          const errorMessage = err instanceof Error ? err.message : 'Unknown error';
          if (errorMessage !== 'Not authenticated') {
            console.error('Erro ao buscar stats:', err);
          }
          return null;
        }),
      ]);

      // Processar status
      if (statusData) {
        // Garantir que current_phi seja tratado corretamente (0.0 é válido, não null)
        const processedStatus = {
          ...statusData,
          current_phi: statusData.current_phi !== null && statusData.current_phi !== undefined
            ? statusData.current_phi
            : null,
        };
        setStatus(processedStatus);
      } else {
        console.warn('Status API não respondeu');
        // Definir valores padrão se status não estiver disponível
        if (!status) {
          setStatus({
            running: false,
            cycle_count: 0,
            component_count: 0,
            current_phi: null,
            phi_threshold: 0.3,
          });
        }
      }

      // Processar ciclos
      if (cyclesData && cyclesData.cycles) {
        setCycles(cyclesData.cycles || []);
      }

      // Processar estatísticas
      if (statsData) {
        setStats(statsData);
      }
    } catch (error) {
      console.error('Erro ao buscar métricas autopoiéticas:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Verificar autenticação antes de fazer fetch
    const isAuthenticated = useAuthStore.getState().isAuthenticated;
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    fetchData();
    // CORREÇÃO (2025-12-09): Manter 30s (métricas importantes mas não críticas)
    const interval = setInterval(() => {
      // Verificar autenticação antes de cada fetch
      if (useAuthStore.getState().isAuthenticated) {
        fetchData();
      }
    }, 30000); // Atualizar a cada 30s (métricas importantes)
    return () => clearInterval(interval);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) {
    return (
      <div className="glass-card p-6">
        <div className="text-gray-300 animate-pulse">Carregando métricas autopoiéticas...</div>
      </div>
    );
  }

  // Verificar se status está disponível
  if (!status) {
    return (
      <div className="glass-card p-6">
        <h2 className="text-2xl font-bold mb-4 text-white">🔄 Status do Ciclo Autopoiético</h2>
        <div className="text-gray-400 text-center py-8">
          Status não disponível. Verificando conexão com backend...
        </div>
      </div>
    );
  }

  // Preparar dados para gráficos
  const phiHistory = cycles
    .filter((c) => c.phi_before !== null && c.phi_after !== null)
    .map((c) => ({
      cycle: c.cycle_id,
      phiBefore: c.phi_before,
      phiAfter: c.phi_after,
      delta: (c.phi_after || 0) - (c.phi_before || 0),
    }))
    .slice(-30); // Últimos 30 ciclos

  const strategyData = stats
    ? Object.entries(stats.strategies).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  const outcomeData = stats
    ? [
        { name: 'Sucessos', value: stats.successful_syntheses, color: '#10b981' },
        { name: 'Rejeitados', value: stats.rejected_before, color: '#f59e0b' },
        { name: 'Rollbacks', value: stats.rolled_back, color: '#ef4444' },
      ]
    : [];

  return (
    <div className="space-y-6">
      {/* Status Card */}
      <div className="glass-card p-6">
        <h2 className="text-2xl font-bold mb-4 text-white">🔄 Status do Ciclo Autopoiético</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-sm text-gray-400">Status</div>
            <div className="text-xl font-semibold text-white">
              {status?.running ? (
                <span className="text-green-400">● Rodando</span>
              ) : (
                <span className="text-red-400">● Parado</span>
              )}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Total de Ciclos</div>
            <div className="text-xl font-semibold text-white">{status?.cycle_count || 0}</div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Componentes</div>
            <div className="text-xl font-semibold text-white">{status?.component_count || 0}</div>
          </div>
          <div>
            <div className="text-sm text-gray-400">Φ Atual</div>
            <div className="text-xl font-semibold text-white">
              {status && status.current_phi !== null && status.current_phi !== undefined
                ? status.current_phi.toFixed(4)
                : 'N/A'}
              {status && status.current_phi !== null && status.current_phi !== undefined &&
                (status.current_phi < (status.phi_threshold || 0.3) ? (
                  <span className="text-red-400 ml-2">⚠️</span>
                ) : (
                  <span className="text-green-400 ml-2">✓</span>
                ))}
            </div>
          </div>
        </div>
      </div>

      {/* Estatísticas Gerais */}
      {stats && (
        <div className="glass-card p-6">
          <h2 className="text-2xl font-bold mb-4 text-white">📊 Estatísticas Gerais</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div>
              <div className="text-sm text-gray-400">Total de Ciclos</div>
              <div className="text-2xl font-bold text-white">{stats.total_cycles}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Sínteses Bem-sucedidas</div>
              <div className="text-2xl font-bold text-green-400">
                {stats.successful_syntheses}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Rejeitados (Φ baixo)</div>
              <div className="text-2xl font-bold text-yellow-400">
                {stats.rejected_before}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Rollbacks</div>
              <div className="text-2xl font-bold text-red-400">{stats.rolled_back}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div className="text-sm text-gray-400">Φ Médio (Antes)</div>
              <div className="text-xl font-semibold text-white">{stats.phi_before_avg.toFixed(4)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Φ Médio (Depois)</div>
              <div className="text-xl font-semibold text-white">{stats.phi_after_avg.toFixed(4)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">ΔΦ Médio</div>
              <div
                className={`text-xl font-semibold ${
                  stats.phi_delta_avg >= 0 ? 'text-green-400' : 'text-red-400'
                }`}
              >
                {stats.phi_delta_avg >= 0 ? '+' : ''}
                {stats.phi_delta_avg.toFixed(4)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Histórico de Φ */}
        {phiHistory.length > 0 && (
          <div className="glass-card p-6">
            <h3 className="text-xl font-bold mb-4 text-white">📈 Histórico de Φ (Últimos 30 ciclos)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={phiHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" />
                <XAxis dataKey="cycle" stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
                <YAxis domain={[0, 1]} stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563', color: '#f3f4f6' }} />
                <Legend wrapperStyle={{ color: '#f3f4f6' }} />
                <Line
                  type="monotone"
                  dataKey="phiBefore"
                  stroke="#3b82f6"
                  name="Φ Antes"
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="phiAfter"
                  stroke="#10b981"
                  name="Φ Depois"
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="delta"
                  stroke="#f59e0b"
                  name="ΔΦ"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Distribuição de Estratégias */}
        {strategyData.length > 0 && (
          <div className="glass-card p-6">
            <h3 className="text-xl font-bold mb-4 text-white">🔧 Distribuição de Estratégias</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={strategyData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  style={{ fontSize: '12px', fill: '#f3f4f6' }}
                >
                  {strategyData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563', color: '#f3f4f6' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Resultados dos Ciclos */}
        {outcomeData.length > 0 && (
          <div className="glass-card p-6">
            <h3 className="text-xl font-bold mb-4 text-white">📊 Resultados dos Ciclos</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={outcomeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" />
                <XAxis dataKey="name" stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
                <YAxis stroke="#9ca3af" tick={{ fill: '#9ca3af' }} />
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563', color: '#f3f4f6' }} />
                <Bar dataKey="value" fill="#8884d8">
                  {outcomeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}

