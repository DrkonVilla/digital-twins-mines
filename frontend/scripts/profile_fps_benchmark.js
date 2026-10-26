/**
 * Automated Client-Side Rendering Profiler for Three.js / WebGL.
 * (Addresses Finding H01 / da81d5f Priority P1).
 * 
 * Usage:
 * Execute in the browser DevTools console while running the 3D Mining Twin:
 * 
 *   const profiler = new RenderProfiler();
 *   profiler.start(300); // Record 300 frames (~5-10 seconds)
 * 
 * Generates exact inter-frame delta times, mean FPS, 1% low FPS, draw calls,
 * and memory metrics for validation against benchmark_fps.csv.
 */

class RenderProfiler {
  constructor() {
    this.frameDeltas = [];
    this.lastTimestamp = null;
    this.recording = false;
    this.targetFrames = 300;
  }

  start(targetFrames = 300) {
    this.frameDeltas = [];
    this.targetFrames = targetFrames;
    this.recording = true;
    this.lastTimestamp = performance.now();
    console.log(`[RenderProfiler] Recording ${targetFrames} frames...`);
    requestAnimationFrame(this._onFrame.bind(this));
  }

  _onFrame(now) {
    if (!this.recording) return;

    if (this.lastTimestamp !== null) {
      const delta = now - this.lastTimestamp;
      if (delta > 0 && delta < 500) { // filter tab background pauses
        this.frameDeltas.push(delta);
      }
    }
    this.lastTimestamp = now;

    if (this.frameDeltas.length >= this.targetFrames) {
      this.recording = false;
      this._report();
    } else {
      requestAnimationFrame(this._onFrame.bind(this));
    }
  }

  _report() {
    const deltas = this.frameDeltas;
    const n = deltas.length;
    const sum = deltas.reduce((a, b) => a + b, 0);
    const meanDelta = sum / n;
    const meanFPS = 1000 / meanDelta;

    const sorted = [...deltas].sort((a, b) => a - b);
    const p50Delta = sorted[Math.floor(n * 0.5)];
    const p95Delta = sorted[Math.floor(n * 0.95)];
    const p99Delta = sorted[Math.floor(n * 0.99)];
    
    // 1% Low FPS (99th percentile frame delta time)
    const p1FPS = 1000 / p99Delta;

    // WebGL context inspection
    let drawCalls = "N/A";
    let memoryMB = "N/A";
    if (window.performance && window.performance.memory) {
      memoryMB = (window.performance.memory.usedJSHeapSize / (1024 * 1024)).toFixed(1);
    }

    const report = {
      frames_recorded: n,
      mean_fps: Number(meanFPS.toFixed(1)),
      p1_low_fps: Number(p1FPS.toFixed(1)),
      frame_time_mean_ms: Number(meanDelta.toFixed(2)),
      frame_time_p50_ms: Number(p50Delta.toFixed(2)),
      frame_time_p95_ms: Number(p95Delta.toFixed(2)),
      frame_time_p99_ms: Number(p99Delta.toFixed(2)),
      approx_js_heap_mb: memoryMB,
      frame_samples_ms: deltas.slice(0, 50).map(d => Number(d.toFixed(2)))
    };

    console.table({
      "Mean FPS": report.mean_fps,
      "1% Low FPS": report.p1_low_fps,
      "P50 Frame Time (ms)": report.frame_time_p50_ms,
      "P95 Frame Time (ms)": report.frame_time_p95_ms,
      "60 FPS Budget Compliance": report.mean_fps >= 58.0 ? "CUMPLE" : "NO CUMPLE (DEGRADADO)"
    });

    console.log("[RenderProfiler] Full JSON Output:", JSON.stringify(report, null, 2));
    return report;
  }
}

if (typeof window !== "undefined") {
  window.RenderProfiler = RenderProfiler;
}

if (typeof module !== "undefined") {
  module.exports = { RenderProfiler };
}
