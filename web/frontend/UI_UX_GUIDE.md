# 🎨 OmniMind DevBrain UI/UX Guide

## Overview

OmniMind features a **futuristic, sleek, and elegant DevBrain-inspired interface** designed for professional AI system monitoring and control. This guide documents the design system, components, and user experience features.

---

## 🌈 Design System

### Color Palette

#### Cyber Blue (Primary)
- **cyber-500**: `#0080ff` - Primary brand color
- **cyber-400**: `#1a94ff` - Interactive elements
- **cyber-600**: `#0066cc` - Hover states
- Usage: Primary buttons, links, focus states, brand identity

#### Neon Accents
- **neon-purple**: `#a855f7` - Secondary accent
- **neon-pink**: `#ec4899` - Error/warning states
- **neon-cyan**: `#06b6d4` - Information
- **neon-green**: `#10b981` - Success states
- **neon-yellow**: `#f59e0b` - Warning states
- **neon-red**: `#ef4444` - Critical alerts

#### Dark Background
- **dark-300**: `#0a0a0a` - Main background
- **dark-200**: `#0f0f0f` - Secondary background
- **dark-100**: `#141414` - Card backgrounds

### Typography

- **Font Family**: Inter, -apple-system, BlinkMacSystemFont, Segoe UI
- **Headings**: Bold, gradient text effects
- **Body**: Regular weight, high contrast for readability
- **Code**: Monospace for technical data

### Spacing & Layout

- **Grid System**: Max-width 7xl (80rem) container
- **Gaps**: 1rem (4), 1.5rem (6), 2rem (8)
- **Padding**: Consistent 1rem-1.5rem padding in cards
- **Border Radius**: 0.5rem (rounded-lg), 0.75rem (rounded-xl)

---

## 🧩 Component Library

### Glass Cards (`.glass-card`)

Glassmorphism effect with backdrop blur and subtle borders.

```tsx
<div className="glass-card p-6">
  <h2>Card Title</h2>
  <p>Content</p>
</div>
```

**Variants:**
- `.glass-card-hover` - Interactive hover effects
- `.metric-card` - Cards with gradient top border

### Buttons

#### Neon Button (`.btn-neon`)
Primary action buttons with gradient background and glow effect.

```tsx
<button className="btn-neon">
  Primary Action
</button>
```

#### Outline Neon (`.btn-outline-neon`)
Secondary buttons with border and subtle hover effects.

```tsx
<button className="btn-outline-neon">
  Secondary Action
</button>
```

### Status Indicators

#### Online Status
```tsx
<div className="status-online">
  <span>System Online</span>
</div>
```

#### Badges
- `.badge-cyber` - Primary information
- `.badge-success` - Success states
- `.badge-warning` - Warning states
- `.badge-error` - Error states

### Form Inputs

#### Cyber Input (`.input-cyber`)
```tsx
<input 
  type="text" 
  className="input-cyber" 
  placeholder="Enter value..."
/>
```

Features:
- Dark background with subtle border
- Cyber blue focus glow
- Smooth transitions

---

## 🎭 Advanced Components

### 1. Real-time Analytics (`RealtimeAnalytics.tsx`)

**Features:**
- Live CPU and memory usage monitoring
- Active task and agent counters
- Performance trend visualization
- Activity indicators with status colors
- WebSocket-powered real-time updates

**Usage:**
```tsx
import { RealtimeAnalytics } from './components/RealtimeAnalytics';

<RealtimeAnalytics />
```

**Data Flow:**
1. Listens to `metrics_update` WebSocket events
2. Updates analytics data in real-time
3. Displays last 30 data points
4. Color-coded thresholds (green → yellow → red)

### 2. Workflow Visualization (`WorkflowVisualization.tsx`)

**Features:**
- Interactive process flow diagrams
- Node-based workflow representation
- Real-time status updates per node
- Task dependency visualization
- Agent assignment display
- Scan line animation for active nodes

**Usage:**
```tsx
import { WorkflowVisualization } from './components/WorkflowVisualization';

<WorkflowVisualization />
```

**Node States:**
- **Pending**: Gray, clock icon
- **Running**: Cyber blue, animated spinner, scan effect
- **Completed**: Green, checkmark icon
- **Failed**: Red, X icon

### 3. Notification Center (`NotificationCenter.tsx`)

**Features:**
- Multi-channel notification system
- In-app notifications with unread count
- Email notification integration (backend)
- Webhook notification support
- Customizable notification preferences
- Real-time WebSocket notifications

**Usage:**
```tsx
import { NotificationCenter } from './components/NotificationCenter';

<NotificationCenter />
```

**Notification Types:**
- Task Complete
- Task Failed
- Agent Error
- System Alert

**Channels:**
- In-app (always enabled)
- Email (configurable)
- Webhook (configurable with custom URL)

---

## 🎨 Visual Effects

### Animations

#### Slide Up (`.animate-slide-up`)
Elements slide up from bottom with fade-in.

```tsx
<div className="animate-slide-up">Content</div>
```

#### Glow Effect (`.animate-glow`)
Pulsing glow effect for active elements.

```tsx
<div className="animate-glow">Glowing Element</div>
```

#### Pulse (`.animate-pulse-slow`)
Slow pulsing for status indicators.

```tsx
<span className="animate-pulse-slow">●</span>
```

#### Scan Line (`.scan-line`)
Sci-fi scan effect for active states.

```tsx
<div className="scan-line">
  Content with scan effect
</div>
```

### Gradients

#### Text Gradients
```tsx
<h1 className="text-gradient-cyber">Gradient Heading</h1>
<p className="text-gradient-neon">Neon Text</p>
```

#### Background Gradients
```tsx
<div className="bg-gradient-cyber">Cyber Gradient</div>
<div className="bg-gradient-neon">Neon Gradient</div>
```

### Effects

#### Cyber Grid Background
```tsx
<div className="cyber-grid">
  Content on grid
</div>
```

#### Hover Lift
```tsx
<div className="hover-lift">
  Card that lifts on hover
</div>
```

---

## ♿ Accessibility Features

### Keyboard Navigation
- All interactive elements are keyboard accessible
- Visible focus indicators (`.focus-cyber`)
- Logical tab order throughout application

### Screen Reader Support
- ARIA labels on all buttons and controls
- Semantic HTML structure
- Live regions for dynamic content updates
- Status announcements for state changes

### Color Contrast
- All text meets WCAG AA standards (4.5:1 minimum)
- High contrast mode support via `prefers-contrast`
- Information not conveyed by color alone

### Motion Preferences
- Respects `prefers-reduced-motion`
- All animations can be disabled
- Fallback to instant state changes

**See [ACCESSIBILITY.md](./ACCESSIBILITY.md) for full compliance details.**

---

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

### Grid Layout
```tsx
// Desktop: 2/3 + 1/3 split
<div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
  <div className="lg:col-span-2">
    Main content
  </div>
  <div>
    Sidebar
  </div>
</div>
```

### Mobile Optimizations
- Stacked layouts on mobile
- Touch-friendly button sizes (min 44x44px)
- Collapsible navigation
- Swipe gestures supported

---

## 🎯 User Experience Patterns

### Loading States
```tsx
// Spinner
<div className="spinner-cyber" />

// Skeleton loading
<DashboardSkeleton />
```

### Empty States
```tsx
<div className="glass-card p-12 text-center">
  <div className="w-16 h-16 rounded-full bg-cyber-500/20 mb-4">
    <Icon />
  </div>
  <p className="text-gray-400">No items to display</p>
</div>
```

### Error States
```tsx
<div className="badge-error">
  Error occurred
</div>
```

### Success States
```tsx
<div className="badge-success">
  Operation completed
</div>
```

---

## 🚀 Performance

### Optimizations
- CSS animations using GPU acceleration
- Debounced WebSocket updates
- Lazy loading for heavy components
- Optimized re-renders with React.memo
- Efficient state management with Zustand

### Best Practices
1. Use CSS transforms for animations (not top/left)
2. Limit number of animated elements simultaneously
3. Use will-change sparingly for critical animations
4. Implement virtual scrolling for long lists
5. Optimize images and SVGs

---

## 🎨 Theming

### Custom Colors
Add custom colors in `tailwind.config.js`:

```js
theme: {
  extend: {
    colors: {
      'custom-color': '#hexcode',
    },
  },
}
```

### Custom Animations
Add animations in `index.css`:

```css
@keyframes customAnimation {
  0% { /* start state */ }
  100% { /* end state */ }
}

.animate-custom {
  animation: customAnimation 1s ease-in-out;
}
```

---

## 📚 Component Examples

### Metric Card
```tsx
<div className="metric-card hover-lift">
  <div className="flex items-center justify-between mb-3">
    <span className="text-gray-400 text-sm">CPU Usage</span>
    <span className="text-2xl font-bold text-neon-green">45%</span>
  </div>
  <div className="w-full h-2 bg-dark-100 rounded-full">
    <div className="h-full bg-gradient-to-r from-neon-green to-green-700" 
         style={{ width: '45%' }} />
  </div>
</div>
```

### Status Indicator
```tsx
<div className="flex items-center gap-2">
  <span className="w-2 h-2 rounded-full bg-neon-green animate-pulse-slow" 
        style={{ boxShadow: '0 0 10px rgba(16, 185, 129, 0.8)' }} />
  <span className="text-sm text-gray-400">System Online</span>
</div>
```

### Interactive Button
```tsx
<button 
  className="btn-neon focus-cyber"
  onClick={handleClick}
  aria-label="Execute action"
>
  <span className="flex items-center gap-2">
    <Icon />
    Execute
  </span>
</button>
```

---

## 🔧 Development

### Running the Frontend
```bash
cd web/frontend
npm install
npm run dev
```

### Building for Production
```bash
npm run build
npm run preview
```

### Linting
```bash
npm run lint
```

---

## 📝 Style Guide Summary

### Do's ✅
- Use glass-card for containers
- Apply cyber color scheme consistently
- Include ARIA labels on all interactive elements
- Use semantic HTML
- Implement responsive design
- Test with reduced motion
- Provide loading states
- Use consistent spacing

### Don'ts ❌
- Don't use color as the only indicator
- Don't nest animations excessively
- Don't skip accessibility features
- Don't use inline styles (use Tailwind classes)
- Don't forget mobile optimization
- Don't ignore keyboard navigation
- Don't use low contrast colors

---

## 🎉 Credits

**Design Inspiration**: DevBrain futuristic aesthetic
**Color Palette**: Cyber punk meets professional
**Typography**: Modern sans-serif for clarity
**Animations**: Subtle sci-fi influences

**Framework**: React + TypeScript + Tailwind CSS
**Icons**: Heroicons (outline)
**State Management**: Zustand
**Build Tool**: Vite
