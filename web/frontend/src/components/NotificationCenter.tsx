import { useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: Date;
  channels: ('in-app' | 'email' | 'webhook')[];
  read: boolean;
}

interface NotificationPreferences {
  email_enabled: boolean;
  webhook_enabled: boolean;
  webhook_url: string;
  notify_on_task_complete: boolean;
  notify_on_task_failed: boolean;
  notify_on_agent_error: boolean;
  notify_on_system_alert: boolean;
}

export function NotificationCenter() {
  const { lastMessage } = useWebSocket();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [showPanel, setShowPanel] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    email_enabled: false,
    webhook_enabled: false,
    webhook_url: '',
    notify_on_task_complete: true,
    notify_on_task_failed: true,
    notify_on_agent_error: true,
    notify_on_system_alert: true,
  });

  useEffect(() => {
    // Listen for notification events from WebSocket
    if (lastMessage) {
      let notification: Notification | null = null;

      switch (lastMessage.type) {
        case 'task_complete':
          if (preferences.notify_on_task_complete) {
            notification = {
              id: `notif-${Date.now()}`,
              type: 'success',
              title: 'Task Completed',
              message: `Task "${lastMessage.data?.name}" has completed successfully`,
              timestamp: new Date(),
              channels: ['in-app'],
              read: false,
            };
          }
          break;
        case 'task_failed':
          if (preferences.notify_on_task_failed) {
            notification = {
              id: `notif-${Date.now()}`,
              type: 'error',
              title: 'Task Failed',
              message: `Task "${lastMessage.data?.name}" has failed`,
              timestamp: new Date(),
              channels: ['in-app'],
              read: false,
            };
          }
          break;
        case 'agent_error':
          if (preferences.notify_on_agent_error) {
            notification = {
              id: `notif-${Date.now()}`,
              type: 'warning',
              title: 'Agent Error',
              message: `Agent "${lastMessage.data?.agent}" encountered an error`,
              timestamp: new Date(),
              channels: ['in-app'],
              read: false,
            };
          }
          break;
        case 'system_alert':
          if (preferences.notify_on_system_alert) {
            notification = {
              id: `notif-${Date.now()}`,
              type: 'warning',
              title: 'System Alert',
              message: lastMessage.data?.message || 'System alert received',
              timestamp: new Date(),
              channels: ['in-app'],
              read: false,
            };
          }
          break;
      }

      if (notification) {
        setNotifications((prev) => [notification!, ...prev]);
        
        // Send to additional channels if enabled
        if (preferences.email_enabled) {
          sendEmailNotification(notification);
        }
        if (preferences.webhook_enabled && preferences.webhook_url) {
          sendWebhookNotification(notification);
        }
      }
    }
  }, [lastMessage, preferences]);

  const sendEmailNotification = async (notification: Notification) => {
    // Mock email sending - in production, this would call the backend API
    console.log('Sending email notification:', notification);
  };

  const sendWebhookNotification = async (notification: Notification) => {
    // Mock webhook sending - in production, this would call the backend API
    if (preferences.webhook_url) {
      console.log('Sending webhook to:', preferences.webhook_url, notification);
    }
  };

  const markAsRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const clearAll = () => {
    setNotifications([]);
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return (
          <svg className="w-5 h-5 text-neon-green" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'error':
        return (
          <svg className="w-5 h-5 text-neon-red" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'warning':
        return (
          <svg className="w-5 h-5 text-neon-yellow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5 text-cyber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  return (
    <>
      {/* Notification Bell Button */}
      <button
        onClick={() => setShowPanel(!showPanel)}
        className="relative p-2 glass-card-hover rounded-lg focus-cyber"
        aria-label="Open notifications"
      >
        <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-neon-red rounded-full flex items-center justify-center text-xs font-bold text-white animate-pulse">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Panel */}
      {showPanel && (
        <div className="fixed top-16 right-4 w-96 max-h-[600px] glass-card border-2 border-cyber-500/20 shadow-cyber-glow z-50 animate-slide-down">
          <div className="p-4 border-b border-gray-700/50 flex items-center justify-between">
            <h3 className="text-lg font-bold text-gradient-cyber">Notifications</h3>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowPreferences(!showPreferences)}
                className="p-2 glass-card-hover rounded-lg text-gray-400 hover:text-white transition-colors focus-cyber"
                aria-label="Notification preferences"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
              <button
                onClick={() => setShowPanel(false)}
                className="p-2 glass-card-hover rounded-lg text-gray-400 hover:text-white transition-colors focus-cyber"
                aria-label="Close notifications"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Preferences Panel */}
          {showPreferences && (
            <div className="p-4 border-b border-gray-700/50 space-y-4 bg-dark-100/50">
              <h4 className="font-semibold text-white">Notification Preferences</h4>
              
              <label className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Email Notifications</span>
                <input
                  type="checkbox"
                  checked={preferences.email_enabled}
                  onChange={(e) => setPreferences({ ...preferences, email_enabled: e.target.checked })}
                  className="w-4 h-4 text-cyber-500 bg-dark-100 border-gray-600 rounded focus:ring-cyber-500"
                />
              </label>

              <label className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Webhook Notifications</span>
                <input
                  type="checkbox"
                  checked={preferences.webhook_enabled}
                  onChange={(e) => setPreferences({ ...preferences, webhook_enabled: e.target.checked })}
                  className="w-4 h-4 text-cyber-500 bg-dark-100 border-gray-600 rounded focus:ring-cyber-500"
                />
              </label>

              {preferences.webhook_enabled && (
                <input
                  type="url"
                  placeholder="Webhook URL"
                  value={preferences.webhook_url}
                  onChange={(e) => setPreferences({ ...preferences, webhook_url: e.target.value })}
                  className="input-cyber text-sm"
                />
              )}

              <div className="pt-2 border-t border-gray-700/50 space-y-2">
                <p className="text-xs text-gray-500">Notify me about:</p>
                {[
                  { key: 'notify_on_task_complete', label: 'Task Completions' },
                  { key: 'notify_on_task_failed', label: 'Task Failures' },
                  { key: 'notify_on_agent_error', label: 'Agent Errors' },
                  { key: 'notify_on_system_alert', label: 'System Alerts' },
                ].map(({ key, label }) => (
                  <label key={key} className="flex items-center justify-between">
                    <span className="text-xs text-gray-400">{label}</span>
                    <input
                      type="checkbox"
                      checked={preferences[key as keyof NotificationPreferences] as boolean}
                      onChange={(e) => setPreferences({ ...preferences, [key]: e.target.checked })}
                      className="w-3 h-3 text-cyber-500 bg-dark-100 border-gray-600 rounded focus:ring-cyber-500"
                    />
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          {notifications.length > 0 && (
            <div className="p-3 border-b border-gray-700/50 flex gap-2">
              <button
                onClick={markAllAsRead}
                className="flex-1 px-3 py-1 glass-card-hover text-sm text-gray-400 hover:text-white rounded transition-colors focus-cyber"
              >
                Mark All Read
              </button>
              <button
                onClick={clearAll}
                className="flex-1 px-3 py-1 glass-card-hover text-sm text-gray-400 hover:text-white rounded transition-colors focus-cyber"
              >
                Clear All
              </button>
            </div>
          )}

          {/* Notification List */}
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-8 text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-cyber-500/20 mb-3">
                  <svg className="w-6 h-6 text-cyber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                </div>
                <p className="text-sm text-gray-400">No notifications</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-700/50">
                {notifications.map((notif) => (
                  <div
                    key={notif.id}
                    className={`p-4 hover:bg-white/5 transition-colors cursor-pointer ${
                      !notif.read ? 'bg-cyber-500/5' : ''
                    }`}
                    onClick={() => markAsRead(notif.id)}
                  >
                    <div className="flex gap-3">
                      <div className="flex-shrink-0 mt-1">
                        {getNotificationIcon(notif.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <p className="font-semibold text-white text-sm">{notif.title}</p>
                          {!notif.read && (
                            <span className="flex-shrink-0 w-2 h-2 rounded-full bg-cyber-500 animate-pulse-slow" />
                          )}
                        </div>
                        <p className="text-sm text-gray-400 mt-1">{notif.message}</p>
                        <p className="text-xs text-gray-500 mt-2">
                          {notif.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
