import { useState, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { apiService } from '../services/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoadingCredentials, setIsLoadingCredentials] = useState(true);
  const login = useAuthStore((state) => state.login);

  // Try to load credentials from backend on component mount
  useEffect(() => {
    const loadCredentials = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/auth/credentials`);
        if (response.ok) {
          const data = await response.json();
          if (data.user && data.pass) {
            setUsername(data.user);
            setPassword(data.pass);
          }
        }
      } catch (err) {
        console.warn('Could not fetch credentials from backend:', err);
      } finally {
        setIsLoadingCredentials(false);
      }
    };

    loadCredentials();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validação básica
    if (!username || !password) {
      setError('Por favor, preencha usuário e senha');
      return;
    }

    try {
      // Configurar credenciais antes de testar
      apiService.setCredentials(username, password);

      // Testar conexão com backend primeiro (endpoint público)
      try {
        const healthCheck = await fetch(`${API_BASE_URL}/health/`);
        if (!healthCheck.ok) {
          throw new Error('Backend não está respondendo');
        }
      } catch (healthErr) {
        setError('Backend não está disponível. Verifique se o servidor está rodando.');
        console.error('Health check failed:', healthErr);
        return;
      }

      // Testar autenticação com endpoint protegido
      try {
        await apiService.getDaemonStatus();
        // Se chegou aqui, autenticação funcionou
        login(username, password);
      } catch (authErr) {
        // Erro específico de autenticação
        if (authErr instanceof Error && authErr.message.includes('401')) {
          setError('Credenciais inválidas. Verifique usuário e senha.');
        } else {
          setError(`Erro de autenticação: ${authErr instanceof Error ? authErr.message : 'Erro desconhecido'}`);
        }
        console.error('Authentication error:', authErr);
      }
    } catch (err) {
      setError(`Erro ao fazer login: ${err instanceof Error ? err.message : 'Erro desconhecido'}`);
      console.error('Login error:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-gray-800 rounded-lg shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">🧠 OmniMind</h1>
          <p className="text-gray-400">Dashboard Login</p>
        </div>

        {isLoadingCredentials && (
          <div className="text-center mb-4">
            <p className="text-sm text-gray-400">Loading credentials...</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-300 mb-2">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          {error && (
            <div className="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
          >
            Login
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-400">
          <p>Credentials are auto-loaded from:</p>
          <code className="text-xs bg-gray-700 px-2 py-1 rounded mt-1 inline-block">
            config/dashboard_auth.json
          </code>
        </div>
      </div>
    </div>
  );
}

