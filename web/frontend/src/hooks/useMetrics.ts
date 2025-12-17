import { useCallback } from 'react';
import { useDaemonStore } from '../store/daemonStore';
import { apiService } from '../services/api';

/**
 * Custom hook for system metrics
 * Provides helpers for fetching daemon status and metrics
 */
export function useMetrics() {
  const { status, setStatus, setLoading, setError } = useDaemonStore();

  const fetchStatus = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const daemonStatus = await apiService.getDaemonStatus();
      setStatus(daemonStatus);
      return daemonStatus;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch status';
      setError(message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setStatus, setLoading, setError]);

  const metrics = status?.system_metrics;
  const isRunning = status?.running ?? false;
  const uptime = status?.uptime_seconds ?? 0;

  return {
    status,
    metrics,
    isRunning,
    uptime,
    fetchStatus,
  };
}
