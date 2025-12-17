import { useAuthStore } from './store/authStore';
import { Login } from './components/Login';
import { Dashboard } from './components/Dashboard';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ToastContainer } from './components/ToastContainer';

function App() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  // Auto-login removido para garantir segurança (Soberania Local)
  // O usuário deve sempre fazer login com as credenciais geradas pelo backend

  return (
    <ErrorBoundary>
      <ToastContainer />
      {isAuthenticated ? <Dashboard /> : <Login />}
    </ErrorBoundary>
  );
}

export default App;
