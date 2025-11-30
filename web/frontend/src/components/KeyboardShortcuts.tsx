/**
 * Global Keyboard Shortcuts Manager for OmniMind
 * 
 * Provides:
 * - Command palette (Ctrl+K)
 * - Global shortcuts
 * - Contextual shortcuts
 * - Shortcut help modal
 */

import { useEffect, useState } from 'react';

export interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  meta?: boolean;
  description: string;
  action: () => void;
  category?: string;
  enabled?: boolean;
}

export interface ShortcutCategory {
  name: string;
  shortcuts: KeyboardShortcut[];
}

class KeyboardShortcutManager {
  private shortcuts: Map<string, KeyboardShortcut> = new Map();
  private listeners: Set<(event: KeyboardEvent) => void> = new Set();

  constructor() {
    this.handleKeyDown = this.handleKeyDown.bind(this);
    if (typeof window !== 'undefined') {
      window.addEventListener('keydown', this.handleKeyDown);
    }
  }

  register(id: string, shortcut: KeyboardShortcut): void {
    this.shortcuts.set(id, shortcut);
  }

  unregister(id: string): void {
    this.shortcuts.delete(id);
  }

  private handleKeyDown(event: KeyboardEvent): void {
    // Check if we're in an input field
    const target = event.target as HTMLElement;
    const isInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName);
    
    for (const [, shortcut] of this.shortcuts.entries()) {
      if (shortcut.enabled === false) continue;

      // Skip shortcuts when in input fields unless explicitly allowed
      if (isInput && !shortcut.key.startsWith('Escape')) continue;

      const matches =
        event.key.toLowerCase() === shortcut.key.toLowerCase() &&
        event.ctrlKey === (shortcut.ctrl || false) &&
        event.shiftKey === (shortcut.shift || false) &&
        event.altKey === (shortcut.alt || false) &&
        event.metaKey === (shortcut.meta || false);

      if (matches) {
        event.preventDefault();
        shortcut.action();
        break;
      }
    }
  }

  getShortcuts(): Map<string, KeyboardShortcut> {
    return new Map(this.shortcuts);
  }

  getShortcutsByCategory(): ShortcutCategory[] {
    const categorized = new Map<string, KeyboardShortcut[]>();
    
    for (const [, shortcut] of this.shortcuts.entries()) {
      const category = shortcut.category || 'General';
      if (!categorized.has(category)) {
        categorized.set(category, []);
      }
      categorized.get(category)!.push(shortcut);
    }

    return Array.from(categorized.entries()).map(([name, shortcuts]) => ({
      name,
      shortcuts,
    }));
  }

  destroy(): void {
    if (typeof window !== 'undefined') {
      window.removeEventListener('keydown', this.handleKeyDown);
    }
    this.shortcuts.clear();
    this.listeners.clear();
  }
}

// Global singleton instance
const globalShortcutManager = new KeyboardShortcutManager();

/**
 * Hook to register keyboard shortcuts
 */
export function useKeyboardShortcut(
  id: string,
  shortcut: KeyboardShortcut,
  deps: any[] = []
): void {
  useEffect(() => {
    globalShortcutManager.register(id, shortcut);

    return () => {
      globalShortcutManager.unregister(id);
    };
  }, [id, ...deps]);
}

/**
 * Hook to get all registered shortcuts
 */
export function useKeyboardShortcuts(): ShortcutCategory[] {
  const [categories, setCategories] = useState<ShortcutCategory[]>([]);

  useEffect(() => {
    const updateShortcuts = () => {
      setCategories(globalShortcutManager.getShortcutsByCategory());
    };

    updateShortcuts();

    // Update every second to catch new registrations
    const interval = setInterval(updateShortcuts, 1000);

    return () => clearInterval(interval);
  }, []);

  return categories;
}

/**
 * Command Palette Component
 */
interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const [search, setSearch] = useState('');
  const categories = useKeyboardShortcuts();

  useEffect(() => {
    if (!isOpen) {
      setSearch('');
    }
  }, [isOpen]);

  const filteredCategories = categories
    .map((category) => ({
      ...category,
      shortcuts: category.shortcuts.filter(
        (shortcut) =>
          shortcut.description.toLowerCase().includes(search.toLowerCase()) ||
          shortcut.key.toLowerCase().includes(search.toLowerCase())
      ),
    }))
    .filter((category) => category.shortcuts.length > 0);

  if (!isOpen) return null;

  const formatShortcut = (shortcut: KeyboardShortcut): string => {
    const parts: string[] = [];
    if (shortcut.ctrl) parts.push('Ctrl');
    if (shortcut.shift) parts.push('Shift');
    if (shortcut.alt) parts.push('Alt');
    if (shortcut.meta) parts.push('⌘');
    parts.push(shortcut.key.toUpperCase());
    return parts.join('+');
  };

  return (
    <div
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-start justify-center pt-20 animate-fade-in"
      onClick={onClose}
    >
      <div
        className="bg-dark-100 rounded-lg shadow-2xl w-full max-w-2xl border border-cyber-500/30 animate-slide-up"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input */}
        <div className="p-4 border-b border-cyber-500/20">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search commands..."
            className="w-full bg-dark-200 border border-cyber-500/30 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyber-500 transition-colors"
            autoFocus
          />
        </div>

        {/* Command List */}
        <div className="max-h-96 overflow-y-auto p-4">
          {filteredCategories.length === 0 ? (
            <div className="text-center text-gray-400 py-8">
              No commands found
            </div>
          ) : (
            filteredCategories.map((category) => (
              <div key={category.name} className="mb-6 last:mb-0">
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                  {category.name}
                </h3>
                <div className="space-y-1">
                  {category.shortcuts.map((shortcut, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        shortcut.action();
                        onClose();
                      }}
                      className="w-full flex items-center justify-between px-4 py-3 bg-dark-200/50 hover:bg-dark-200 rounded-lg transition-colors text-left group"
                    >
                      <span className="text-white group-hover:text-cyber-400 transition-colors">
                        {shortcut.description}
                      </span>
                      <kbd className="px-2 py-1 bg-dark-300 border border-cyber-500/30 rounded text-xs font-mono text-gray-400 group-hover:border-cyber-500/50 group-hover:text-cyber-400 transition-colors">
                        {formatShortcut(shortcut)}
                      </kbd>
                    </button>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-cyber-500/20 flex items-center justify-between text-xs text-gray-400">
          <span>Press ESC to close</span>
          <span>{filteredCategories.reduce((sum, cat) => sum + cat.shortcuts.length, 0)} commands</span>
        </div>
      </div>
    </div>
  );
}

/**
 * Keyboard Shortcuts Help Modal
 */
interface ShortcutHelpProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ShortcutHelp({ isOpen, onClose }: ShortcutHelpProps) {
  const categories = useKeyboardShortcuts();

  if (!isOpen) return null;

  const formatShortcut = (shortcut: KeyboardShortcut): string => {
    const parts: string[] = [];
    if (shortcut.ctrl) parts.push('Ctrl');
    if (shortcut.shift) parts.push('Shift');
    if (shortcut.alt) parts.push('Alt');
    if (shortcut.meta) parts.push('⌘');
    parts.push(shortcut.key.toUpperCase());
    return parts.join('+');
  };

  return (
    <div
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in"
      onClick={onClose}
    >
      <div
        className="bg-dark-100 rounded-lg shadow-2xl w-full max-w-4xl max-h-[80vh] overflow-hidden border border-cyber-500/30"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-6 border-b border-cyber-500/20">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-white">Keyboard Shortcuts</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors"
              aria-label="Close"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="overflow-y-auto max-h-[60vh] p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {categories.map((category) => (
              <div key={category.name} className="space-y-3">
                <h3 className="text-sm font-semibold text-cyber-400 uppercase tracking-wider">
                  {category.name}
                </h3>
                <div className="space-y-2">
                  {category.shortcuts.map((shortcut, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between text-sm"
                    >
                      <span className="text-gray-300">{shortcut.description}</span>
                      <kbd className="px-2 py-1 bg-dark-200 border border-cyber-500/30 rounded font-mono text-xs text-gray-400">
                        {formatShortcut(shortcut)}
                      </kbd>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="p-4 border-t border-cyber-500/20 text-center text-sm text-gray-400">
          Press <kbd className="px-2 py-1 bg-dark-200 border border-cyber-500/30 rounded font-mono text-xs">?</kbd> to toggle this help
        </div>
      </div>
    </div>
  );
}

export { globalShortcutManager };
