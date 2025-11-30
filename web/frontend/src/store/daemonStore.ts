import { create } from 'zustand';
import type { DaemonStatus, DaemonTask, Agent, Task } from '../types/daemon';

interface DaemonState {
  status: DaemonStatus | null;
  tasks: DaemonTask[];
  agents: Agent[];
  activeTasks: Task[];
  loading: boolean;
  error: string | null;
  isConnected: boolean;
  setStatus: (status: DaemonStatus) => void;
  setTasks: (tasks: DaemonTask[]) => void;
  setAgents: (agents: Agent[]) => void;
  setActiveTasks: (tasks: Task[]) => void;
  addTask: (task: Task) => void;
  updateTask: (id: string, updates: Partial<Task>) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setConnected: (connected: boolean) => void;
}

export const useDaemonStore = create<DaemonState>((set) => ({
  status: null,
  tasks: [],
  agents: [],
  activeTasks: [],
  loading: false,
  error: null,
  isConnected: false,
  setStatus: (status) => set({ status }),
  setTasks: (tasks) => set({ tasks }),
  setAgents: (agents) => set({ agents }),
  setActiveTasks: (tasks) => set({ activeTasks: tasks }),
  addTask: (task) => set((state) => ({ activeTasks: [...state.activeTasks, task] })),
  updateTask: (id, updates) =>
    set((state) => ({
      activeTasks: state.activeTasks.map((task) =>
        task.task_id === id ? { ...task, ...updates } : task
      ),
    })),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setConnected: (connected) => set({ isConnected: connected }),
}));
