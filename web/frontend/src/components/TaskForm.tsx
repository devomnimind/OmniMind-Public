import { useState, FormEvent } from 'react';
import { apiService } from '../services/api';
import { toast } from '../store/toastStore';
import type { AddTaskRequest } from '../types/daemon';

export function TaskForm() {
  const [formData, setFormData] = useState<AddTaskRequest>({
    task_id: '',
    name: '',
    description: '',
    code: '',
    priority: 'MEDIUM',
    repeat_interval_seconds: undefined,
    timeout_seconds: 300,
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.task_id || !formData.name || !formData.description || !formData.code) {
      setMessage({ type: 'error', text: 'Please fill in all required fields' });
      return;
    }

    // Validate task_id format (alphanumeric and underscores only)
    if (!/^[a-z0-9_]+$/.test(formData.task_id)) {
      setMessage({ 
        type: 'error', 
        text: 'Task ID must contain only lowercase letters, numbers, and underscores' 
      });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const result = await apiService.addTask(formData);
      toast.success(result.message);
      
      // Reset form on success
      setFormData({
        task_id: '',
        name: '',
        description: '',
        code: '',
        priority: 'MEDIUM',
        repeat_interval_seconds: undefined,
        timeout_seconds: 300,
      });
      setShowAdvanced(false);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to add task';
      toast.error(errorMessage);
      setMessage({ type: 'error', text: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof AddTaskRequest, value: string | number | undefined) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-2xl font-bold text-white mb-6">Create New Task</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Task ID */}
        <div>
          <label htmlFor="task_id" className="block text-sm font-medium text-gray-300 mb-2">
            Task ID <span className="text-red-400">*</span>
          </label>
          <input
            id="task_id"
            type="text"
            value={formData.task_id}
            onChange={(e) => handleChange('task_id', e.target.value)}
            placeholder="e.g., backup_database"
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            required
          />
          <p className="mt-1 text-xs text-gray-400">Lowercase letters, numbers, and underscores only</p>
        </div>

        {/* Task Name */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2">
            Task Name <span className="text-red-400">*</span>
          </label>
          <input
            id="name"
            type="text"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder="e.g., Daily Database Backup"
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            required
          />
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-2">
            Description <span className="text-red-400">*</span>
          </label>
          <textarea
            id="description"
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            placeholder="Describe what this task does..."
            rows={2}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            required
          />
        </div>

        {/* Priority */}
        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-300 mb-2">
            Priority
          </label>
          <select
            id="priority"
            value={formData.priority}
            onChange={(e) => handleChange('priority', e.target.value as AddTaskRequest['priority'])}
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          >
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>

        {/* Python Code */}
        <div>
          <label htmlFor="code" className="block text-sm font-medium text-gray-300 mb-2">
            Python Code <span className="text-red-400">*</span>
          </label>
          <textarea
            id="code"
            value={formData.code}
            onChange={(e) => handleChange('code', e.target.value)}
            placeholder={`def execute():\n    # Your code here\n    return {"status": "completed"}`}
            rows={8}
            className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white font-mono text-sm placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            required
          />
          <p className="mt-1 text-xs text-gray-400">Must define an execute() function</p>
        </div>

        {/* Advanced Options Toggle */}
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors"
        >
          {showAdvanced ? '▼' : '▶'} Advanced Options
        </button>

        {/* Advanced Options */}
        {showAdvanced && (
          <div className="space-y-4 pl-4 border-l-2 border-gray-600">
            {/* Repeat Interval */}
            <div>
              <label htmlFor="repeat_interval" className="block text-sm font-medium text-gray-300 mb-2">
                Repeat Interval (seconds)
              </label>
              <input
                id="repeat_interval"
                type="number"
                min="0"
                value={formData.repeat_interval_seconds || ''}
                onChange={(e) => handleChange('repeat_interval_seconds', e.target.value ? parseInt(e.target.value) : undefined)}
                placeholder="Leave empty for one-time execution"
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              />
              <p className="mt-1 text-xs text-gray-400">E.g., 3600 for hourly, 86400 for daily</p>
            </div>

            {/* Timeout */}
            <div>
              <label htmlFor="timeout" className="block text-sm font-medium text-gray-300 mb-2">
                Timeout (seconds)
              </label>
              <input
                id="timeout"
                type="number"
                min="1"
                value={formData.timeout_seconds}
                onChange={(e) => handleChange('timeout_seconds', parseInt(e.target.value))}
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              />
              <p className="mt-1 text-xs text-gray-400">Maximum execution time (default: 300)</p>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="pt-4">
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            {loading ? 'Adding Task...' : 'Add Task'}
          </button>
        </div>

        {/* Status Message */}
        {message && (
          <div
            className={`p-4 rounded-lg ${
              message.type === 'error'
                ? 'bg-red-900/50 border border-red-500 text-red-200'
                : 'bg-green-900/50 border border-green-500 text-green-200'
            }`}
          >
            {message.text}
          </div>
        )}
      </form>

      {/* Code Examples */}
      <div className="mt-6 pt-6 border-t border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-3">Code Examples</h3>
        <div className="space-y-3 text-sm">
          <details className="bg-gray-700/50 rounded p-3 cursor-pointer">
            <summary className="font-medium text-gray-300">Simple Task</summary>
            <pre className="mt-2 text-xs text-gray-400 overflow-x-auto">
{`def execute():
    print("Hello from custom task!")
    return {"status": "completed"}`}
            </pre>
          </details>

          <details className="bg-gray-700/50 rounded p-3 cursor-pointer">
            <summary className="font-medium text-gray-300">File System Task</summary>
            <pre className="mt-2 text-xs text-gray-400 overflow-x-auto">
{`def execute():
    import os
    workspace = os.getenv("OMNIMIND_WORKSPACE", ".")
    file_count = len(os.listdir(workspace))
    return {
        "status": "completed",
        "file_count": file_count
    }`}
            </pre>
          </details>

          <details className="bg-gray-700/50 rounded p-3 cursor-pointer">
            <summary className="font-medium text-gray-300">Async Task</summary>
            <pre className="mt-2 text-xs text-gray-400 overflow-x-auto">
{`async def execute():
    import asyncio
    await asyncio.sleep(1)
    return {"status": "completed"}`}
            </pre>
          </details>
        </div>
      </div>
    </div>
  );
}
