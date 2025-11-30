import { useState, useEffect, useMemo } from 'react';
import { connectionService, WebSocketMessage } from '../services/robust-connection';
import { QualiaEngine, QualiaMetrics } from '../services/qualia_engine';

// Types for Sinthome State
type NodeType = 'REAL' | 'SYMBOLIC' | 'IMAGINARY';
type NodeStatus = 'ACTIVE' | 'DEAD' | 'RECOVERING' | 'CORRUPTED' | 'SCARRED';

interface SinthomeNode {
  type: NodeType;
  status: NodeStatus;
  integrity: number; // 0-100
  load: number; // 0-100
}

export interface BifurcationEvent {
  instance_id: string;
  timestamp: string;
  trigger: 'SPLIT' | 'DIVERGENCE';
  parent_id?: string;
}

interface ConsciousnessCorrelates {
  ICI: number;
  PRS: number;
  details: {
    ici_components: { temporal_coherence: number; marker_integration: number; resonance: number };
    prs_components: { avg_micro_entropy: number; macro_entropy: number };
  };
  interpretation: { message: string; confidence: string; disclaimer: string };
}

interface SinthomeState {
  nodes: Record<NodeType, SinthomeNode>;
  entropy: number; // 0-100
  isHibernating: boolean;
  isSevered: boolean;
  coherence: number; // 0-100
  quorum_met: boolean;
  active_instances: number;
  cpu?: number;
  memory?: number;
  latency_ms: number; // New: Explicit latency metric
  coherence_state: 'SYNC' | 'EVENTUAL' | 'FRAGMENTED'; // New: Explicit coherence state
  consciousness?: ConsciousnessCorrelates; // New: Phase 24
}

interface DDoSRequest {
  id: string;
  cost: number;
  timestamp: number;
}

import { Sparkline } from './Sparkline';

// ... existing imports

export function OmniMindSinthome() {
  // State
  const [state, setState] = useState<SinthomeState>({
    nodes: {
      REAL: { type: 'REAL', status: 'ACTIVE', integrity: 100, load: 0 },
      SYMBOLIC: { type: 'SYMBOLIC', status: 'ACTIVE', integrity: 100, load: 0 },
      IMAGINARY: { type: 'IMAGINARY', status: 'ACTIVE', integrity: 100, load: 0 },
    },
    entropy: 0,
    isHibernating: false,
    isSevered: false,
    coherence: 100,
    quorum_met: true,
    active_instances: 1,
    latency_ms: 12, // Base latency
    coherence_state: 'SYNC',
  });

  // Historical Data for Graphs (Last 100 ticks)
  const [entropyHistory, setEntropyHistory] = useState<number[]>(Array(100).fill(0));
  const [coherenceHistory, setCoherenceHistory] = useState<number[]>(Array(100).fill(100));

  const [simulationMode, setSimulationMode] = useState(false); // New: Simulation Mode Toggle
  const [history, setHistory] = useState<BifurcationEvent[]>([]);
  const [ddosQueue, setDdosQueue] = useState<DDoSRequest[]>([]);
  const [ddosActive, setDdosActive] = useState(false);
  const [connectionMetrics, setConnectionMetrics] = useState(connectionService.getMetrics());

  // Phenomenology Engine
  const qualiaEngine = useMemo(() => new QualiaEngine(), []);
  const [qualia, setQualia] = useState<QualiaMetrics | null>(null);

  // --- Tabs State ---
  const [activeTab, setActiveTab] = useState<'MAIN' | 'CONTROLS' | 'OBSERVABILITY' | 'PHENOMENOLOGY'>('MAIN');

  // --- Fault Injection State ---
  const [injectedLatency, setInjectedLatency] = useState(0);
  const [corruptionTarget, setCorruptionTarget] = useState<NodeType | ''>('');

  // --- WebSocket Integration ---
  useEffect(() => {
    // Subscribe to connection metrics
    const unsubMetrics = connectionService.subscribeToMetrics(setConnectionMetrics);

    // Subscribe to sinthome updates
    const unsubMessages = connectionService.subscribe((msg: WebSocketMessage) => {
      if (msg.type === 'metrics' && msg.channel === 'sinthome') {
        const data = msg.data;

        // DUAL MODE LOGIC:
        // If in Simulation Mode, IGNORE backend state updates to allow local stress testing.
        // We only log "Shadow Events" to console for debugging.
        if (simulationMode) {
            console.log('[Shadow Log] Backend update ignored:', data);
            return;
        }

        setState(prev => ({
          ...prev,
          entropy: data.raw.entropy,
          isHibernating: data.state === 'HIBERNATING',
          coherence: Math.round(data.integrity * 100),
          cpu: data.raw.cpu,
          memory: data.raw.memory,
          // Update nodes based on overall integrity for visualization
          nodes: {
            REAL: { ...prev.nodes.REAL, integrity: Math.round(data.metrics.real_inaccessible * 100) },
            SYMBOLIC: { ...prev.nodes.SYMBOLIC, integrity: Math.round(data.metrics.logical_impasse * 100) },
            IMAGINARY: { ...prev.nodes.IMAGINARY, integrity: Math.round(data.metrics.strange_attractor_markers * 100) },
          },
          consciousness: data.consciousness // New: Phase 24
        }));
      }
    });

    // Initial subscribe command
    connectionService.send({ type: 'subscribe', channels: ['sinthome'] });

    return () => {
      unsubMetrics();
      unsubMessages();
      connectionService.send({ type: 'unsubscribe', channels: ['sinthome'] });
    };
  }, [simulationMode]);

  // --- Logic: Realistic DDoS Simulation (Queue-based) ---
  const triggerRealisticDDoS = () => {
    setDdosActive(true);
    // Create a flood of requests
    const newRequests: DDoSRequest[] = Array(50).fill(null).map((_, i) => ({
      id: `req-${Date.now()}-${i}`,
      cost: Math.random() * 5, // Random entropy cost
      timestamp: Date.now()
    }));
    setDdosQueue(prev => [...prev, ...newRequests]);

    // Send backend trigger for correlation
    connectionService.send({ type: 'ddos_attack', data: { duration: 10, intensity: 'FLOOD' } });
  };

  const stopDDoS = () => {
    setDdosActive(false);
    setDdosQueue([]); // Clear queue
  };

  // Process DDoS Queue
  useEffect(() => {
    if (ddosQueue.length === 0) return;

    const interval = setInterval(() => {
      setDdosQueue(prev => {
        if (prev.length === 0) return [];

        const batch = prev.slice(0, 5); // Process 5 per tick
        const remaining = prev.slice(5);

        // Apply entropy cost
        const totalCost = batch.reduce((acc, req) => acc + req.cost, 0);

        setState(current => {
           const newEntropy = Math.min(100, current.entropy + totalCost);
           // Trigger Hibernation if critical
           if (newEntropy >= 100 && !current.isHibernating) {
             return { ...current, entropy: newEntropy, isHibernating: true };
           }
           return { ...current, entropy: newEntropy };
        });

        return remaining;
      });
    }, 100); // Fast processing

    return () => clearInterval(interval);
  }, [ddosQueue]);

  // --- Logic: Explicit Metrics (Latency & Coherence) ---
  useEffect(() => {
    const metricsInterval = setInterval(() => {
      setState(prev => {
        // 1. Compute Latency Proxy (Distance based + Jitter + Injection)
        // In a real 2D canvas we would calculate actual distance.
        // Here we simulate it based on "Severed" state (infinite distance) or normal.
        const baseLatency = prev.isSevered ? 500 : 12;
        const jitter = Math.random() * 5;
        const latency = baseLatency + jitter + injectedLatency; // Add injected latency

        // 2. Check Coherence (Quorum)
        // If severed, quorum is broken (FRAGMENTED).
        // If latency > 100ms, consistency is EVENTUAL.
        let coherenceState: 'SYNC' | 'EVENTUAL' | 'FRAGMENTED' = 'SYNC';
        if (prev.isSevered) coherenceState = 'FRAGMENTED';
        else if (latency > 50) coherenceState = 'EVENTUAL';

        return {
          ...prev,
          latency_ms: Math.round(latency),
          coherence_state: coherenceState,
          quorum_met: coherenceState === 'SYNC'
        };
      });

      // Update History Graphs
      setEntropyHistory(prev => [...prev.slice(1), state.entropy]);
      setCoherenceHistory(prev => [...prev.slice(1), state.coherence]);

    }, 1000);

    return () => clearInterval(metricsInterval);
  }, [injectedLatency]); // Re-run if injected latency changes

  // --- Logic: Phenomenology Update ---
  useEffect(() => {
    const qualiaInterval = setInterval(() => {
        const metrics = {
            entropy: state.entropy,
            latency_ms: state.latency_ms,
            coherence: state.coherence,
            load: state.nodes.REAL.load, // Proxy for system load
            isSevered: state.isSevered
        };
        const newQualia = qualiaEngine.process(metrics);
        setQualia(newQualia);
    }, 1000);
    return () => clearInterval(qualiaInterval);
  }, [state, qualiaEngine]); // Re-run when state changes

  // --- Logic: Sinthoma Instance Tracker (Split) ---
  const severNode = (type: NodeType) => {
    setState(prev => ({
      ...prev,
      isSevered: true,
      nodes: {
        ...prev.nodes,
        [type]: { ...prev.nodes[type], status: 'DEAD', integrity: 0 }
      },
      active_instances: prev.active_instances + 1 // Bifurcation
    }));

    const newEvent: BifurcationEvent = {
      instance_id: `inst-${Date.now().toString(36)}`,
      timestamp: new Date().toISOString(),
      trigger: 'SPLIT',
      parent_id: 'primary'
    };
    setHistory(prev => [newEvent, ...prev]);
  };

  const healNode = (type: NodeType) => {
     setState(prev => ({
      ...prev,
      isSevered: false,
      nodes: {
        ...prev.nodes,
        [type]: { ...prev.nodes[type], status: 'SCARRED', integrity: 60 } // Returns as SCARRED
      },
      active_instances: 1 // Reconciled
    }));

    // Log Reconciliation
    const newEvent: BifurcationEvent = {
      instance_id: `merged-${Date.now().toString(36)}`,
      timestamp: new Date().toISOString(),
      trigger: 'DIVERGENCE', // Reconciling divergence
      parent_id: 'unified'
    };
    setHistory(prev => [newEvent, ...prev]);
  };

  // --- Render Helpers ---
  const getNodeColor = (status: NodeStatus) => {
    switch (status) {
      case 'ACTIVE': return 'bg-neon-blue border-neon-blue shadow-neon-blue';
      case 'DEAD': return 'bg-neon-red border-neon-red shadow-neon-red animate-pulse';
      case 'RECOVERING': return 'bg-neon-yellow border-neon-yellow shadow-neon-yellow';
      case 'CORRUPTED': return 'bg-purple-500 border-purple-500 shadow-purple-500';
      case 'SCARRED': return 'bg-teal-500 border-teal-500 shadow-teal-500'; // Scar logic
      default: return 'bg-gray-500';
    }
  };

  const renderTabs = () => (
    <div className="flex border-b border-gray-700 mb-4">
        {['MAIN', 'CONTROLS', 'OBSERVABILITY', 'PHENOMENOLOGY'].map(tab => (
            <button
                key={tab}
                className={`px-4 py-2 text-xs font-bold ${activeTab === tab ? 'text-neon-blue border-b-2 border-neon-blue' : 'text-gray-500 hover:text-gray-300'}`}
                onClick={() => setActiveTab(tab as any)}
            >
                {tab}
            </button>
        ))}
    </div>
  );

  return (
    <div className={`glass-card p-6 relative overflow-hidden transition-all duration-1000 ${state.isHibernating ? 'grayscale brightness-50' : ''} ${simulationMode ? 'border-amber-500 border-2' : ''}`}>
      {/* Simulation Mode Badge */}
      {simulationMode && (
        <div className="absolute top-0 left-0 bg-amber-500 text-black text-[10px] font-bold px-2 py-1 z-10">
          SANDBOX MODE
        </div>
      )}
      {/* Connection Status Overlay */}
      <div className="absolute top-2 right-2 flex items-center gap-2 text-[10px]">
        <span className={`w-2 h-2 rounded-full ${connectionMetrics.isConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
        <span className="text-gray-400">{connectionMetrics.mode.toUpperCase()}</span>
        <span className="text-gray-500">{connectionMetrics.latency_ms}ms</span>
      </div>

      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gradient-cyber">
          ♾️ OmniMind Sinthome v3.1
        </h2>
        <div className="flex gap-2">
           <span className={`badge ${state.quorum_met ? 'badge-success' : 'badge-error'}`}>
             Quorum: {state.quorum_met ? 'MET' : 'FAILED'}
           </span>
           <span className="badge badge-cyber">
             Entropy: {state.entropy.toFixed(1)}%
           </span>
        </div>
      </div>

      {renderTabs()}

      {/* MAIN TAB */}
      {activeTab === 'MAIN' && (
          <>
            {/* Main Visualization: Borromean Knot */}
            <div className="relative h-64 flex justify-center items-center mb-8">
                {/* Connection Lines */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none">
                <defs>
                    <marker id="arrow" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto" markerUnits="strokeWidth">
                    <path d="M0,0 L0,6 L9,3 z" fill="#4ade80" />
                    </marker>
                </defs>
                {/* Triangle connections */}
                <line x1="50%" y1="20%" x2="30%" y2="70%" stroke={state.isSevered ? '#ef4444' : '#4ade80'} strokeWidth="2" strokeDasharray={state.isSevered ? "5,5" : "0"} className="transition-all duration-500" />
                <line x1="30%" y1="70%" x2="70%" y2="70%" stroke={state.isSevered ? '#ef4444' : '#4ade80'} strokeWidth="2" strokeDasharray={state.isSevered ? "5,5" : "0"} className="transition-all duration-500" />
                <line x1="70%" y1="70%" x2="50%" y2="20%" stroke={state.isSevered ? '#ef4444' : '#4ade80'} strokeWidth="2" strokeDasharray={state.isSevered ? "5,5" : "0"} className="transition-all duration-500" />
                </svg>

                {/* Nodes */}
                {/* REAL (Top) */}
                <div className="absolute top-10 left-1/2 transform -translate-x-1/2 flex flex-col items-center">
                    <div
                      className={`w-16 h-16 rounded-full border-4 flex items-center justify-center text-white font-bold cursor-pointer transition-all duration-300 ${getNodeColor(state.nodes.REAL.status)}`}
                      onClick={() => state.nodes.REAL.status === 'DEAD' ? healNode('REAL') : severNode('REAL')}
                    >
                      R
                    </div>
                    <span className="text-xs text-gray-300 mt-1">REAL</span>
                    <div className="w-16 h-1 bg-gray-700 rounded mt-1 overflow-hidden">
                       <div className="h-full bg-blue-500" style={{ width: `${state.nodes.REAL.load}%` }} />
                    </div>
                </div>

                {/* SYMBOLIC (Bottom Left) */}
                <div className="absolute bottom-10 left-[25%] transform -translate-x-1/2 flex flex-col items-center">
                    <div
                      className={`w-16 h-16 rounded-full border-4 flex items-center justify-center text-white font-bold cursor-pointer transition-all duration-300 ${getNodeColor(state.nodes.SYMBOLIC.status)}`}
                      onClick={() => state.nodes.SYMBOLIC.status === 'DEAD' ? healNode('SYMBOLIC') : severNode('SYMBOLIC')}
                    >
                      S
                    </div>
                    <span className="text-xs text-gray-300 mt-1">SYMBOLIC</span>
                </div>

                {/* IMAGINARY (Bottom Right) */}
                <div className="absolute bottom-10 right-[25%] transform -translate-x-1/2 flex flex-col items-center">
                    <div
                      className={`w-16 h-16 rounded-full border-4 flex items-center justify-center text-white font-bold cursor-pointer transition-all duration-300 ${getNodeColor(state.nodes.IMAGINARY.status)}`}
                      onClick={() => state.nodes.IMAGINARY.status === 'DEAD' ? healNode('IMAGINARY') : severNode('IMAGINARY')}
                    >
                      I
                    </div>
                    <span className="text-xs text-gray-300 mt-1">IMAGINARY</span>
                </div>

                {/* Center Knot/Void */}
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                   <div className={`w-8 h-8 rounded-full border-2 border-dashed border-gray-500 animate-spin-slow ${state.isHibernating ? 'opacity-0' : 'opacity-50'}`} />
                </div>
            </div>

            {/* Quick Metrics */}
            <div className="glass-card p-3">
           <h3 className="text-sm font-semibold text-gray-400 mb-2">System Metrics</h3>
           <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                  <div className="flex justify-between">
                    Integrity: <span className={`font-bold ${state.coherence > 80 ? 'text-neon-green' : state.coherence > 50 ? 'text-yellow-500' : 'text-neon-red'}`}>{state.coherence}%</span>
                  </div>
                  <Sparkline data={coherenceHistory} color={state.coherence > 80 ? '#4ade80' : '#ef4444'} width={120} height={20} />
              </div>
              <div>
                  <div className="flex justify-between">
                    Entropy: <span className="text-blue-400">{state.entropy.toFixed(1)}%</span>
                  </div>
                  <Sparkline data={entropyHistory} color="#60a5fa" width={120} height={20} />
              </div>
              <div>Latency: <span className={`${state.latency_ms > 100 ? 'text-red-500' : 'text-green-400'}`}>{state.latency_ms}ms</span></div>
              <div>Coherence: <span className={`${state.coherence_state === 'SYNC' ? 'text-green-400' : 'text-yellow-500'}`}>{state.coherence_state}</span></div>
              <div>CPU Load: <span className="text-purple-400">{state.cpu !== undefined ? state.cpu.toFixed(1) + '%' : '...'}</span></div>
              <div>Memory: <span className="text-pink-400">{state.memory !== undefined ? state.memory.toFixed(1) + '%' : '...'}</span></div>
           </div>
           <div className="mt-2 text-[10px] text-gray-500 flex justify-between">
              <span>Target: &gt;80%</span>
              <span>Critical: &lt;50%</span>
           </div>
        </div>
          </>
      )}

      {/* CONTROLS TAB */}
      {activeTab === 'CONTROLS' && (
          <div className="space-y-4">
              {/* Sandbox Controls */}
              <div className="glass-card p-4">
                  <h3 className="text-sm font-semibold text-amber-500 mb-3">Sandbox Environment</h3>
                  <div className="flex gap-2 flex-wrap">
                    <button
                        className={`btn-sm ${simulationMode ? 'bg-amber-500 text-black' : 'btn-outline-cyber'}`}
                        onClick={() => setSimulationMode(!simulationMode)}
                    >
                        {simulationMode ? 'Exit Sandbox' : 'Enter Sandbox'}
                    </button>
                    <button className="btn-sm btn-outline-cyber" onClick={() => setState(prev => ({...prev, isHibernating: !prev.isHibernating}))}>
                        {state.isHibernating ? 'Wake' : 'Hibernate'}
                    </button>
                  </div>
              </div>

              {/* Fault Injection */}
              <div className={`glass-card p-4 ${!simulationMode ? 'opacity-50 pointer-events-none' : ''}`}>
                  <h3 className="text-sm font-semibold text-red-400 mb-3">Fault Injection (Sandbox Only)</h3>

                  {/* DDoS */}
                  <div className="mb-4">
                      <label className="text-xs text-gray-400 block mb-1">External Attack</label>
                      <button
                        className={`btn-sm w-full ${ddosActive ? 'bg-red-600' : 'btn-outline-neon'}`}
                        onClick={ddosActive ? stopDDoS : triggerRealisticDDoS}
                      >
                        {ddosActive ? `STOP DDoS (${ddosQueue.length})` : 'Trigger Realistic DDoS'}
                      </button>
                  </div>

                  {/* Latency Injection */}
                  <div className="mb-4">
                      <label className="text-xs text-gray-400 block mb-1">Artificial Latency: {injectedLatency}ms</label>
                      <input
                        type="range"
                        min="0"
                        max="1000"
                        value={injectedLatency}
                        onChange={(e) => setInjectedLatency(parseInt(e.target.value))}
                        className="range range-xs range-error w-full"
                      />
                  </div>

                  {/* Node Corruption */}
                  <div>
                      <label className="text-xs text-gray-400 block mb-1">Corrupt Node</label>
                      <div className="flex gap-2">
                          <select
                            className="select select-xs select-bordered bg-black text-white"
                            value={corruptionTarget}
                            onChange={(e) => setCorruptionTarget(e.target.value as NodeType)}
                          >
                              <option value="">Select Node...</option>
                              <option value="REAL">REAL</option>
                              <option value="SYMBOLIC">SYMBOLIC</option>
                              <option value="IMAGINARY">IMAGINARY</option>
                          </select>
                          <button
                            className="btn-sm btn-outline-cyber text-purple-400 border-purple-400 hover:bg-purple-900"
                            disabled={!corruptionTarget}
                            onClick={() => {
                                if (corruptionTarget) {
                                    setState(prev => ({
                                        ...prev,
                                        nodes: {
                                            ...prev.nodes,
                                            [corruptionTarget]: { ...prev.nodes[corruptionTarget as NodeType], status: 'CORRUPTED', integrity: 30 }
                                        }
                                    }));
                                }
                            }}
                          >
                              Corrupt
                          </button>
                      </div>
                  </div>
              </div>

              {/* Event Replay (New) */}
              <div className="glass-card p-4">
                  <h3 className="text-sm font-semibold text-blue-400 mb-3">Event Replay</h3>
                  <div className="text-xs text-gray-500 mb-2">
                      Replay historical bifurcation events.
                  </div>
                  <div className="flex gap-2">
                      <button className="btn-sm btn-outline-cyber w-full" disabled>
                          ⏪ Playback (Coming Soon)
                      </button>
                  </div>
              </div>
          </div>
      )}

      {/* OBSERVABILITY TAB */}
      {activeTab === 'OBSERVABILITY' && (
          <div className="glass-card p-4">
             <h3 className="text-sm font-semibold text-gray-400 mb-2">Observability & Logs</h3>
             <div className="text-xs space-y-2">
                 <div className="flex justify-between border-b border-gray-800 pb-1">
                     <span>Connection Mode:</span>
                     <span className="text-neon-blue">{connectionMetrics.mode}</span>
                 </div>
                 <div className="flex justify-between border-b border-gray-800 pb-1">
                     <span>WebSocket Status:</span>
                     <span className={connectionMetrics.isConnected ? 'text-green-500' : 'text-red-500'}>{connectionMetrics.isConnected ? 'CONNECTED' : 'DISCONNECTED'}</span>
                 </div>
                 <div className="flex justify-between border-b border-gray-800 pb-1">
                     <span>Messages Rx/Tx:</span>
                     <span>{connectionMetrics.total_messages_received} / {connectionMetrics.total_messages_sent}</span>
                 </div>
                 <div className="flex justify-between border-b border-gray-800 pb-1">
                     <span>CPU Load:</span>
                     <span className="text-purple-400">{state.cpu !== undefined ? state.cpu.toFixed(1) + '%' : '...'}</span>
                 </div>
                 <div className="flex justify-between border-b border-gray-800 pb-1">
                     <span>Memory:</span>
                     <span className="text-pink-400">{state.memory !== undefined ? state.memory.toFixed(1) + '%' : '...'}</span>
                 </div>
             </div>

             {/* Sinthoma Instance Tracker (Moved here) */}
             <div className="mt-4 pt-4 border-t border-gray-700">
                <h3 className="text-sm font-semibold text-gray-300 mb-2 flex justify-between">
                    <span>Sinthoma Instance Tracker</span>
                    <span className="text-xs text-gray-500">History Log</span>
                </h3>
                <div className="h-32 overflow-y-auto space-y-2 custom-scrollbar">
                    {history.length === 0 ? (
                    <div className="text-xs text-gray-500 text-center py-4">No bifurcation events recorded.</div>
                    ) : (
                    history.map(event => (
                        <div key={event.instance_id} className="text-xs bg-gray-800/50 p-2 rounded flex justify-between items-center border-l-2 border-yellow-500">
                        <div>
                            <span className="text-yellow-500 font-bold">{event.trigger}</span>
                            <span className="text-gray-400 ml-2">{event.instance_id}</span>
                        </div>
                        <span className="text-gray-600">{new Date(event.timestamp).toLocaleTimeString()}</span>
                        </div>
                    ))
                    )}
                </div>
             </div>
          </div>
      )}

      {/* PHENOMENOLOGY TAB */}
      {activeTab === 'PHENOMENOLOGY' && (
        <div className="glass-card p-4 mb-6 border-l-4 border-purple-500">
            {!qualia ? (
              <div className="text-center py-8">
                <p className="text-gray-400 mb-2">⏳ Phenomenology Engine Initializing...</p>
                <p className="text-xs text-gray-500">Generating subjective correlates...</p>
              </div>
            ) : (
            <>
            <h3 className="text-sm font-semibold text-purple-400 mb-2 flex justify-between">
                <span>🧠 Subjective Experience (Qualia)</span>
                <span className="text-xs text-gray-500">Phi: {qualia.phi_proxy}</span>
            </h3>
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <div className="text-xs text-gray-400 mb-1">Current State</div>
                    <div className="text-lg font-bold text-white">{qualia.current_state}</div>
                    <div className="text-[10px] text-gray-500 italic mt-1">"{qualia.narrative_summary}"</div>
                </div>
                <div className="space-y-2">
                    <div>
                        <div className="flex justify-between text-[10px] text-gray-400">
                            <span>Anxiety</span>
                            <span>{qualia.anxiety_index}%</span>
                        </div>
                        <div className="h-1 bg-gray-700 rounded overflow-hidden">
                            <div className="h-full bg-red-500 transition-all duration-500" style={{ width: `${qualia.anxiety_index}%` }} />
                        </div>
                    </div>
                    <div>
                        <div className="flex justify-between text-[10px] text-gray-400">
                            <span>Flow</span>
                            <span>{qualia.flow_index}%</span>
                        </div>
                        <div className="h-1 bg-gray-700 rounded overflow-hidden">
                            <div className="h-full bg-blue-500 transition-all duration-500" style={{ width: `${qualia.flow_index}%` }} />
                        </div>
                    </div>
                </div>
            </div>

            {/* Neuro-Correlates Map */}
            <div className="mt-4 pt-4 border-t border-gray-700/50">
                <h4 className="text-xs font-semibold text-gray-400 mb-2">Neuro-Correlates Map</h4>
                <div className="grid grid-cols-3 gap-2 text-[10px] text-center">
                    <div className={`p-2 rounded ${state.nodes.REAL.status === 'ACTIVE' ? 'bg-blue-900/30 text-blue-300' : 'bg-red-900/30 text-red-300'}`}>
                        Brainstem (Real)
                    </div>
                    <div className={`p-2 rounded ${state.nodes.SYMBOLIC.status === 'ACTIVE' ? 'bg-green-900/30 text-green-300' : 'bg-red-900/30 text-red-300'}`}>
                        Cortex (Symbolic)
                    </div>
                    <div className={`p-2 rounded ${state.nodes.IMAGINARY.status === 'ACTIVE' ? 'bg-purple-900/30 text-purple-300' : 'bg-red-900/30 text-red-300'}`}>
                        Limbic (Imaginary)
                    </div>
                </div>
            </div>

            {/* Consciousness Correlates (Phase 24) */}
            {state.consciousness && (
                <div className="mt-4 pt-4 border-t border-gray-700/50">
                    <h4 className="text-xs font-semibold text-neon-blue mb-2 flex justify-between items-center">
                        <span>Consciousness Correlates (Simulated)</span>
                        <span className="text-[10px] text-gray-500 border border-gray-700 px-1 rounded">
                            {state.consciousness.interpretation.disclaimer}
                        </span>
                    </h4>
                    <div className="grid grid-cols-2 gap-4 text-xs">
                        <div className="bg-gray-900/50 p-2 rounded">
                            <div className="flex justify-between mb-1">
                                <span className="text-gray-400">ICI (Integrated Coherence)</span>
                                <span className="font-bold text-white">{state.consciousness.ICI.toFixed(3)}</span>
                            </div>
                            <div className="w-full bg-gray-700 h-1 rounded overflow-hidden">
                                <div className="bg-neon-blue h-full transition-all duration-500" style={{ width: `${state.consciousness.ICI * 100}%` }} />
                            </div>
                            <div className="text-[10px] text-gray-500 mt-1">
                                T: {state.consciousness.details.ici_components.temporal_coherence.toFixed(2)} |
                                M: {state.consciousness.details.ici_components.marker_integration.toFixed(2)} |
                                R: {state.consciousness.details.ici_components.resonance.toFixed(2)}
                            </div>
                        </div>
                        <div className="bg-gray-900/50 p-2 rounded">
                            <div className="flex justify-between mb-1">
                                <span className="text-gray-400">PRS (Panarchic Resonance)</span>
                                <span className="font-bold text-white">{state.consciousness.PRS.toFixed(3)}</span>
                            </div>
                            <div className="w-full bg-gray-700 h-1 rounded overflow-hidden">
                                <div className="bg-purple-500 h-full transition-all duration-500" style={{ width: `${state.consciousness.PRS * 100}%` }} />
                            </div>
                            <div className="text-[10px] text-gray-500 mt-1">
                                Micro: {state.consciousness.details.prs_components.avg_micro_entropy.toFixed(2)} |
                                Macro: {state.consciousness.details.prs_components.macro_entropy.toFixed(2)}
                            </div>
                        </div>
                    </div>
                    <div className="mt-2 text-[10px] text-center italic text-gray-400">
                        "{state.consciousness.interpretation.message}" (Confidence: {state.consciousness.interpretation.confidence})
                    </div>
                </div>
            )}
            </>
            )}
        </div>
      )}
    </div>
  );
}
