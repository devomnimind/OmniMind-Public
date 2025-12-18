import { useEffect, useCallback } from 'react';
import { useAuthStore } from '../store/authStore';
import { useDaemonStore } from '../store/daemonStore';
import { apiService } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import type { DaemonStatus as DaemonStatusType } from '../types/daemon';
import { DaemonStatus } from './DaemonStatus';
import { TribunalStatus } from './TribunalStatus';
import { TribunalMetricsVisual } from './TribunalMetricsVisual';
import { SystemMetrics } from './SystemMetrics';
import { TaskList } from './TaskList';
import { TaskForm } from './TaskForm';
import { AgentStatus } from './AgentStatus';
import { DaemonControls } from './DaemonControls';
import { ConnectionStatus } from './ConnectionStatus';
import { DashboardSkeleton } from './LoadingSkeletons';
import { RealtimeAnalytics } from './RealtimeAnalytics';
import { WorkflowVisualization } from './WorkflowVisualization';
import { NotificationCenter } from './NotificationCenter';
import { OmniMindSinthome } from './OmniMindSinthome';
import { ConsciousnessMetrics } from './ConsciousnessMetrics';
import { SystemHealthSummary } from './SystemHealthSummary';
import { AutopoieticMetrics } from './AutopoieticMetrics';
import { EventLog } from './EventLog';
import { ModuleActivityHeatmap } from './ModuleActivityHeatmap';
import { QuickStatsCards } from './QuickStatsCards';
import { MetricsTimeline } from './MetricsTimeline';
import { BaselineComparison } from './BaselineComparison';
import { ActionButtons } from './ActionButtons';
import { ConversationAssistant } from './ConversationAssistant';
import { DecisionsDashboard } from './DecisionsDashboard';
import { PsychoanalyticDashboard } from './PsychoanalyticDashboard';

export function Dashboard() {
  const logout = useAuthStore((state) => state.logout);
  const username = useAuthStore((state) => state.username);
  const { status, setStatus, updateStatus, setTasks, setLoading, setError, loading } = useDaemonStore();
  const { lastMessage } = useWebSocket();

  const fetchData = useCallback(async () => {
    // Se não estiver autenticado, não faz requests para evitar spam de 401
    if (!useAuthStore.getState().isAuthenticated) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      // CORREÇÃO (2025-12-09): Timeout individual para cada request
      const [status, tasks] = await Promise.allSettled([
        apiService.getDaemonStatus().catch(err => {
          console.error('[Dashboard] Erro ao buscar status:', err);
          return null; // Retornar null em caso de erro
        }),
        apiService.getDaemonTasks().catch(err => {
          console.error('[Dashboard] Erro ao buscar tarefas:', err);
          return null; // Retornar null em caso de erro
        }),
      ]);

      // Processar resultados
      if (status.status === 'fulfilled' && status.value) {
        setStatus(status.value);
      }
      if (tasks.status === 'fulfilled' && tasks.value) {
        setTasks(tasks.value);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [setStatus, setTasks, setLoading, setError]);

  // Handle WebSocket messages
  useEffect(() => {
    if (!lastMessage) return;

    // CORREÇÃO CRÍTICA (2025-12-09): Depender apenas de campos estáveis da mensagem
    // lastMessage muda constantemente, causando loop infinito
    const messageType = lastMessage.type;
    const messageData = lastMessage.data;

    switch (messageType) {
      case 'daemon_status':
        setStatus(messageData as DaemonStatusType);
        break;
      case 'task_update':
        // Refresh tasks when update received (sem chamar fetchData para evitar loop)
        // Os componentes individuais já fazem polling
        break;
      case 'agent_update':
        // Agent updates handled by AgentStatus component
        break;
      case 'metrics_update':
        // Metrics updates handled automatically by RealtimeAnalytics
        // Não atualizar status aqui para evitar loops - RealtimeAnalytics já processa
        break;
      case 'omnimind_pulse':
        const pulse = messageData;
        updateStatus({
          system_metrics: status ? {
            ...status.system_metrics,
            cpu_percent: pulse.hardware.cpu,
            memory_percent: pulse.hardware.memory,
          } : undefined,
          task_count: pulse.daemon.tasks.task_count,
          completed_tasks: pulse.daemon.tasks.completed_tasks,
          failed_tasks: pulse.daemon.tasks.failed_tasks,
          consciousness_metrics: status ? {
            ...status.consciousness_metrics,
            phi: pulse.consciousness.phi,
            anxiety: pulse.consciousness.anxiety,
            flow: pulse.consciousness.flow,
            entropy: pulse.consciousness.entropy,
            ici: pulse.consciousness.ici,
            prs: pulse.consciousness.prs,
            interpretation: pulse.consciousness.interpretation,
          } : undefined
        } as any);
        break;
      default:
        // Ignorar mensagens desconhecidas silenciosamente
        break;
    }
  }, [lastMessage?.type, lastMessage?.id, status]); // Adicionado status para garantir mapeamento correto

  useEffect(() => {
    // Verificar autenticação antes de fazer fetch
    if (!useAuthStore.getState().isAuthenticated) {
      return;
    }

    // CORREÇÃO CRÍTICA (2025-12-09): Usar função estável para evitar loop infinito
    // fetchData é recriado a cada render, causando loop infinito
    const fetchDataStable = async () => {
      if (!useAuthStore.getState().isAuthenticated) {
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const [status, tasks] = await Promise.allSettled([
          apiService.getDaemonStatus().catch(err => {
            // CORREÇÃO (2025-12-10): Não logar erro se não há autenticação
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            if (errorMessage !== 'Not authenticated') {
              console.error('[Dashboard] Erro ao buscar status:', err);
            }
            return null;
          }),
          apiService.getDaemonTasks().catch(err => {
            // CORREÇÃO (2025-12-10): Não logar erro se não há autenticação
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            if (errorMessage !== 'Not authenticated') {
              console.error('[Dashboard] Erro ao buscar tarefas:', err);
            }
            return null;
          }),
        ]);

        if (status.status === 'fulfilled' && status.value) {
          setStatus(status.value);
        }
        if (tasks.status === 'fulfilled' && tasks.value) {
          setTasks(tasks.value);
        }
      } catch (err) {
        // CORREÇÃO (2025-12-10): Não mostrar erro se não há autenticação
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch data';
        if (errorMessage !== 'Not authenticated') {
          setError(errorMessage);
          console.error('Fetch error:', err);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDataStable();
    // CORREÇÃO (2025-12-09): Aumentar intervalo para 15s (métricas críticas mas não precisa ser tão frequente)
    // Dashboard precisa estar atualizado mas não precisa sobrecarregar servidor
    const interval = setInterval(() => {
      // Verificar autenticação antes de cada fetch
      if (useAuthStore.getState().isAuthenticated) {
        fetchDataStable();
      }
    }, 15000); // Atualizar a cada 15s (métricas críticas)
    return () => clearInterval(interval);
  }, []); // CORREÇÃO CRÍTICA: Array vazio - executa apenas uma vez na montagem

  // Show loading skeleton on initial load
  if (loading && !useDaemonStore.getState().status) {
    return <DashboardSkeleton />;
  }

  return (
    <div className="min-h-screen bg-dark-300 cyber-grid">
      {/* Animated Background Gradient */}
      <div className="fixed inset-0 bg-gradient-to-br from-dark-300 via-dark-200 to-dark-300 opacity-50 pointer-events-none" />

      {/* Header */}
      <header className="glass-card sticky top-0 z-50 border-b border-cyber-500/20 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-3xl font-bold text-gradient-cyber animate-fade-in">
                🧠 OmniMind Dashboard
              </h1>
              <button
                onClick={fetchData}
                className="btn-outline-neon text-sm focus-cyber"
                disabled={loading}
                aria-label="Refresh dashboard data"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <span className="spinner-cyber w-4 h-4" />
                    Syncing...
                  </span>
                ) : (
                  <>🔄 Refresh</>
                )}
              </button>
              <ConnectionStatus />
            </div>
            <div className="flex items-center gap-4">
              <NotificationCenter />
              <span className="text-gray-400">
                Welcome, <span className="text-gradient-neon font-semibold">{username}</span>
              </span>
              <button
                onClick={logout}
                className="px-4 py-2 bg-gradient-to-r from-neon-red to-red-700 hover:from-neon-red/80 hover:to-red-600 text-white rounded-lg font-semibold transition-all duration-300 hover:shadow-pink-glow focus-cyber"
                aria-label="Logout from dashboard"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Real-time Analytics Section */}
        <div className="mb-6 animate-slide-up">
          <RealtimeAnalytics />
        </div>

        {/* Workflow Visualization Section */}
        <div className="mb-6 animate-slide-up" style={{ animationDelay: '0.1s' }}>
          <WorkflowVisualization />
        </div>

        {/* System Health & Quick Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <SystemHealthSummary />
          </div>
          <div className="lg:col-span-2 animate-slide-up" style={{ animationDelay: '0.25s' }}>
            <QuickStatsCards />
          </div>
        </div>

        {/* Consciousness Metrics & Timeline */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="animate-slide-up" style={{ animationDelay: '0.3s' }}>
            <ConsciousnessMetrics />
          </div>
          <div className="animate-slide-up" style={{ animationDelay: '0.35s' }}>
            <MetricsTimeline />
          </div>
        </div>

        {/* Psychoanalytic Dashboard (V3 Consolidation) */}
        <div className="mb-6 animate-slide-up" style={{ animationDelay: '0.38s' }}>
          <PsychoanalyticDashboard />
        </div>

        {/* Autopoietic Metrics (Phase 22) */}
        <div className="mb-6 animate-slide-up" style={{ animationDelay: '0.4s' }}>
          <AutopoieticMetrics />
        </div>

        {/* Module Activity & Event Log */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="animate-slide-up" style={{ animationDelay: '0.4s' }}>
            <ModuleActivityHeatmap />
          </div>
          <div className="animate-slide-up" style={{ animationDelay: '0.45s' }}>
            <EventLog />
          </div>
        </div>

        {/* Baseline Comparison & Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="animate-slide-up" style={{ animationDelay: '0.5s' }}>
            <BaselineComparison />
          </div>
          <div className="animate-slide-up" style={{ animationDelay: '0.55s' }}>
            <ActionButtons />
          </div>
        </div>

        {/* Original Content Grid - Legacy Components */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Status and Tasks */}
          <div className="lg:col-span-2 space-y-6">
            <div className="animate-slide-up" style={{ animationDelay: '0.6s' }}>
              <DaemonStatus />
            </div>
            <div className="animate-slide-up" style={{ animationDelay: '0.62s' }}>
              <TribunalStatus />
            </div>
            <div className="animate-slide-up" style={{ animationDelay: '0.63s' }}>
              <TribunalMetricsVisual />
            </div>
            <div className="animate-slide-up" style={{ animationDelay: '0.65s' }}>
              <OmniMindSinthome />
            </div>
            <div className="animate-slide-up" style={{ animationDelay: '0.7s' }}>
              <AgentStatus />
            </div>
            <div className="animate-slide-up" style={{ animationDelay: '0.75s' }}>
              <TaskList />
            </div>
            <div className="animate-slide-up" style={{ animationDelay: '0.8s' }}>
              <DecisionsDashboard />
            </div>
          </div>

          {/* Right Column - Metrics, Controls, and Task Form */}
          <div className="space-y-6">
            <div className="animate-slide-up" style={{ animationDelay: '0.8s' }}>
              <SystemMetrics />
            </div>
            <div className="animate-slide-up" style={{ animationDelay: '0.85s' }}>
              <DaemonControls />
            </div>
            <div className="animate-slide-up" style={{ animationDelay: '0.9s' }}>
              <TaskForm />
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="glass-card border-t border-cyber-500/20 mt-12 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-gray-400 text-sm">
            <p className="flex items-center justify-center gap-2">
              <span className="text-gradient-cyber font-semibold">OmniMind</span>
              <span>Autonomous Agent System</span>
            </p>
            <p className="mt-1 flex items-center justify-center gap-2">
              <span className="inline-block w-2 h-2 rounded-full bg-neon-green animate-pulse-slow" style={{ boxShadow: '0 0 10px rgba(16, 185, 129, 0.8)' }} />
              24/7 Background Task Execution
            </p>
          </div>
        </div>
      </footer>

      {/* Conversation Assistant Panel */}
      <ConversationAssistant />
    </div>
  );
}
