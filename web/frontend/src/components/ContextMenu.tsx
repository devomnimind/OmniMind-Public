/**
 * Context Menu System for OmniMind
 * 
 * Provides intelligent right-click context menus with:
 * - Position-aware rendering
 * - Keyboard navigation
 * - Icons and shortcuts
 * - Nested submenus
 */

import { useState, useEffect, useRef, ReactNode } from 'react';

export interface ContextMenuItem {
  id: string;
  label: string;
  icon?: ReactNode;
  shortcut?: string;
  action?: () => void;
  disabled?: boolean;
  divider?: boolean;
  danger?: boolean;
  submenu?: ContextMenuItem[];
}

interface ContextMenuProps {
  items: ContextMenuItem[];
  x: number;
  y: number;
  onClose: () => void;
}

export function ContextMenu({ items, x, y, onClose }: ContextMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x, y });

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [onClose]);

  useEffect(() => {
    // Adjust position if menu would go off-screen
    if (menuRef.current) {
      const rect = menuRef.current.getBoundingClientRect();
      const windowWidth = window.innerWidth;
      const windowHeight = window.innerHeight;

      let adjustedX = x;
      let adjustedY = y;

      if (x + rect.width > windowWidth) {
        adjustedX = windowWidth - rect.width - 10;
      }

      if (y + rect.height > windowHeight) {
        adjustedY = windowHeight - rect.height - 10;
      }

      setPosition({ x: adjustedX, y: adjustedY });
    }
  }, [x, y]);

  const handleItemClick = (item: ContextMenuItem) => {
    if (item.disabled || item.divider) return;
    
    if (item.action) {
      item.action();
      onClose();
    }
  };

  return (
    <div
      ref={menuRef}
      className="fixed z-50 min-w-[200px] bg-dark-100 border border-cyber-500/30 rounded-lg shadow-2xl shadow-cyber-500/20 animate-scale-in"
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
      }}
    >
      <div className="py-2">
        {items.map((item, index) => {
          if (item.divider) {
            return (
              <div
                key={item.id || `divider-${index}`}
                className="h-px bg-cyber-500/20 my-2"
              />
            );
          }

          return (
            <button
              key={item.id}
              onClick={() => handleItemClick(item)}
              disabled={item.disabled}
              className={`
                w-full flex items-center justify-between px-4 py-2 text-left text-sm
                transition-colors
                ${item.disabled
                  ? 'text-gray-500 cursor-not-allowed'
                  : item.danger
                  ? 'text-red-400 hover:bg-red-900/20 hover:text-red-300'
                  : 'text-white hover:bg-cyber-500/10 hover:text-cyber-400'
                }
              `}
            >
              <div className="flex items-center gap-3">
                {item.icon && (
                  <span className="flex-shrink-0 w-4 h-4">{item.icon}</span>
                )}
                <span>{item.label}</span>
              </div>
              {item.shortcut && (
                <kbd className="ml-4 px-2 py-0.5 bg-dark-200 border border-cyber-500/30 rounded text-xs font-mono text-gray-400">
                  {item.shortcut}
                </kbd>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

/**
 * Hook to use context menu
 */
export function useContextMenu() {
  const [contextMenu, setContextMenu] = useState<{
    items: ContextMenuItem[];
    x: number;
    y: number;
  } | null>(null);

  const showContextMenu = (
    event: React.MouseEvent,
    items: ContextMenuItem[]
  ) => {
    event.preventDefault();
    setContextMenu({
      items,
      x: event.clientX,
      y: event.clientY,
    });
  };

  const closeContextMenu = () => {
    setContextMenu(null);
  };

  const ContextMenuComponent = contextMenu ? (
    <ContextMenu
      items={contextMenu.items}
      x={contextMenu.x}
      y={contextMenu.y}
      onClose={closeContextMenu}
    />
  ) : null;

  return {
    showContextMenu,
    closeContextMenu,
    ContextMenuComponent,
  };
}

/**
 * Auto-Save System
 */

interface AutoSaveOptions {
  key: string;
  delay?: number;
  storage?: 'local' | 'session';
}

export function useAutoSave<T>(
  data: T,
  options: AutoSaveOptions
): {
  savedData: T | null;
  isSaving: boolean;
  lastSaved: Date | null;
  clearSaved: () => void;
} {
  const { key, delay = 1000, storage = 'local' } = options;
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [savedData, setSavedData] = useState<T | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout>();

  const storageObject = storage === 'local' ? localStorage : sessionStorage;

  // Load saved data on mount
  useEffect(() => {
    try {
      const saved = storageObject.getItem(key);
      if (saved) {
        const parsed = JSON.parse(saved);
        setSavedData(parsed.data);
        setLastSaved(new Date(parsed.timestamp));
      }
    } catch (error) {
      console.error('Failed to load saved data:', error);
    }
  }, [key, storageObject]);

  // Auto-save data when it changes
  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    setIsSaving(true);

    timeoutRef.current = setTimeout(() => {
      try {
        const saveData = {
          data,
          timestamp: new Date().toISOString(),
        };
        storageObject.setItem(key, JSON.stringify(saveData));
        setLastSaved(new Date());
        setSavedData(data);
      } catch (error) {
        console.error('Failed to save data:', error);
      } finally {
        setIsSaving(false);
      }
    }, delay);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [data, key, delay, storageObject]);

  const clearSaved = () => {
    storageObject.removeItem(key);
    setSavedData(null);
    setLastSaved(null);
  };

  return {
    savedData,
    isSaving,
    lastSaved,
    clearSaved,
  };
}

/**
 * Auto-Save Indicator Component
 */
interface AutoSaveIndicatorProps {
  isSaving: boolean;
  lastSaved: Date | null;
}

export function AutoSaveIndicator({ isSaving, lastSaved }: AutoSaveIndicatorProps) {
  const [timeAgo, setTimeAgo] = useState('');

  useEffect(() => {
    const updateTimeAgo = () => {
      if (!lastSaved) {
        setTimeAgo('');
        return;
      }

      const seconds = Math.floor((Date.now() - lastSaved.getTime()) / 1000);

      if (seconds < 60) {
        setTimeAgo('just now');
      } else if (seconds < 3600) {
        const minutes = Math.floor(seconds / 60);
        setTimeAgo(`${minutes}m ago`);
      } else {
        const hours = Math.floor(seconds / 3600);
        setTimeAgo(`${hours}h ago`);
      }
    };

    updateTimeAgo();
    const interval = setInterval(updateTimeAgo, 10000); // Update every 10 seconds

    return () => clearInterval(interval);
  }, [lastSaved]);

  return (
    <div className="flex items-center gap-2 text-sm text-gray-400">
      {isSaving ? (
        <>
          <div className="w-4 h-4 border-2 border-cyber-500 border-t-transparent rounded-full animate-spin" />
          <span>Saving...</span>
        </>
      ) : lastSaved ? (
        <>
          <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
          <span>Saved {timeAgo}</span>
        </>
      ) : null}
    </div>
  );
}
