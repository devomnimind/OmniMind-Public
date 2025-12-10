import { useState, useRef, useEffect } from 'react';
import { useDaemonStore } from '../store/daemonStore';
import { apiService } from '../services/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  suggestedActions?: string[];
}

interface ConversationState {
  messages: Message[];
  isLoading: boolean;
  isOpen: boolean;
}

/**
 * Conversation Assistant Panel
 *
 * Full-featured chat interface for natural conversations with OmniMind
 * Supports:
 * - Multi-turn conversations
 * - Task suggestions
 * - Command recommendations
 * - Real-time streaming responses
 */
export function ConversationAssistant() {
  const [state, setState] = useState<ConversationState>({
    messages: [
      {
        id: '0',
        role: 'assistant',
        content: '👋 Olá! Sou o Assistente OmniMind. Como posso ajudar você hoje?',
        timestamp: new Date(),
        suggestedActions: [
          'Ver status do sistema',
          'Listar tarefas ativas',
          'Verificar consciência',
          'Iniciar nova tarefa'
        ]
      }
    ],
    isLoading: false,
    isOpen: false,
  });

  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const status = useDaemonStore((state) => state.status);

  // Auto-scroll para última mensagem
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [state.messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  /**
   * Processar comando do usuário
   */
  const processUserInput = async (userMessage: string) => {
    if (!userMessage.trim()) return;

    // Adicionar mensagem do usuário
    const userMsgId = Date.now().toString();
    const newUserMessage: Message = {
      id: userMsgId,
      role: 'user',
      content: userMessage,
      timestamp: new Date(),
    };

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, newUserMessage],
      isLoading: true,
    }));

    setInput('');

    try {
      // Chamar backend com contexto do sistema
      const data = await apiService.post('/api/omnimind/chat', {
        message: userMessage,
        context: {
          system_metrics: status?.system_metrics,
          daemon_running: status?.running,
          task_count: status?.task_count,
          consciousness_metrics: status?.consciousness_metrics,
        }
      });

      const assistantResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'Desculpe, não consegui processar sua solicitação.',
        timestamp: new Date(),
        suggestedActions: data.suggested_actions,
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantResponse],
        isLoading: false,
      }));

    } catch (error) {
      console.error('Error calling assistant:', error);

      // Fallback response se API não está disponível
      const fallbackResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '⚠️ Desculpe, o assistente está temporariamente indisponível. Tente novamente em alguns momentos.',
        timestamp: new Date(),
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, fallbackResponse],
        isLoading: false,
      }));
    }

    scrollToBottom();
  };

  /**
   * Lidar com sugestões de ação
   */
  const handleSuggestedAction = (action: string) => {
    processUserInput(action);
  };

  /**
   * Renderizar mensagem individual
   */
  const renderMessage = (message: Message) => {
    const isUser = message.role === 'user';
    return (
      <div
        key={message.id}
        className={`flex gap-4 mb-4 animate-slide-up ${
          isUser ? 'justify-end' : 'justify-start'
        }`}
      >
        {!isUser && (
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center text-white text-sm font-bold">
            🧠
          </div>
        )}

        <div
          className={`max-w-md lg:max-w-lg xl:max-w-2xl px-4 py-3 rounded-lg ${
            isUser
              ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-br-none'
              : 'bg-gray-700/50 text-gray-100 rounded-bl-none border border-gray-600/50'
          }`}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
          <span className="text-xs opacity-70 mt-1 block">
            {message.timestamp.toLocaleTimeString('pt-BR', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>

        {isUser && (
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center text-white text-sm font-bold">
            👤
          </div>
        )}
      </div>
    );
  };

  /**
   * Renderizar sugestões de ações
   */
  const renderSuggestedActions = (actions: string[] | undefined) => {
    if (!actions || actions.length === 0) return null;

    return (
      <div className="flex flex-wrap gap-2 mt-4 pt-3 border-t border-gray-600/30">
        {actions.map((action, idx) => (
          <button
            key={idx}
            onClick={() => handleSuggestedAction(action)}
            className="text-xs px-3 py-1.5 rounded-full bg-gray-700/50 hover:bg-gray-600 text-gray-300 hover:text-gray-100 border border-gray-600/50 hover:border-gray-500 transition-all duration-200 cursor-pointer hover:shadow-md"
          >
            {action}
          </button>
        ))}
      </div>
    );
  };

  // Não renderizar se fechado
  if (!state.isOpen) {
    return (
      <button
        onClick={() => setState(prev => ({ ...prev, isOpen: true }))}
        className="fixed bottom-4 right-4 w-16 h-16 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white rounded-full shadow-2xl z-40 flex items-center justify-center text-2xl transition-all hover:scale-110"
        title="Abrir Assistente OmniMind"
      >
        💬
      </button>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 w-96 h-[600px] flex flex-col bg-gray-800 rounded-lg border border-gray-700 shadow-2xl z-40">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700 bg-gradient-to-r from-gray-800 to-gray-750">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
          <h3 className="text-white font-semibold">🤖 Assistente OmniMind</h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setState(prev => ({ ...prev, isOpen: !prev.isOpen }))}
            className="text-gray-400 hover:text-gray-200 transition-colors px-2 py-1 rounded hover:bg-gray-700"
            title={state.isOpen ? 'Minimizar' : 'Expandir'}
          >
            {state.isOpen ? '−' : '+'}
          </button>
          <button
            onClick={() => setState(prev => ({ ...prev, isOpen: false }))}
            className="text-gray-400 hover:text-red-400 transition-colors px-2 py-1 rounded hover:bg-gray-700"
            title="Fechar"
          >
            ×
          </button>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {state.messages.map((msg) => (
          <div key={msg.id}>
            {renderMessage(msg)}
            {msg.suggestedActions && renderSuggestedActions(msg.suggestedActions)}
          </div>
        ))}

        {state.isLoading && (
          <div className="flex gap-2 items-center py-2">
            <div className="flex gap-1">
              <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
            <span className="text-xs text-gray-400">Assistente está pensando...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-700 bg-gray-750">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                processUserInput(input);
              }
            }}
            placeholder="Faça uma pergunta ou dê um comando..."
            className="flex-1 bg-gray-700 text-white text-sm rounded px-3 py-2 border border-gray-600 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 placeholder-gray-500 transition-all"
            disabled={state.isLoading}
          />
          <button
            onClick={() => processUserInput(input)}
            disabled={state.isLoading || !input.trim()}
            className="px-3 py-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white rounded font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg"
          >
            {state.isLoading ? '...' : '📤'}
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Dica: Use linguagem natural ou comandos. Ex: "listar tarefas", "qual meu status?" ou "iniciar análise"
        </p>
      </div>
    </div>
  );
}
