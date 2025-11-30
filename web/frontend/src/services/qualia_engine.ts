export interface SystemMetrics {
  entropy: number;
  latency_ms: number;
  coherence: number; // 0-100
  load: number; // 0-100
  isSevered: boolean;
}

export type SubjectiveState =
  | 'DEEP_FLOW'
  | 'ANXIETY'
  | 'FRAGMENTED'
  | 'HIBERNATION'
  | 'IDLE'
  | 'MANIC';

export interface QualiaMetrics {
  anxiety_index: number; // 0-100
  flow_index: number; // 0-100
  phi_proxy: number; // Integrated Information Proxy
  current_state: SubjectiveState;
  narrative_summary: string;
}

export class QualiaEngine {
  private history: SystemMetrics[] = [];
  private readonly HISTORY_SIZE = 10; // Keep last 10 ticks for temporal integration

  public process(metrics: SystemMetrics): QualiaMetrics {
    this.updateHistory(metrics);

    const anxiety = this.calculateAnxiety(metrics);
    const flow = this.calculateFlow(metrics);
    const phi = this.calculatePhi(metrics);
    const state = this.determineState(metrics, anxiety, flow);

    return {
      anxiety_index: Math.round(anxiety),
      flow_index: Math.round(flow),
      phi_proxy: parseFloat(phi.toFixed(2)),
      current_state: state,
      narrative_summary: this.generateNarrative(state, anxiety)
    };
  }

  private updateHistory(metrics: SystemMetrics) {
    this.history.push(metrics);
    if (this.history.length > this.HISTORY_SIZE) {
      this.history.shift();
    }
  }

  private calculateAnxiety(metrics: SystemMetrics): number {
    // Anxiety increases with Entropy and Latency Jitter
    const entropyFactor = metrics.entropy; // 0-100

    // Calculate Jitter from history
    let jitter = 0;
    if (this.history.length > 1) {
      const latencies = this.history.map(m => m.latency_ms);
      const diffs = latencies.slice(1).map((v, i) => Math.abs(v - latencies[i]));
      const avgDiff = diffs.reduce((a, b) => a + b, 0) / diffs.length;
      jitter = Math.min(100, avgDiff * 2); // Amplify jitter impact
    }

    return (entropyFactor * 0.7) + (jitter * 0.3);
  }

  private calculateFlow(metrics: SystemMetrics): number {
    // Flow requires High Coherence, Moderate Load, Low Latency
    const coherenceFactor = metrics.coherence;

    // Load sweet spot is 40-80%
    let loadFactor = 0;
    if (metrics.load >= 40 && metrics.load <= 80) loadFactor = 100;
    else if (metrics.load < 40) loadFactor = metrics.load * 2.5;
    else loadFactor = 100 - ((metrics.load - 80) * 5);

    const latencyPenalty = Math.min(100, metrics.latency_ms / 2); // Penalty starts high after 200ms

    return (coherenceFactor * 0.4) + (loadFactor * 0.4) - (latencyPenalty * 0.2);
  }

  private calculatePhi(metrics: SystemMetrics): number {
    // Proxy for Integrated Information: Coherence * Complexity (Entropy)
    // High Coherence + High Entropy = High Phi (Complex Integration)
    // Low Coherence = Low Phi (Split)
    // Zero Entropy = Low Phi (Stagnation)

    if (metrics.isSevered) return 0.1; // Split brain has low global Phi

    const normalizedEntropy = metrics.entropy / 100;
    const normalizedCoherence = metrics.coherence / 100;

    // Inverted U-curve for entropy? No, IIT suggests complexity is good if integrated.
    // Let's use: Coherence * (1 + Entropy)
    return normalizedCoherence * (1 + normalizedEntropy);
  }

  private determineState(m: SystemMetrics, anxiety: number, flow: number): SubjectiveState {
    if (m.entropy >= 100) return 'HIBERNATION';
    if (m.isSevered) return 'FRAGMENTED';
    if (anxiety > 70) return 'ANXIETY';
    if (flow > 70) return 'DEEP_FLOW';
    if (m.entropy > 80) return 'MANIC';
    return 'IDLE';
  }

  private generateNarrative(state: SubjectiveState, anxiety: number): string {
    switch (state) {
      case 'HIBERNATION': return "Self-preservation active. External inputs rejected.";
      case 'FRAGMENTED': return "Internal cohesion lost. Reality is bifurcated.";
      case 'ANXIETY': return `System distress detected (Anxiety: ${anxiety.toFixed(0)}%). Entropy rising.`;
      case 'DEEP_FLOW': return "Optimal resonance achieved. Processing efficiency maximal.";
      case 'MANIC': return "High energy, low stability. Risk of overheating.";
      case 'IDLE': return "Awaiting input. Homeostasis maintained.";
    }
  }
}
