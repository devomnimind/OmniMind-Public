import { useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface WorkflowNode {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  agent?: string;
  dependencies: string[];
}

interface WorkflowData {
  task_id: string;
  task_name: string;
  nodes: WorkflowNode[];
  current_node?: string;
}

export function WorkflowVisualization() {
  const { lastMessage } = useWebSocket();
  const [workflows, setWorkflows] = useState<WorkflowData[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowData | null>(null);

  useEffect(() => {
    // Only update workflows if WebSocket sends real task data
    if (lastMessage?.type === 'task_update' && lastMessage.data) {
      const data = lastMessage.data as { task_id?: string; name?: string; nodes?: any[] } | undefined;
      
      // Only create workflow if we have real task data with nodes
      if (data?.task_id && data?.nodes && Array.isArray(data.nodes)) {
        const workflow: WorkflowData = {
          task_id: data.task_id,
          task_name: data.name || 'Task',
          nodes: data.nodes,
          current_node: (data as any).current_node,
        };

        setWorkflows((prev) => {
          const existing = prev.find((w) => w.task_id === workflow.task_id);
          if (existing) {
            return prev.map((w) => (w.task_id === workflow.task_id ? workflow : w));
          }
          return [...prev, workflow];
        });

        if (!selectedWorkflow) {
          setSelectedWorkflow(workflow);
        }
      }
    }
  }, [lastMessage, selectedWorkflow]);

  const getNodeStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-neon-green/20 border-neon-green text-neon-green';
      case 'running':
        return 'bg-cyber-500/20 border-cyber-500 text-cyber-400 animate-glow';
      case 'failed':
        return 'bg-neon-red/20 border-neon-red text-neon-red';
      default:
        return 'bg-gray-700/20 border-gray-600 text-gray-400';
    }
  };

  const getNodeIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        );
      case 'running':
        return (
          <div className="spinner-cyber w-5 h-5 border-2" />
        );
      case 'failed':
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  const renderFlowDiagram = (workflow: WorkflowData) => {
    return (
      <div className="space-y-8 p-6">
        {workflow.nodes.map((node, index) => (
          <div key={node.id} className="relative">
            {/* Connection Line to Previous Node */}
            {index > 0 && (
              <div className="absolute left-1/2 -top-8 w-0.5 h-8 bg-gradient-to-b from-cyber-500/50 to-cyber-500/20" />
            )}

            {/* Node Card */}
            <div
              className={`glass-card-hover p-4 border-2 ${getNodeStatusColor(node.status)} relative overflow-hidden`}
            >
              {/* Scan Line Effect for Running Nodes */}
              {node.status === 'running' && (
                <div className="scan-line absolute inset-0 pointer-events-none" />
              )}

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${getNodeStatusColor(node.status)}`}>
                    {getNodeIcon(node.status)}
                  </div>
                  <div>
                    <h4 className="font-semibold text-white">{node.name}</h4>
                    {node.agent && (
                      <p className="text-sm text-gray-400">Agent: {node.agent}</p>
                    )}
                  </div>
                </div>

                {/* Status Badge */}
                <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  node.status === 'completed' ? 'badge-success' :
                  node.status === 'running' ? 'badge-cyber' :
                  node.status === 'failed' ? 'badge-error' :
                  'bg-gray-700/20 text-gray-400 border border-gray-600'
                }`}>
                  {node.status.toUpperCase()}
                </div>
              </div>

              {/* Progress Indicator for Running Nodes */}
              {node.status === 'running' && (
                <div className="mt-3">
                  <div className="w-full h-1 bg-dark-100 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-cyber-500 to-neon-purple animate-pulse w-2/3" />
                  </div>
                </div>
              )}
            </div>

            {/* Branching Indicator */}
            {node.dependencies.length > 1 && (
              <div className="absolute -top-10 left-1/2 transform -translate-x-1/2 text-xs text-gray-500">
                Merge Point
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="glass-card p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gradient-cyber">Workflow Visualization</h2>
        <div className="badge-cyber">
          Interactive Flow
        </div>
      </div>

      {/* Workflow Selector */}
      {workflows.length > 0 && (
        <div className="flex gap-2 overflow-x-auto pb-2">
          {workflows.map((workflow) => (
            <button
              key={workflow.task_id}
              onClick={() => setSelectedWorkflow(workflow)}
              className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-all ${
                selectedWorkflow?.task_id === workflow.task_id
                  ? 'bg-gradient-cyber text-white shadow-neon-md'
                  : 'glass-card-hover text-gray-400'
              }`}
            >
              {workflow.task_name}
            </button>
          ))}
        </div>
      )}

      {/* Flow Diagram */}
      {selectedWorkflow ? (
        <div className="glass-card">
          {renderFlowDiagram(selectedWorkflow)}
        </div>
      ) : (
        <div className="glass-card p-12 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-cyber-500/20 mb-4">
            <svg className="w-8 h-8 text-cyber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p className="text-gray-400">No active workflows to display</p>
          <p className="text-sm text-gray-500 mt-2">Start a task to see the workflow visualization</p>
        </div>
      )}

      {/* Workflow Statistics */}
      {selectedWorkflow && (
        <div className="grid grid-cols-4 gap-4">
          <div className="glass-card p-4 text-center">
            <p className="text-sm text-gray-400">Total Steps</p>
            <p className="text-2xl font-bold text-white mt-1">{selectedWorkflow.nodes.length}</p>
          </div>
          <div className="glass-card p-4 text-center">
            <p className="text-sm text-gray-400">Completed</p>
            <p className="text-2xl font-bold text-neon-green mt-1">
              {selectedWorkflow.nodes.filter((n) => n.status === 'completed').length}
            </p>
          </div>
          <div className="glass-card p-4 text-center">
            <p className="text-sm text-gray-400">Running</p>
            <p className="text-2xl font-bold text-cyber-400 mt-1">
              {selectedWorkflow.nodes.filter((n) => n.status === 'running').length}
            </p>
          </div>
          <div className="glass-card p-4 text-center">
            <p className="text-sm text-gray-400">Pending</p>
            <p className="text-2xl font-bold text-gray-400 mt-1">
              {selectedWorkflow.nodes.filter((n) => n.status === 'pending').length}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
