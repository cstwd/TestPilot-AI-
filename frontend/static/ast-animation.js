// Runs only the presentation timeline. A paused or completed timeline has no timer.
const nodeSweep = 730;
const nodeFade = 320;
const edgeSweep = 690;
const edgeDraw = 460;
const edgeStart = nodeSweep + nodeFade;
const inspectionStart = edgeStart + edgeSweep + edgeDraw;
const end = inspectionStart + 500;
const clamp = value => Math.max(0, Math.min(1, value));

export function createAnimation(onChange, invalidate, reducedMotion) {
  let time = 0;
  let lastTick = null;
  let paused = false;
  let lastState = "";
  let motion = !reducedMotion;

  function publish() {
    const stage = time >= end ? "COMPLETE" : time >= inspectionStart ? "INSPECTION"
      : time >= edgeStart ? "STRUCTURE BUILDING" : "PARSING";
    const state = stage + paused;
    if (state !== lastState) {
      lastState = state;
      onChange(stage, paused);
    }
  }

  function replay() {
    time = motion ? 0 : end;
    lastTick = null;
    paused = false;
    publish();
    invalidate();
  }

  return {
    replay,
    tick(now) {
      if (paused || time >= end) return;
      if (lastTick !== null) time = Math.min(end, time + Math.max(0, now - lastTick));
      lastTick = now;
      publish();
    },
    nodeFraction(order) {
      const t = clamp((time - order * nodeSweep) / nodeFade);
      return t * t * (3 - 2 * t);
    },
    edgeFraction(order) {
      const t = clamp((time - edgeStart - order * edgeSweep) / edgeDraw);
      return t * t * (3 - 2 * t);
    },
    get inspectionPulse() {
      return time > inspectionStart && time < end
        ? Math.sin(Math.PI * (time - inspectionStart) / (end - inspectionStart)) : 0;
    },
    get elapsed() { return time; },
    get active() { return !paused && time < end; },
    pause() {
      if (time >= end || paused) return;
      paused = true;
      lastTick = null;
      publish();
    },
    resume() {
      if (!paused) return;
      paused = false;
      publish();
      invalidate();
    },
    setMotion(enabled) {
      motion = enabled;
      if (!enabled) {
        time = end;
        paused = false;
        publish();
        invalidate();
      }
    },
  };
}
