import { useEffect, useState, useRef } from 'react';
import { apiService } from '../services/api';

interface BackendHealth {
  isOnline: boolean;
  consecutiveFailures: number;
  lastCheck: number;
}

/**
 * Hook para verificar saúde do backend e evitar polling excessivo quando offline.
 *
 * Implementa circuit breaker pattern:
 * - Após 3 falhas consecutivas, marca backend como offline
 * - Aumenta intervalo de verificação quando offline
 * - Retorna ao polling normal quando backend volta online
 */
export function useBackendHealth() {
  const [health, setHealth] = useState<BackendHealth>({
    isOnline: true,
    consecutiveFailures: 0,
    lastCheck: Date.now(),
  });

  const checkIntervalRef = useRef<number | null>(null);
  const isCheckingRef = useRef(false);

  const checkBackendHealth = async () => {
    // Evitar múltiplas verificações simultâneas
    if (isCheckingRef.current) return;
    isCheckingRef.current = true;

    try {
      // Tentar fazer uma requisição simples ao backend
      await apiService.get('/health/');

      // Backend está online
      setHealth(() => ({
        isOnline: true,
        consecutiveFailures: 0,
        lastCheck: Date.now(),
      }));
    } catch (error) {
      // Backend está offline ou com erro
      setHealth((prev) => {
        const newFailures = prev.consecutiveFailures + 1;
        const isOnline = newFailures < 3; // Circuit breaker: 3 falhas = offline

        return {
          isOnline,
          consecutiveFailures: newFailures,
          lastCheck: Date.now(),
        };
      });
    } finally {
      isCheckingRef.current = false;
    }
  };

  useEffect(() => {
    // Verificação inicial
    checkBackendHealth();

    // Configurar intervalo inicial (aumentado para dar mais tempo de carregamento)
    const initialInterval = health.isOnline ? 30000 : 60000; // 30s quando online, 60s quando offline
    checkIntervalRef.current = window.setInterval(() => {
      checkBackendHealth();
    }, initialInterval);

    return () => {
      if (checkIntervalRef.current) {
        clearInterval(checkIntervalRef.current);
      }
    };
  }, []); // Apenas uma vez no mount

  // Reconfigurar intervalo quando health.isOnline mudar
  useEffect(() => {
    if (checkIntervalRef.current) {
      clearInterval(checkIntervalRef.current);
    }

    const currentInterval = health.isOnline ? 30000 : 60000; // 30s quando online, 60s quando offline
    checkIntervalRef.current = window.setInterval(() => {
      checkBackendHealth();
    }, currentInterval);

    return () => {
      if (checkIntervalRef.current) {
        clearInterval(checkIntervalRef.current);
      }
    };
  }, [health.isOnline]);

  return {
    isOnline: health.isOnline,
    consecutiveFailures: health.consecutiveFailures,
    lastCheck: health.lastCheck,
    checkNow: checkBackendHealth,
  };
}

