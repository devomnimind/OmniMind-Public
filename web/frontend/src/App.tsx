import { useEffect } from 'react';
import { useAuthStore } from './store/authStore';
import { Login } from './components/Login';
import { Dashboard } from './components/Dashboard';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ToastContainer } from './components/ToastContainer';
import { apiService } from './services/api';

function App() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const login = useAuthStore((state) => state.login);

  useEffect(() => {
    const defaultUser = import.meta.env.VITE_DASHBOARD_USER;
    const defaultPass = import.meta.env.VITE_DASHBOARD_PASS;

    if (
      typeof defaultUser === 'string' &&
      defaultUser &&
      typeof defaultPass === 'string' &&
      defaultPass
    ) {
      apiService.setCredentials(defaultUser, defaultPass);
      if (!isAuthenticated) {
        apiService
          .getDaemonStatus()
          .then(() => login(defaultUser, defaultPass))
          .catch((err) => {
            console.warn('Falha no login automático', err);
          });
      }
    }
  }, [isAuthenticated, login]);

  return (
    <ErrorBoundary>
      <ToastContainer />
      {isAuthenticated ? <Dashboard /> : <Login />}
    </ErrorBoundary>
  );
}

export default App;
