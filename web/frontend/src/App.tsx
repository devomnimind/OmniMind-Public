import { useEffect, useState } from 'react';
import { useAuthStore } from './store/authStore';
import { Login } from './components/Login';
import { Dashboard } from './components/Dashboard';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ToastContainer } from './components/ToastContainer';
import { apiService } from './services/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const login = useAuthStore((state) => state.login);
  const [isLoading, setIsLoading] = useState(true);

  // Carregar credenciais automaticamente na inicialização
  useEffect(() => {
    const autoLoginWithBackendCredentials = async () => {
      try {
        // 1. Verificar se já está autenticado (localStorage)
        if (isAuthenticated) {
          setIsLoading(false);
          return;
        }

        // 2. Tentar carregar credenciais do backend (endpoint público)
        const response = await fetch(`${API_BASE_URL}/auth/credentials`);
        if (!response.ok) {
          console.warn('Could not fetch credentials from /auth/credentials:', response.status);
          setIsLoading(false);
          return;
        }

        const data = await response.json();
        if (!data.user || !data.pass) {
          console.warn('Credentials from backend are incomplete:', data);
          setIsLoading(false);
          return;
        }

        // 3. Configurar credenciais no apiService
        apiService.setCredentials(data.user, data.pass);

        // 4. Testar se as credenciais funcionam (health check simples)
        try {
          const healthResponse = await fetch(`${API_BASE_URL}/health/`);
          if (!healthResponse.ok) {
            console.warn('Health check failed, but continuing with credentials');
          }
        } catch (err) {
          console.warn('Could not perform health check:', err);
        }

        // 5. Fazer login automaticamente (sem mostrar tela de login)
        login(data.user, data.pass);
        console.log('[App] ✅ Auto-login successful com credenciais do backend');
      } catch (err) {
        console.error('[App] Erro ao fazer auto-login:', err);
      } finally {
        setIsLoading(false);
      }
    };

    autoLoginWithBackendCredentials();
  }, [isAuthenticated, login]);

  if (isLoading) {
    return (
      <ErrorBoundary>
        <div className="min-h-screen bg-gray-900 flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-white mb-4">🧠 OmniMind</h1>
            <div className="animate-pulse">
              <p className="text-gray-400">Carregando credenciais do backend...</p>
            </div>
          </div>
        </div>
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <ToastContainer />
      {isAuthenticated ? <Dashboard /> : <Login />}
    </ErrorBoundary>
  );
}

export default App;
