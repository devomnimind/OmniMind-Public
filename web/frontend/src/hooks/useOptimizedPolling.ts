import { useEffect, useRef, useCallback } from 'react';
import { useAuthStore } from '../store/authStore';

/**
 * Hook centralizado para polling otimizado
 *
 * Prioridades:
 * - 'high': 10-15s (métricas críticas)
 * - 'medium': 30s (métricas importantes)
 * - 'low': 60s+ (métricas secundárias)
 */
export function useOptimizedPolling<T>(
  fetchFn: () => Promise<T>,
  options: {
    interval?: number;
    priority?: 'high' | 'medium' | 'low';
    enabled?: boolean;
    onSuccess?: (data: T) => void;
    onError?: (error: Error) => void;
  } = {}
) {
  const {
    interval,
    priority = 'medium',
    enabled = true,
    onSuccess,
    onError,
  } = options;

  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const intervalRef = useRef<number | null>(null);
  const lastFetchRef = useRef<number>(0);
  const cacheRef = useRef<{ data: T; timestamp: number } | null>(null);
  const CACHE_TTL = 5000; // 5 segundos de cache

  // Calcular intervalo baseado na prioridade
  const getInterval = useCallback(() => {
    if (interval) return interval;

    const baseIntervals = {
      high: 15000,    // 15s para métricas críticas
      medium: 30000,  // 30s para métricas importantes
      low: 60000,     // 60s para métricas secundárias
    };

    return baseIntervals[priority];
  }, [interval, priority]);

  const fetchWithCache = useCallback(async () => {
    // Verificar cache primeiro
    if (cacheRef.current) {
      const cacheAge = Date.now() - cacheRef.current.timestamp;
      if (cacheAge < CACHE_TTL) {
        return cacheRef.current.data;
      }
    }

    // Throttling: evitar múltiplas requisições simultâneas
    const now = Date.now();
    const timeSinceLastFetch = now - lastFetchRef.current;
    const minInterval = getInterval() * 0.5; // Mínimo 50% do intervalo

    if (timeSinceLastFetch < minInterval) {
      // Usar cache se disponível
      if (cacheRef.current) {
        return cacheRef.current.data;
      }
      return null;
    }

    try {
      lastFetchRef.current = now;
      const data = await fetchFn();

      // Atualizar cache
      cacheRef.current = { data, timestamp: now };

      if (onSuccess) {
        onSuccess(data);
      }

      return data;
    } catch (error) {
      console.error(`[useOptimizedPolling] Erro ao buscar dados:`, error);

      if (onError) {
        onError(error instanceof Error ? error : new Error(String(error)));
      }

      // Retornar cache em caso de erro se disponível
      if (cacheRef.current) {
        return cacheRef.current.data;
      }

      throw error;
    }
  }, [fetchFn, getInterval, onSuccess, onError]);

  useEffect(() => {
    // Não fazer polling se não estiver autenticado ou desabilitado
    if (!enabled || !isAuthenticated) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    // Fetch inicial
    fetchWithCache().catch(() => {
      // Erro já foi tratado no fetchWithCache
    });

    // Configurar intervalo
    const pollInterval = getInterval();
    intervalRef.current = window.setInterval(() => {
      fetchWithCache().catch(() => {
        // Erro já foi tratado no fetchWithCache
      });
    }, pollInterval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [enabled, isAuthenticated, fetchWithCache, getInterval]);

  return {
    refetch: fetchWithCache,
    clearCache: () => {
      cacheRef.current = null;
    },
  };
}

