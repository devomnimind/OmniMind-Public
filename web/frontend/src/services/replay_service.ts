import { BifurcationEvent } from '../components/OmniMindSinthome';

export interface ReplayState {
  isPlaying: boolean;
  currentTime: number; // Timestamp
  speed: number; // 1x, 2x, 5x
  totalDuration: number;
}

export class ReplayService {
  private history: BifurcationEvent[] = [];
  private startTime: number = 0;
  private endTime: number = 0;

  loadHistory(history: BifurcationEvent[]) {
    this.history = [...history].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
    if (this.history.length > 0) {
      this.startTime = new Date(this.history[0].timestamp).getTime();
      this.endTime = new Date(this.history[this.history.length - 1].timestamp).getTime();
    }
  }

  getEventAt(timestamp: number): BifurcationEvent | null {
    // Find the event closest to timestamp but not after
    // Simple linear search for MVP (optimize with binary search later)
    let lastEvent = null;
    for (const event of this.history) {
      const t = new Date(event.timestamp).getTime();
      if (t <= timestamp) {
        lastEvent = event;
      } else {
        break;
      }
    }
    return lastEvent;
  }

  getDuration(): number {
    return this.endTime - this.startTime;
  }

  getStartTime(): number {
    return this.startTime;
  }
}

export const replayService = new ReplayService();
