import {hierarchy, tree} from "./vendor/d3-hierarchy.js";
import {createAnimation} from "./ast-animation.js";

const TAU = 2 * Math.PI;
const STYLE = {
  file: {color: "#639cff", radius: 19},
  class: {color: "#b291ff", radius: 15},
  function: {color: "#46dcc7", radius: 11},
  method: {color: "#c3df77", radius: 9},
};
const clamp = (value, low, high) => Math.min(high, Math.max(low, value));

function layout(graph) {
  const byId = new Map(graph.nodes.map(node => [node.id, {
    node, children: [], neighbors: new Set(), x: 0, y: 0, drawn: false,
  }]));
  let root;
  for (const point of byId.values()) {
    const parent = byId.get(point.node.parent_id);
    if (parent) parent.children.push(point);
    else root = point;
  }
  const trunk = hierarchy(root, item => item.children);
  const dense = byId.size > 160;
  tree().size([TAU, 1]).separation((a, b) => a.parent === b.parent ? 1 : dense ? 3 : 1.5)(trunk);
  const oneBranch = root.children.length === 1;
  const levels = trunk.descendants();
  const loadByDepth = [];
  for (const item of levels) {
    // Spread wide terminal families across staggered tracks inside their own
    // angular sector. Positions are deterministic and retain the D3 tree order.
    if (dense && item.children?.length >= 12 && item.children.every(child => !child.children)) {
      const tracks = Math.min(12, Math.ceil(Math.sqrt(item.children.length / 5)));
      item.children.forEach((child, i) => {
        child.data.trackOffset = ((i % tracks) / (tracks - 1) - .5) * .78;
        child.data.tracks = tracks;
      });
    }
    loadByDepth[item.depth] = (loadByDepth[item.depth] || 0) + 1 / (item.data.tracks || 1);
  }
  const arcSpan = TAU * (oneBranch ? .56 : 1);
  const spacing = loadByDepth.reduce((step, load, depth) =>
    depth ? Math.max(step, load * 29 / (arcSpan * depth)) : step, 150);
  const points = levels.map((item, index) => {
    const point = item.data;
    // Keep a lone class and its methods on the same side of the file; a full
    // revolution would route half of the class's edges back across its parent.
    const angle = oneBranch ? (item.x - Math.PI) * .56 - .26 : item.x - Math.PI / 2 + .34;
    const distance = (item.depth + (point.trackOffset || 0)) * spacing;
    point.x = Math.cos(angle) * distance * 1.18;
    point.y = Math.sin(angle) * distance;
    point.order = index / Math.max(1, graph.nodes.length - 1);
    point.depth = item.depth;
    return point;
  });
  const lines = graph.edges.map(edge => {
    const source = byId.get(edge.source);
    const target = byId.get(edge.target);
    source.neighbors.add(target);
    target.neighbors.add(source);
    return {source, target};
  }).sort((a, b) => a.target.order - b.target.order);
  return {points, lines, byId};
}

function bounds(points) {
  let left = Infinity, right = -Infinity, top = Infinity, bottom = -Infinity;
  for (const p of points) {
    left = Math.min(left, p.x);
    right = Math.max(right, p.x);
    top = Math.min(top, p.y);
    bottom = Math.max(bottom, p.y);
  }
  return {left, right, top, bottom};
}

// Two short paths read clearly even on a small node. Letters inside the nodes
// keep method/function/class distinct when the display cannot reproduce color.
function drawGlyph(ctx, type, x, y, r) {
  ctx.save();
  ctx.translate(x, y);
  ctx.scale(r / 12, r / 12);
  ctx.strokeStyle = "#effaff";
  ctx.fillStyle = "#effaff";
  ctx.lineWidth = 1.2;
  ctx.lineJoin = ctx.lineCap = "round";
  if (type === "file") {
    ctx.beginPath();
    ctx.moveTo(-4, -6); ctx.lineTo(1, -6); ctx.lineTo(5, -2);
    ctx.lineTo(5, 6); ctx.lineTo(-4, 6); ctx.closePath();
    ctx.moveTo(1, -6); ctx.lineTo(1, -2); ctx.lineTo(5, -2);
    ctx.moveTo(-2, 1); ctx.lineTo(2, 1);
    ctx.moveTo(-2, 3.5); ctx.lineTo(1, 3.5);
    ctx.stroke();
  } else if (type === "class") {
    ctx.beginPath();
    ctx.moveTo(0, -6); ctx.lineTo(5.2, -3); ctx.lineTo(5.2, 3);
    ctx.lineTo(0, 6); ctx.lineTo(-5.2, 3); ctx.lineTo(-5.2, -3); ctx.closePath();
    ctx.moveTo(-5.2, -3); ctx.lineTo(0, 0); ctx.lineTo(5.2, -3);
    ctx.moveTo(0, 0); ctx.lineTo(0, 6); ctx.stroke();
  } else {
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = type === "method" ? "bold 12px Consolas,monospace" : "italic bold 17px Georgia,serif";
    ctx.fillText(type === "method" ? "m" : "ƒ", 0, 0.6);
  }
  ctx.restore();
}

export function createCanvas(canvas, graph, {
  onSelect = () => {}, onStage = () => {}, onZoom = () => {}, onInspect = null,
} = {}) {
  const ctx = canvas.getContext("2d");
  const {points, lines, byId} = layout(graph);
  const rootBounds = bounds(points);
  const dense = points.length > 160;
  const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
  const listeners = new AbortController();
  const eventOptions = {signal: listeners.signal};
  let width = 0, height = 0, ratio = 1;
  let camera = {x: 0, y: 0, k: 1};
  let baseScale = 1, cameraMove = null, autoFit = true;
  let lastZoomPercent = null;
  let selected = null, hovered = null, highlightedAt = -1000, drag = null;
  let enabledTypes = new Set(Object.keys(STYLE));
  let labels = true, allowMotion = true, frame = null, closed = false;
  let hiddenAt = null;
  let visible = points, visibleLines = lines;
  const overlays = canvas.closest(".plot")?.querySelectorAll(".plot-meta, .plot-controls") || [];
  let overlayBounds = [];
  const animation = createAnimation(onStage, invalidate, preference.matches);

  function invalidate() {
    if (!closed && hiddenAt === null && width && height && frame === null) frame = requestAnimationFrame(draw);
  }

  function fitted(box) {
    const contentWidth = Math.max(40, width - Math.min(150, width * .27));
    // The lowest label extends below its glyph, above the floating zoom controls.
    const contentHeight = Math.max(40, height - Math.min(178, height * .34));
    return {
      x: (box.left + box.right) / 2, y: (box.top + box.bottom) / 2,
      k: Math.min(1.45, contentWidth / Math.max(1, box.right - box.left),
        contentHeight / Math.max(1, box.bottom - box.top)),
    };
  }

  function reportZoom() {
    const scale = camera.k / baseScale;
    const percent = Math.round(scale * 100);
    if (percent !== lastZoomPercent) {
      lastZoomPercent = percent;
      onZoom(scale);
    }
  }

  function moveTo(target, animate = false) {
    if (animate && allowMotion && !preference.matches) {
      cameraMove = {from: {...camera}, to: target, start: performance.now()};
    } else {
      camera = target;
      cameraMove = null;
    }
    reportZoom();
    invalidate();
  }

  function fit() {
    autoFit = true;
    if (width && height) moveTo(fitted(visible.length ? bounds(visible) : rootBounds));
  }

  function reset() {
    autoFit = true;
    if (width && height) moveTo(fitted(rootBounds));
  }

  function resize() {
    if (closed || hiddenAt !== null) return;
    const rect = canvas.getBoundingClientRect();
    overlayBounds = Array.from(overlays, element => {
      const r = element.getBoundingClientRect();
      return {x: r.left - rect.left, y: r.top - rect.top, w: r.width, h: r.height};
    });
    const nextRatio = Math.min(window.devicePixelRatio || 1, 2);
    if (width === rect.width && height === rect.height && nextRatio === ratio) {
      invalidate();
      return;
    }
    width = rect.width;
    height = rect.height;
    if (!width || !height) return;
    ratio = nextRatio;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    baseScale = fitted(rootBounds).k;
    if (autoFit) fit();
    else {
      reportZoom();
      invalidate();
    }
  }

  function zoom(factor, x = width / 2, y = height / 2) {
    const next = clamp(camera.k * factor, baseScale * .16, Math.max(7, baseScale * 16));
    autoFit = false;
    moveTo({
      x: camera.x + (x - width / 2) * (1 / camera.k - 1 / next),
      y: camera.y + (y - height / 2) * (1 / camera.k - 1 / next), k: next,
    });
  }

  function replay() {
    // An earlier interaction's accent must not keep running underneath a
    // newly paused replay. Its inspection accent now belongs to the timeline.
    highlightedAt = -Infinity;
    animation.replay();
    autoFit = true;
    if (!width || !height) return;
    const target = fitted(visible.length ? bounds(visible) : rootBounds);
    moveTo(target, true);
    // Keep the opening shot on the presentation clock so pause freezes it too.
    if (cameraMove) cameraMove.replay = true;
  }

  function select(id, {focus = false, local = false} = {}) {
    selected = byId.get(id) || null;
    highlightedAt = performance.now();
    if (selected && (focus || local)) {
      autoFit = false;
      const region = local ? [selected, ...selected.neighbors].filter(p => enabledTypes.has(p.node.type)) : [];
      const target = region.length > 1 ? fitted(bounds(region))
        : {x: selected.x, y: selected.y, k: Math.max(.9, camera.k)};
      moveTo(target, true);
    }
    invalidate();
  }

  function setTypes(types) {
    enabledTypes = new Set(types);
    visible = points.filter(p => enabledTypes.has(p.node.type));
    visibleLines = lines.filter(line => enabledTypes.has(line.source.node.type) && enabledTypes.has(line.target.node.type));
    if (hovered && !enabledTypes.has(hovered.node.type)) hovered = null;
    if (selected && !enabledTypes.has(selected.node.type)) selected = null;
    invalidate();
  }

  function positionOf(id) {
    const p = byId.get(id);
    return p ? {x: width / 2 + (p.x - camera.x) * camera.k, y: height / 2 + (p.y - camera.y) * camera.k} : null;
  }

  function updatePoint(p) {
    p.sx = width / 2 + (p.x - camera.x) * camera.k;
    p.sy = height / 2 + (p.y - camera.y) * camera.k;
    const normalRadius = STYLE[p.node.type].radius;
    const size = normalRadius * clamp(Math.sqrt(camera.k), dense ? .19 : .57, 1.45);
    p.radius = size;
    p.fraction = animation.nodeFraction(p.order);
    p.drawn = p.fraction > 0 && p.sx > -90 && p.sx < width + 90 && p.sy > -40 && p.sy < height + 40;
  }

  function drawLinks() {
    // One stroke per type/emphasis group, even when thousands of edges appear.
    const batches = new Map();
    const tips = new Path2D();
    for (let i = 0; i < visibleLines.length; i++) {
      const {source: a, target: b} = visibleLines[i];
      const t = animation.edgeFraction(i / Math.max(1, visibleLines.length - 1));
      if (!t) break;
      if (Math.max(a.sx,b.sx) < -100 || Math.min(a.sx,b.sx) > width+100
          || Math.max(a.sy,b.sy) < -100 || Math.min(a.sy,b.sy) > height+100) continue;
      const active = selected && (selected === a || selected === b);
      const alpha = active ? "ea" : selected ? "3d" : dense ? "45" : "8d";
      const color = STYLE[b.node.type].color + alpha;
      let batch = batches.get(color);
      if (!batch) {
        batch = {path: new Path2D(), active, width: active ? 2.1 : dense ? .8 : 1.3};
        batches.set(color, batch);
      }
      const dx = b.sx - a.sx, dy = b.sy - a.sy;
      const bend = dense ? .026 : .085;
      const cx = (a.sx + b.sx) / 2 - bend * dy;
      const cy = (a.sy + b.sy) / 2 + bend * dx;
      const ux = a.sx + (cx-a.sx)*t, uy = a.sy + (cy-a.sy)*t;
      const endX = ux*(1-t)+(cx+(b.sx-cx)*t)*t;
      const endY = uy*(1-t)+(cy+(b.sy-cy)*t)*t;
      batch.path.moveTo(a.sx, a.sy);
      batch.path.quadraticCurveTo(ux, uy, endX, endY);
      if (!dense && t > .03 && t < .97) {
        tips.moveTo(endX + 2, endY);
        tips.arc(endX, endY, 2, 0, TAU);
      }
    }
    for (const [color, batch] of [...batches].sort((a,b) => Number(a[1].active) - Number(b[1].active))) {
      ctx.strokeStyle = color;
      ctx.lineWidth = batch.width;
      ctx.stroke(batch.path);
    }
    if (!dense) {
      ctx.fillStyle = "#e2dcff";
      ctx.fill(tips);
    }
  }

  function drawPoint(p, now) {
    const {sx: x, sy: y} = p;
    const active = p === selected || p === hovered;
    const color = STYLE[p.node.type].color;
    const neighbor = selected?.neighbors.has(p);
    const dim = selected && !active && !neighbor;
    ctx.globalAlpha = p.fraction * (dim ? .56 : 1);
    const r = p.radius * (.50 + .50 * p.fraction);
    if (r > 6 || active) {
      if (!dense || active) {
        const halo = ctx.createRadialGradient(x, y, r * .45, x, y, r * 2.8);
        halo.addColorStop(0, color + (active ? "59" : "33"));
        halo.addColorStop(1, color + "00");
        ctx.fillStyle = halo;
        ctx.fillRect(x-r*2.8, y-r*2.8, r*5.6, r*5.6);
      }
      ctx.beginPath(); ctx.arc(x, y, r+3, 0, TAU);
      ctx.strokeStyle = color + (active ? "e3" : neighbor ? "ae" : "55"); ctx.lineWidth = 1; ctx.stroke();
    }
    ctx.beginPath(); ctx.arc(x, y, r, 0, TAU);
    ctx.fillStyle = r > 6 ? "#111a2b" : color;
    ctx.fill();
    if (r > 6) {
      ctx.fillStyle = color + (active ? "76" : "45");
      ctx.fill();
      ctx.strokeStyle = color;
      ctx.lineWidth = active ? 2 : 1.4;
      ctx.stroke();
      if (!dense || active || camera.k > .9) drawGlyph(ctx, p.node.type, x, y, r);
    }
    if (p === selected) {
      const elapsed = allowMotion && !preference.matches ? clamp((now-highlightedAt)/210, 0, 1) : 1;
      const outer = r + 7 + 3 * (1 - elapsed) + 5 * animation.inspectionPulse;
      ctx.beginPath();
      ctx.arc(x, y, outer, -.8, .33);
      ctx.moveTo(x + outer * Math.cos(Math.PI - .8), y + outer * Math.sin(Math.PI - .8));
      ctx.arc(x, y, outer, Math.PI - .8, Math.PI + .33);
      ctx.strokeStyle = color + "aa"; ctx.lineWidth = 1.3; ctx.stroke();
    }
    ctx.globalAlpha = 1;
  }

  function drawLabels() {
    const occupancy = [...overlayBounds];
    const nodeRows = new Map();
    for (const p of visible) {
      if (!p.drawn) continue;
      const row = Math.floor(p.sy / 32);
      if (!nodeRows.has(row)) nodeRows.set(row, []);
      nodeRows.get(row).push(p);
    }
    // The maximum glyph radius is under 28 px at all camera scales. Group by
    // screen row to check only the nearby glyphs in both overview and close-up.
    function hitsNode(box) {
      for (let row = Math.floor((box.y - 32) / 32); row <= Math.floor((box.y + box.h + 32) / 32); row++) {
        for (const q of nodeRows.get(row) || []) {
          const dx = q.sx - clamp(q.sx, box.x, box.x + box.w);
          const dy = q.sy - clamp(q.sy, box.y, box.y + box.h);
          if (dx*dx + dy*dy < (q.radius+4)**2) return true;
        }
      }
      return false;
    }
    const priority = [];
    if (selected) priority.push(selected);
    if (hovered && hovered !== selected) priority.push(hovered);
    for (const p of visible) {
      if (labels && p !== selected && p !== hovered && selected?.neighbors.has(p)) priority.push(p);
    }
    if (labels) for (const p of visible) {
      if (p !== selected && p !== hovered && !selected?.neighbors.has(p)) priority.push(p);
    }
    ctx.font = '12px Consolas, "Microsoft YaHei", monospace';
    ctx.textBaseline = "middle";
    ctx.textAlign = "center";
    for (const p of priority) {
      if (!p.drawn || p.fraction < .65 || !enabledTypes.has(p.node.type)) continue;
      // Glyphs are overscanned for panning. Only attach a name to a node
      // whose centre can actually be seen in this viewport.
      if (p.sx < 0 || p.sx > width || p.sy < 0 || p.sy > height) continue;
      const active = p === selected || p === hovered;
      if (!active && (occupancy.length >= 75 ||
          (dense && p.radius < 7 && p.depth > 0 && !(p.children.length && selected?.neighbors.has(p))))) continue;
      const name = p.node.name.length > 33 ? p.node.name.slice(0,30) + "…" : p.node.name;
      p.labelWidth ??= ctx.measureText(name).width + 12;
      const labelWidth = Math.min(width-8, p.labelWidth);
      const offset = p.radius + 17;
      const side = p.radius + 7 + labelWidth/2;
      const candidates = [[0,offset], [0,-offset], [side,0], [-side,0]];
      if (active) candidates.push([side,offset],[-side,offset],[side,-offset],[-side,-offset]);
      let box = null;
      for (const [dx, dy] of candidates) {
        const x = clamp(p.sx+dx, labelWidth/2+2, width-labelWidth/2-2), y = p.sy + dy;
        if (y < 10 || y > height - 11) continue;
        const next = {x: x-labelWidth/2, y: y-9, w: labelWidth, h: 19};
        if (occupancy.some(q => next.x < q.x+q.w+3 && next.x+next.w+3 > q.x
            && next.y < q.y+q.h+2 && next.y+next.h+2 > q.y)) continue;
        if (hitsNode(next)) continue;
        box = next;
        break;
      }
      if (!box) continue;
      occupancy.push(box);
      const dim = selected && !active && !selected.neighbors.has(p);
      ctx.globalAlpha = (dim ? .59 : 1) * clamp((p.fraction - .65) / .35, 0, 1);
      ctx.fillStyle = active ? "#1b1e33" : "#101323ed";
      ctx.beginPath(); ctx.roundRect(box.x, box.y, box.w, box.h, 4); ctx.fill();
      if (active || p.depth === 0) {
        ctx.strokeStyle = STYLE[p.node.type].color + "78"; ctx.lineWidth = 1; ctx.stroke();
      }
      ctx.fillStyle = active || !p.depth ? "#f7f7ff" : "#d8dce9";
      ctx.fillText(name, box.x + box.w/2, box.y + 9.5, Math.max(1,labelWidth-6));
    }
    ctx.globalAlpha = 1;
  }

  function draw(now) {
    frame = null;
    if (closed || hiddenAt !== null || !width || !height) return;
    animation.tick(now);
    if (cameraMove) {
      const {from, to, replay} = cameraMove;
      const t = clamp(replay ? animation.elapsed/600 : (now-cameraMove.start)/210, 0, 1);
      const mix = t*t*(3-2*t);
      // Interpolate magnification geometrically. Even replaying at a fitted
      // view has one small pull-back with zero velocity at both endpoints.
      const pullBack = replay ? 1 - .055 * Math.sin(Math.PI*t)**2 : 1;
      camera = {x: from.x+(to.x-from.x)*mix, y: from.y+(to.y-from.y)*mix,
        k: from.k * (to.k/from.k)**mix * pullBack};
      reportZoom();
      if (t === 1) cameraMove = null;
    }
    ctx.setTransform(ratio,0,0,ratio,0,0);
    ctx.clearRect(0,0,width,height);
    for (const p of visible) updatePoint(p);
    drawLinks();
    for (const p of visible) if (p.drawn && p !== selected) drawPoint(p,now);
    if (selected?.drawn) drawPoint(selected,now);
    drawLabels();
    if (animation.active || (cameraMove && !cameraMove.replay) || (allowMotion && !preference.matches && selected && now-highlightedAt < 210)) invalidate();
  }

  function hit(x, y) {
    let best = null, distance = Infinity;
    for (const p of visible) {
      if (!p.drawn) continue;
      const dx=x-p.sx, dy=y-p.sy;
      const d=dx*dx+dy*dy;
      if (d < distance && d < Math.max(11,p.radius+5)**2) { best=p; distance=d; }
    }
    return best;
  }
  function pointer(event) {
    const rect = canvas.getBoundingClientRect();
    return {x: event.clientX - rect.left, y: event.clientY - rect.top};
  }
  canvas.addEventListener("wheel", event => {
    event.preventDefault();
    const p = pointer(event);
    const delta = event.deltaY * (event.deltaMode === 1 ? 16 : 1);
    zoom(Math.exp(-clamp(delta,-700,700)*.0017), p.x, p.y);
  }, {...eventOptions, passive: false});
  canvas.addEventListener("pointerdown", event => {
    if (event.button !== 0 || !event.isPrimary) return;
    const p = pointer(event);
    drag = {p, camera: {...camera}, moved: false, id: event.pointerId};
    cameraMove = null;
    canvas.setPointerCapture(event.pointerId);
  }, eventOptions);
  canvas.addEventListener("pointermove", event => {
    const p = pointer(event);
    if (drag && drag.id === event.pointerId) {
      const dx = p.x - drag.p.x, dy = p.y - drag.p.y;
      if (Math.hypot(dx,dy) > 3) drag.moved = true;
      if (drag.moved) {
        autoFit = false;
        hovered = null;
        canvas.style.cursor = "grabbing";
        camera.x = drag.camera.x - dx / camera.k;
        camera.y = drag.camera.y - dy / camera.k;
        invalidate();
      }
    } else {
      const next = hit(p.x,p.y);
      if (next !== hovered) { hovered = next; invalidate(); }
      canvas.style.cursor = hovered ? "pointer" : "grab";
    }
  }, eventOptions);
  canvas.addEventListener("pointerup", event => {
    if (!drag || drag.id !== event.pointerId) return;
    const {moved} = drag;
    drag = null;
    canvas.releasePointerCapture(event.pointerId);
    canvas.style.cursor = "grab";
    if (!moved) {
      const p = pointer(event);
      const id = hit(p.x, p.y)?.node.id ?? null;
      if (id !== (selected?.node.id ?? null)) onSelect(id);
    }
  }, eventOptions);
  canvas.addEventListener("lostpointercapture", () => { drag = null; }, eventOptions);
  canvas.addEventListener("pointerleave", () => { if (hovered) { hovered = null; invalidate(); } }, eventOptions);
  canvas.addEventListener("dblclick", event => {
    const p = pointer(event), target = hit(p.x,p.y);
    if (!target) return;
    if (onInspect) onInspect(target.node.id);
    else select(target.node.id, {local:true});
  }, eventOptions);
  function syncMotion() {
    animation.setMotion(allowMotion && !preference.matches);
    if (cameraMove && (!allowMotion || preference.matches)) moveTo(cameraMove.to);
  }
  preference.addEventListener("change",syncMotion,eventOptions);
  const observer = new ResizeObserver(resize);
  observer.observe(canvas);
  for (const element of overlays) observer.observe(element);
  resize();
  animation.replay();

  return {
    select, setTypes, zoom, fit, reset, positionOf,
    pause: animation.pause, resume: animation.resume, replay,
    setMotion(value) { allowMotion = value; syncMotion(); },
    setLabels(value) { labels = value; invalidate(); },
    setVisible(visible) {
      if (closed || visible === (hiddenAt === null)) return;
      const now = performance.now();
      animation.resetClock();
      if (!visible) {
        hiddenAt = now;
        if (frame !== null) cancelAnimationFrame(frame);
        frame = null;
        return;
      }
      const elapsed = now - hiddenAt;
      hiddenAt = null;
      if (cameraMove && !cameraMove.replay) cameraMove.start += elapsed;
      highlightedAt += elapsed;
      resize();
    },
    destroy() {
      closed = true;
      observer.disconnect();
      listeners.abort();
      if (frame !== null) cancelAnimationFrame(frame);
    },
  };
}
