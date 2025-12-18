import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiService } from '../services/api';

interface AuthState {
  isAuthenticated: boolean;
  username: string;
  login: (username: string, password: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      username: '',
      login: (username: string, password: string) => {
        // Guardar no apiService
        apiService.setCredentials(username, password);

        // Guardar no localStorage para recuperação posterior
        localStorage.setItem('omnimind_user', username);
        localStorage.setItem('omnimind_pass', password);

        // Atualizar estado
        set({ isAuthenticated: true, username });
        console.log('[authStore] Login successful, credentials saved');
      },
      logout: () => {
        // Limpar apiService
        apiService.setCredentials('', '');

        // Limpar localStorage
        localStorage.removeItem('omnimind_user');
        localStorage.removeItem('omnimind_pass');

        // Limpar estado
        set({ isAuthenticated: false, username: '' });
        console.log('[authStore] Logout successful, credentials cleared');
      },
    }),
    {
      name: 'omnimind-auth',
      // Sincronizar com apiService ao carregar do localStorage
      onRehydrateStorage: () => (state) => {
        if (state?.username && state?.isAuthenticated) {
          const pass = localStorage.getItem('omnimind_pass');
          if (pass) {
            apiService.setCredentials(state.username, pass);
            console.log('[authStore] Restored credentials from localStorage on hydration');
          }
        }
      },
    }
  )
);
