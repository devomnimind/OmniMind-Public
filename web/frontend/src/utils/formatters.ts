/**
 * Utility functions for formatting and data manipulation
 */

/**
 * Format seconds to human-readable duration
 * @example formatDuration(3665) => "1h 1m"
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (hours >= 24) {
    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;
    return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`;
  }
  
  if (hours > 0) {
    return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`;
  }
  
  return `${minutes}m`;
}

/**
 * Format interval in seconds to human-readable string
 * @example formatInterval(3600) => "Every 1h"
 */
export function formatInterval(seconds: number | null): string {
  if (!seconds) return 'One-time';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (hours > 0) {
    return minutes > 0 ? `Every ${hours}h ${minutes}m` : `Every ${hours}h`;
  }
  
  return `Every ${minutes}m`;
}

/**
 * Format ISO timestamp to relative time
 * @example formatRelativeTime("2024-01-01T00:00:00Z") => "2h ago"
 */
export function formatRelativeTime(timestamp?: string): string {
  if (!timestamp) return 'Never';
  
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const seconds = Math.floor(diff / 1000);
  
  if (seconds < 0) return 'Just now';
  if (seconds < 60) return `${seconds}s ago`;
  
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  
  const weeks = Math.floor(days / 7);
  if (weeks < 4) return `${weeks}w ago`;
  
  const months = Math.floor(days / 30);
  return `${months}mo ago`;
}

/**
 * Format ISO timestamp to locale date string
 * @example formatDate("2024-01-01T00:00:00Z") => "1/1/2024, 12:00:00 AM"
 */
export function formatDate(timestamp?: string): string {
  if (!timestamp) return 'Never';
  
  const date = new Date(timestamp);
  return date.toLocaleString();
}

/**
 * Format bytes to human-readable size
 * @example formatBytes(1024) => "1 KB"
 */
export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
}

/**
 * Format percentage with optional decimal places
 * @example formatPercent(0.5678, 1) => "56.8%"
 */
export function formatPercent(value: number, decimals: number = 0): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Truncate string to max length with ellipsis
 * @example truncate("Hello World", 8) => "Hello..."
 */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return `${str.substring(0, maxLength)}...`;
}

/**
 * Debounce function calls
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: number | null = null;
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait) as unknown as number;
  };
}

/**
 * Throttle function calls
 */
export function throttle<T extends (...args: unknown[]) => unknown>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Generate unique ID
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Validate task ID format (lowercase, numbers, underscores)
 */
export function isValidTaskId(taskId: string): boolean {
  return /^[a-z0-9_]+$/.test(taskId);
}

/**
 * Get color class for usage percentage
 */
export function getUsageColor(percent: number): string {
  if (percent > 80) return 'bg-red-500';
  if (percent > 60) return 'bg-yellow-500';
  return 'bg-green-500';
}

/**
 * Get color class for priority
 */
export function getPriorityColor(priority: string): string {
  switch (priority) {
    case 'CRITICAL':
      return 'bg-red-900/50 text-red-400 border-red-500';
    case 'HIGH':
      return 'bg-orange-900/50 text-orange-400 border-orange-500';
    case 'MEDIUM':
      return 'bg-yellow-900/50 text-yellow-400 border-yellow-500';
    case 'LOW':
      return 'bg-blue-900/50 text-blue-400 border-blue-500';
    default:
      return 'bg-gray-900/50 text-gray-400 border-gray-500';
  }
}

/**
 * Calculate success rate percentage
 */
export function calculateSuccessRate(
  successful: number,
  total: number
): number {
  if (total === 0) return 0;
  return (successful / total) * 100;
}
