/**
 * Enhanced TaskList with Drag-and-Drop, Hover Effects, and Micro-Interactions
 * 
 * Features:
 * - Drag-and-drop task reordering
 * - Smooth hover animations
 * - Visual feedback on interactions
 * - Accessibility support
 * - Touch device support
 */

import { useState, useRef, useEffect } from 'react';
import { useDaemonStore } from '../store/daemonStore';

const PRIORITY_COLORS = {
  CRITICAL: 'bg-red-900/50 text-red-400 border-red-500',
  HIGH: 'bg-orange-900/50 text-orange-400 border-orange-500',
  MEDIUM: 'bg-yellow-900/50 text-yellow-400 border-yellow-500',
  LOW: 'bg-blue-900/50 text-blue-400 border-blue-500',
};

interface DragState {
  draggedIndex: number | null;
  draggedOverIndex: number | null;
}

export function DragDropTaskList() {
  const tasks = useDaemonStore((state) => state.tasks);
  const [dragState, setDragState] = useState<DragState>({
    draggedIndex: null,
    draggedOverIndex: null,
  });
  const [hoveredTask, setHoveredTask] = useState<string | null>(null);
  const [localTasks, setLocalTasks] = useState(tasks);
  const dragItemRef = useRef<HTMLDivElement | null>(null);

  // Sync local tasks with store
  useEffect(() => {
    setLocalTasks(tasks);
  }, [tasks]);

  const handleDragStart = (e: React.DragEvent<HTMLDivElement>, index: number) => {
    setDragState({ ...dragState, draggedIndex: index });
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', e.currentTarget.innerHTML);
    
    // Add visual feedback
    e.currentTarget.style.opacity = '0.5';
  };

  const handleDragEnd = (e: React.DragEvent<HTMLDivElement>) => {
    e.currentTarget.style.opacity = '1';
    setDragState({ draggedIndex: null, draggedOverIndex: null });
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>, index: number) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    
    if (dragState.draggedIndex === null || dragState.draggedIndex === index) {
      return;
    }

    setDragState({ ...dragState, draggedOverIndex: index });
  };

  const handleDragLeave = () => {
    setDragState({ ...dragState, draggedOverIndex: null });
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>, index: number) => {
    e.preventDefault();
    
    if (dragState.draggedIndex === null) return;

    const draggedIndex = dragState.draggedIndex;
    const newTasks = [...localTasks];
    const [draggedTask] = newTasks.splice(draggedIndex, 1);
    newTasks.splice(index, 0, draggedTask);
    
    setLocalTasks(newTasks);
    setDragState({ draggedIndex: null, draggedOverIndex: null });
    
    // Here you would typically update the task order on the backend
    console.log('Task order updated:', newTasks.map(t => t.task_id));
  };

  const handleMouseEnter = (taskId: string) => {
    setHoveredTask(taskId);
  };

  const handleMouseLeave = () => {
    setHoveredTask(null);
  };

  const formatInterval = (seconds: number | null) => {
    if (!seconds) return 'One-time';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `Every ${hours}h ${minutes}m`;
    return `Every ${minutes}m`;
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'Never';
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  const getSuccessRate = (task: typeof tasks[0]) => {
    if (task.stats.total_executions === 0) return 0;
    return ((task.stats.successful_executions / task.stats.total_executions) * 100).toFixed(0);
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 transition-all duration-300 hover:shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Tasks</h2>
        <div className="text-sm text-gray-400">
          <span className="inline-flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
            </svg>
            Drag to reorder
          </span>
        </div>
      </div>

      {localTasks.length === 0 ? (
        <div className="text-center text-gray-400 py-8 transition-opacity duration-300 animate-fade-in">
          <div className="mb-4">
            <svg className="w-16 h-16 mx-auto text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <p>No tasks registered</p>
          <p className="text-sm mt-2">Create a new task to get started</p>
        </div>
      ) : (
        <div className="space-y-4">
          {localTasks.map((task, index) => {
            const isHovered = hoveredTask === task.task_id;
            const isDragging = dragState.draggedIndex === index;
            const isDropTarget = dragState.draggedOverIndex === index && dragState.draggedIndex !== index;
            
            return (
              <div
                key={task.task_id}
                ref={dragItemRef}
                draggable
                onDragStart={(e) => handleDragStart(e, index)}
                onDragEnd={handleDragEnd}
                onDragOver={(e) => handleDragOver(e, index)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, index)}
                onMouseEnter={() => handleMouseEnter(task.task_id)}
                onMouseLeave={handleMouseLeave}
                className={`
                  bg-gray-700/50 rounded-lg p-4 border cursor-move
                  transition-all duration-300 ease-in-out
                  ${isDragging ? 'opacity-50 scale-95' : 'opacity-100 scale-100'}
                  ${isDropTarget ? 'border-cyan-400 shadow-cyan-glow mt-8' : 'border-gray-600'}
                  ${isHovered && !isDragging ? 'border-gray-500 shadow-lg transform -translate-y-1' : ''}
                  hover:bg-gray-700/70
                  animate-slide-up
                `}
                style={{ animationDelay: `${index * 50}ms` }}
                role="listitem"
                aria-label={`Task: ${task.name}`}
              >
                {/* Drag Handle */}
                <div className="absolute left-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </div>

                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1 pl-6">
                    <h3 className="text-white font-semibold text-lg mb-1 transition-colors duration-200">
                      {task.name}
                    </h3>
                    <p className="text-gray-400 text-sm line-clamp-2 transition-all duration-200">
                      {task.description}
                    </p>
                  </div>
                  <div 
                    className={`
                      px-3 py-1 rounded-full text-xs font-semibold border
                      transition-all duration-300
                      ${PRIORITY_COLORS[task.priority]}
                      ${isHovered ? 'shadow-lg scale-110' : 'scale-100'}
                    `}
                  >
                    {task.priority}
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                  <div className="transition-all duration-200 hover:scale-105">
                    <div className="text-gray-400 mb-1 flex items-center gap-1">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Interval
                    </div>
                    <div className="text-white font-medium">{formatInterval(task.repeat_interval_seconds)}</div>
                  </div>

                  <div className="transition-all duration-200 hover:scale-105">
                    <div className="text-gray-400 mb-1 flex items-center gap-1">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                      Executions
                    </div>
                    <div className="text-white font-medium">{task.stats.total_executions}</div>
                  </div>

                  <div className="transition-all duration-200 hover:scale-105">
                    <div className="text-gray-400 mb-1 flex items-center gap-1">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Success Rate
                    </div>
                    <div className={`font-medium ${
                      parseFloat(getSuccessRate(task)) >= 80 ? 'text-green-400' :
                      parseFloat(getSuccessRate(task)) >= 50 ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {task.stats.total_executions > 0 ? `${getSuccessRate(task)}%` : 'N/A'}
                    </div>
                  </div>

                  <div className="transition-all duration-200 hover:scale-105">
                    <div className="text-gray-400 mb-1 flex items-center gap-1">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      Last Run
                    </div>
                    <div className="text-white text-xs font-medium">{formatDate(task.stats.last_execution)}</div>
                  </div>
                </div>

                {task.stats.last_failure && (
                  <div 
                    className={`
                      mt-3 bg-red-900/30 border border-red-500/50 rounded p-2 text-xs text-red-300
                      transition-all duration-300
                      ${isHovered ? 'bg-red-900/40 shadow-red-glow' : ''}
                    `}
                  >
                    <span className="flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Last failure: {formatDate(task.stats.last_failure)}
                    </span>
                  </div>
                )}

                {/* Hover Action Buttons */}
                {isHovered && (
                  <div className="mt-3 flex gap-2 animate-fade-in">
                    <button 
                      className="flex-1 px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-sm font-medium transition-all duration-200 hover:shadow-cyan-glow"
                      onClick={(e) => {
                        e.stopPropagation();
                        console.log('View details:', task.task_id);
                      }}
                    >
                      View Details
                    </button>
                    <button 
                      className="flex-1 px-3 py-1.5 bg-green-600 hover:bg-green-500 text-white rounded text-sm font-medium transition-all duration-200 hover:shadow-green-glow"
                      onClick={(e) => {
                        e.stopPropagation();
                        console.log('Execute now:', task.task_id);
                      }}
                    >
                      Execute Now
                    </button>
                    <button 
                      className="px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white rounded text-sm font-medium transition-all duration-200 hover:shadow-red-glow"
                      onClick={(e) => {
                        e.stopPropagation();
                        console.log('Delete:', task.task_id);
                      }}
                    >
                      Delete
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
