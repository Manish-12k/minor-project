/**
 * Interaction Tracker
 * Tracks mouse and keyboard behavioral signals
 */

interface MouseSignal {
  x: number;
  y: number;
  timestamp: number;
}

interface KeyboardSignal {
  timestamp: number;
  isKeyDown: boolean;
}

export class InteractionTracker {
  private mouseSignals: MouseSignal[] = [];
  private keyboardSignals: KeyboardSignal[] = [];
  private startTime: number;

  constructor() {
    this.startTime = Date.now();
    this.initializeTracking();
  }

  private initializeTracking() {
    // Track mouse movements
    document.addEventListener('mousemove', (e) => {
      this.mouseSignals.push({
        x: e.clientX,
        y: e.clientY,
        timestamp: Date.now() - this.startTime,
      });
    });

    // Track keyboard events
    document.addEventListener('keydown', () => {
      this.keyboardSignals.push({
        timestamp: Date.now() - this.startTime,
        isKeyDown: true,
      });
    });

    document.addEventListener('keyup', () => {
      this.keyboardSignals.push({
        timestamp: Date.now() - this.startTime,
        isKeyDown: false,
      });
    });
  }

  private calculateMouseEntropy(): number {
    if (this.mouseSignals.length < 2) return 0;

    // Calculate distances between consecutive points
    const distances: number[] = [];
    for (let i = 1; i < this.mouseSignals.length; i++) {
      const dx = this.mouseSignals[i].x - this.mouseSignals[i - 1].x;
      const dy = this.mouseSignals[i].y - this.mouseSignals[i - 1].y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      distances.push(dist);
    }

    // Calculate entropy (measure of randomness)
    const mean = distances.reduce((a, b) => a + b, 0) / distances.length;
    const variance =
      distances.reduce((a, b) => a + (b - mean) ** 2, 0) / distances.length;
    const stddev = Math.sqrt(variance);

    // Entropy (bits) - higher for human, lower for bot
    return stddev > 0 ? Math.log2(stddev + 1) : 0;
  }

  private calculateMouseVelocity() {
    if (this.mouseSignals.length < 2) {
      return { mean: 0, stddev: 0, max: 0 };
    }

    const velocities: number[] = [];
    for (let i = 1; i < this.mouseSignals.length; i++) {
      const dx = this.mouseSignals[i].x - this.mouseSignals[i - 1].x;
      const dy = this.mouseSignals[i].y - this.mouseSignals[i - 1].y;
      const dt = this.mouseSignals[i].timestamp - this.mouseSignals[i - 1].timestamp;
      if (dt > 0) {
        const velocity = Math.sqrt(dx * dx + dy * dy) / dt;
        velocities.push(velocity);
      }
    }

    if (velocities.length === 0) {
      return { mean: 0, stddev: 0, max: 0 };
    }

    const mean = velocities.reduce((a, b) => a + b, 0) / velocities.length;
    const variance =
      velocities.reduce((a, b) => a + (b - mean) ** 2, 0) / velocities.length;
    const stddev = Math.sqrt(variance);
    const max = Math.max(...velocities);

    return { mean, stddev, max };
  }

  private calculateKeyboardMetrics() {
    if (this.keyboardSignals.length < 2) {
      return {
        typingSpeed: 0,
        keystrokeEntropy: 0,
        errorRate: 0,
      };
    }

    // Calculate inter-keystroke timing
    const keystrokeTimes: number[] = [];
    for (let i = 1; i < this.keyboardSignals.length; i += 2) {
      if (
        this.keyboardSignals[i - 1].isKeyDown &&
        !this.keyboardSignals[i].isKeyDown
      ) {
        const timeDiff =
          this.keyboardSignals[i].timestamp -
          this.keyboardSignals[i - 1].timestamp;
        keystrokeTimes.push(timeDiff);
      }
    }

    const avgKeyTime = keystrokeTimes.length > 0
      ? keystrokeTimes.reduce((a, b) => a + b, 0) / keystrokeTimes.length
      : 0;

    // Typing speed (WPM) - assume avg word is 5 chars
    const typingSpeed = avgKeyTime > 0 ? (60000 / (avgKeyTime * 5)) : 0;

    // Keystroke entropy
    const variance = keystrokeTimes.length > 0
      ? keystrokeTimes.reduce(
          (a, b) => a + (b - avgKeyTime) ** 2,
          0
        ) / keystrokeTimes.length
      : 0;
    const stddev = Math.sqrt(variance);
    const keystrokeEntropy = stddev > 0 ? Math.log2(stddev + 1) : 0;

    return {
      typingSpeed: Math.max(0, typingSpeed),
      keystrokeEntropy: Math.max(0, keystrokeEntropy),
      errorRate: 0.02, // Placeholder - would need actual error detection
    };
  }

  getAllSignals() {
    return {
      mouse: {
        movementEntropy: this.calculateMouseEntropy(),
        velocityStats: this.calculateMouseVelocity(),
        totalMovements: this.mouseSignals.length,
      },
      keyboard: this.calculateKeyboardMetrics(),
    };
  }

  getMouseSignals() {
    return this.mouseSignals;
  }

  getKeyboardSignals() {
    return this.keyboardSignals;
  }

  clearSignals() {
    this.mouseSignals = [];
    this.keyboardSignals = [];
    this.startTime = Date.now();
  }
}