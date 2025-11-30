/**
 * AgentCommunicationMonitor - Monitor de Comunicação Inter-Agentes
 * 
 * Componente React para visualização em tempo real de:
 * - Mensagens entre agentes
 * - Status de filas
 * - Métricas de comunicação
 * - Resolução de conflitos
 */

import React, { useEffect, useState } from 'react';
import { wsService } from '../services/websocket';
import { WebSocketMessage } from '../services/websocket';

interface AgentMessage {
  message_id: string;
  message_type: string;
  sender: string;
  recipient: string;
  payload: Record<string, unknown>;
  priority: string;
  timestamp: string;
}

interface QueueStats {
  agent_id: string;
  queue_size: number;
  subscriptions: string[];
}

interface ConflictResolution {
  conflict_id: string;
  agents_involved: string[];
  conflict_type: string;
  resolution: string;
  winner?: string;
  timestamp: string;
}

export const AgentCommunicationMonitor: React.FC = () => {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [queueStats, setQueueStats] = useState<QueueStats[]>([]);
  const [conflicts, setConflicts] = useState<ConflictResolution[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  useEffect(() => {
    // Subscribe to agent communication updates
    const unsubscribe = wsService.subscribe((message: WebSocketMessage) => {
      if (message.type === 'agent_message') {
        const agentMsg = message.data as AgentMessage;
        setMessages((prev) => [agentMsg, ...prev].slice(0, 50));
      } else if (message.type === 'queue_stats') {
        setQueueStats(message.data as QueueStats[]);
      } else if (message.type === 'conflict_resolution') {
        const conflict = message.data as ConflictResolution;
        setConflicts((prev) => [conflict, ...prev].slice(0, 20));
      }
    });

    return unsubscribe;
  }, []);

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'CRITICAL':
        return 'text-red-600 bg-red-100';
      case 'HIGH':
        return 'text-orange-600 bg-orange-100';
      case 'MEDIUM':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const filteredMessages = selectedAgent
    ? messages.filter(
        (msg) => msg.sender === selectedAgent || msg.recipient === selectedAgent
      )
    : messages;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          🔗 Agent Communication Monitor
        </h2>
        <p className="text-gray-600">
          Real-time monitoring of inter-agent messages and coordination
        </p>
      </div>

      {/* Queue Statistics */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">
          📊 Queue Statistics
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {queueStats.map((stat) => (
            <div
              key={stat.agent_id}
              className={`p-4 border rounded-lg cursor-pointer transition ${
                selectedAgent === stat.agent_id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-blue-300'
              }`}
              onClick={() =>
                setSelectedAgent(
                  selectedAgent === stat.agent_id ? null : stat.agent_id
                )
              }
            >
              <div className="font-semibold text-gray-800">{stat.agent_id}</div>
              <div className="text-2xl font-bold text-blue-600 my-2">
                {stat.queue_size}
              </div>
              <div className="text-sm text-gray-600">messages pending</div>
              <div className="mt-2 flex flex-wrap gap-1">
                {stat.subscriptions.map((sub) => (
                  <span
                    key={sub}
                    className="text-xs px-2 py-1 bg-gray-100 rounded"
                  >
                    {sub}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Conflicts */}
      {conflicts.length > 0 && (
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">
            ⚔️ Conflict Resolutions
          </h3>
          <div className="space-y-3">
            {conflicts.map((conflict) => (
              <div
                key={conflict.conflict_id}
                className="p-3 border border-yellow-200 bg-yellow-50 rounded-lg"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <span className="font-semibold text-yellow-800">
                      {conflict.conflict_type}
                    </span>
                    <div className="text-sm text-gray-600 mt-1">
                      Agents: {conflict.agents_involved.join(', ')}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-gray-500">
                      {new Date(conflict.timestamp).toLocaleTimeString()}
                    </div>
                    {conflict.winner && (
                      <div className="text-sm font-semibold text-green-600 mt-1">
                        Winner: {conflict.winner}
                      </div>
                    )}
                  </div>
                </div>
                <div className="text-sm text-gray-700 mt-2">
                  Resolution: {conflict.resolution}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Message Stream */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold text-gray-800">
            💬 Message Stream
          </h3>
          {selectedAgent && (
            <button
              onClick={() => setSelectedAgent(null)}
              className="px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded text-sm"
            >
              Clear Filter
            </button>
          )}
        </div>

        <div className="space-y-2 max-h-96 overflow-y-auto">
          {filteredMessages.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              No messages yet
            </div>
          ) : (
            filteredMessages.map((msg) => (
              <div
                key={msg.message_id}
                className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className={`text-xs px-2 py-1 rounded font-semibold ${getPriorityColor(
                          msg.priority
                        )}`}
                      >
                        {msg.priority}
                      </span>
                      <span className="text-sm font-mono text-gray-600">
                        {msg.message_type}
                      </span>
                    </div>
                    <div className="text-sm text-gray-700">
                      <span className="font-semibold">{msg.sender}</span>
                      <span className="mx-2">→</span>
                      <span className="font-semibold">{msg.recipient}</span>
                    </div>
                    <div className="mt-2 text-xs text-gray-600 bg-gray-50 p-2 rounded">
                      {JSON.stringify(msg.payload, null, 2)}
                    </div>
                  </div>
                  <div className="text-xs text-gray-500 ml-4">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
