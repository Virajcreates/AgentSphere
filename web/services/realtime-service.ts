"use client";

// High performance async polling coordinator to simulate real-time operations
export class RealtimeService {
  private static _timers: Map<string, NodeJS.Timeout> = new Map();

  static startPolling<T>(
    key: string,
    task: () => Promise<T>,
    callback: (result: T) => void,
    interval_ms: number = 3000
  ): void {
    // Prevent overlapping timers matching the same key identifier
    this.stopPolling(key);

    const executeTask = async () => {
      try {
        const res = await task();
        callback(res);
      } catch (err) {
        console.warn(`RealtimeService polling task error [${key}]:`, err);
      }
    };

    // Trigger initial execution
    executeTask();

    const timer = setInterval(executeTask, interval_ms);
    this._timers.set(key, timer);
  }

  static stopPolling(key: string): void {
    if (this._timers.has(key)) {
      clearInterval(this._timers.get(key)!);
      this._timers.delete(key);
    }
  }

  static clearAll(): void {
    for (const key of this._timers.keys()) {
      this.stopPolling(key);
    }
  }
}
export default RealtimeService;
