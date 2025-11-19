import { useCallback } from 'react';
import { useDaemonStore } from '../store/daemonStore';
import { apiService } from '../services/api';
import type { AddTaskRequest } from '../types/daemon';

/**
 * Custom hook for task management
 * Provides helpers for fetching and creating tasks
 */
export function useTasks() {
  const { tasks, activeTasks, setTasks, addTask, updateTask, setLoading, setError } = useDaemonStore();

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const fetchedTasks = await apiService.getDaemonTasks();
      setTasks(fetchedTasks);
      return fetchedTasks;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch tasks';
      setError(message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [setTasks, setLoading, setError]);

  const createTask = useCallback(async (taskData: AddTaskRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiService.addTask(taskData);
      // Refresh task list after creation
      await fetchTasks();
      return result;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create task';
      setError(message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [fetchTasks, setLoading, setError]);

  return {
    tasks,
    activeTasks,
    fetchTasks,
    createTask,
    addTask,
    updateTask,
  };
}
