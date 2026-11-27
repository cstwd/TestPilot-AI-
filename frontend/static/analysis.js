import {buildGraph} from "./ast-model.js";
import {createInspector} from "./ast-inspector.js";
import {createCanvas} from "./ast-canvas.js";

const MARK = {file: "◆", class: "⬡", function: "ƒ", method: "m"};
const SNAPSHOTS = "testpilot.f02.snapshots.1";
const mobile = window.matchMedia("(max-width: 900px)");

function el(tag, className, text) {
  const item = document.createElement(tag);
  if (className) item.className = className;
  if (text !== undefined) item.textContent = text;
  return item;
}

function button(label, action, className) {
  const item = el("button", className, label);
  item.type = "button";
  item.onclick = action;
  return item;
}

function icon(name) {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("class", "ico");
  svg.setAttribute("aria-hidden", "true");
  const use = document.createElementNS(ns, "use");
  use.setAttribute("href", "#i-" + name);
  svg.append(use);
  return svg;
}

// Snapshots contain the actual analysis response, keyed by immutable identity.
// Reading the source afresh also verifies membership and hash before reuse.
function snapshots() {
  try {
    const values = JSON.parse(localStorage.getItem(SNAPSHOTS) || "[]");
    return Array.isArray(values) ? values : [];
  } catch { return []; }
}
function saveSnapshot(key, data) {
  try {
    const values = [{key, data}, ...snapshots().filter(row => row?.key !== key)].slice(0, 4);
    // On quota pressure keep the most recent result if it fits.
    while (values.length) {
      try { localStorage.setItem(SNAPSHOTS, JSON.stringify(values)); return true; }
      catch { values.pop(); }
    }
  } catch { /* Private windows may disable storage. */ }
  return false;
}

function panel(name) {
  document.body.dataset.panel = name;
  for (const control of document.querySelectorAll("#ast-panel-nav button")) {
    control.setAttribute("aria-pressed", String(control.dataset.panel === name));
  }
  document.querySelector(".graph-pane").inert = mobile.matches && name !== "graph";
}

function showMessage($, title, detail, action) {
  const box = $("ast-message");
  box.hidden = false;
  box.querySelector("h3").textContent = title;
  box.querySelector("p").textContent = detail;
  box.querySelector("a")?.remove();
  if (action) {
    const a = el("a", "", action.label);
    a.href = action.url;
    box.append(a);
  }
}
function status($, text, state, note) {
  $("ast-status").textContent = text;
  $("ast-status").dataset.state = state;
  $("notice").textContent = note;
  $("notice").toggleAttribute("data-error", state === "error");
}
function requestFreshAnalysis() {
  const url = new URL(location.href);
  url.searchParams.set("refresh","1");
  location.assign(url);
}
export function showAnalysisError($, error) {
  status($, "读取失败", "error", error.message);
  $("ast-stage").textContent = "ERROR";
  showMessage($, "无法载入分析", error.message);
  $("ast-refresh").disabled = false;
  $("ast-refresh").onclick = requestFreshAnalysis;
}

function setupFiles($, files, fileId, link, focusRoot) {
  const current = files.find(f => String(f.id) === fileId);
  // SQLite NOCASE folds ASCII letters when grouping immutable revisions.
  const filenameKey = name => name.replace(/[A-Z]/g, ch => ch.toLowerCase());
  const latest = new Map();
  for (const row of files) {
    const key = filenameKey(row.filename);
    if (!latest.has(key) || latest.get(key).revision < row.revision) latest.set(key, row);
  }
  if (current) latest.set(filenameKey(current.filename), current);
  if (current) {
    const revisions = files.filter(f => filenameKey(f.filename) === filenameKey(current.filename));
    if (revisions.length > 1) {
      const chooser = $("ast-revisions");
      chooser.replaceChildren(...revisions.map(f => new Option("v" + f.revision + " · #" + f.id, f.id)));
      chooser.value = fileId;
      chooser.onchange = () => location.assign(link("analysis",{file:chooser.value}));
      chooser.closest("label").hidden = false;
    }
  }
  $("ast-file-count").textContent = String(latest.size);
  function render() {
    const q = $("ast-file-search").value.trim().toLowerCase();
    const rows = [];
    for (const row of latest.values()) {
      if (!row.filename.toLowerCase().includes(q)) continue;
      const active = row.id === current?.id;
      const item = button("", () => {
        if (active) focusRoot(); else location.assign(link("analysis", {file: row.id}));
      }, active ? "chosen" : "");
      item.title = row.filename + " · v" + row.revision;
      item.append(icon("file"), el("span", "row-label", row.filename), el("span", "row-version", "v" + row.revision));
      rows.push(item);
    }
    $("ast-files").replaceChildren(...(rows.length ? rows : [el("p", "muted", q ? "没有匹配的文件" : "尚无导入文件")]));
  }
  $("ast-file-search").oninput = render;
  render();
}

function setupDialog($, options) {
  const dialog = $("ast-dialog");
  $("ast-dialog-close").onclick = () => dialog.close();
  dialog.onclick = event => { if (event.target === dialog) dialog.close(); };
  function open(title, children) {
    $("ast-dialog-title").textContent = title;
    $("ast-dialog-body").replaceChildren(...children);
    dialog.showModal();
  }
  $("ast-help").onclick = () => {
    const links = el("nav","help-nav");
    links.setAttribute("aria-label","工作台模块");
    for (const dest of document.querySelectorAll(".module-rail a")) {
      const a = el("a","",dest.title);
      a.href = dest.href;
      links.append(a);
    }
    open("操作帮助", [
      el("p", "", "点击节点查看定义。双击聚焦局部结构，点击画布空白处取消选择。拖动画布平移，使用滚轮或工具栏缩放。"),
      el("p", "", "按 / 搜索限定名；使用方向键选择，Enter 定位，Esc 关闭。Source 中点击行号可返回最内层定义。"),
      el("p", "", "图谱只展示包含关系。暂停、重播用于重看已返回的数据。"),
      links,
    ]);
  };
  $("ast-settings").onclick = () => {
    const fields = [];
    for (const [key, title] of [["labels","显示节点名称"],["motion","播放渐进动画"]]) {
      const label = el("label");
      const input = el("input");
      input.type = "checkbox"; input.checked = options[key];
      input.onchange = () => options.update(key, input.checked);
      label.append(input, title); fields.push(label);
    }
    if (options.saved) fields.push(button("重新读取已保存结果", () => location.reload()));
    open("图谱设置", fields);
  };
}

function setupSearch($, nodes, choose) {
  const input = $("ast-search"), menu = $("ast-matches");
  let position = 0, matches = [];
  const close = () => { menu.hidden = true; input.setAttribute("aria-expanded","false"); };
  function paint() {
    const q = input.value.trim().toLowerCase();
    if (!q) { close(); return; }
    matches = nodes.filter(node => node.qualified_name.toLowerCase().includes(q)).slice(0, 20);
    position = 0;
    menu.replaceChildren(...matches.map(node => {
      const hit = button("", () => pick(node));
      hit.dataset.nodeId = node.id;
      hit.dataset.type = node.type;
      hit.append(el("i","match-kind",MARK[node.type]), el("span","",node.qualified_name));
      return hit;
    }));
    if (!matches.length) menu.append(el("p", "", "当前版本没有匹配节点"));
    menu.firstElementChild?.classList.add("active");
    menu.hidden = false; input.setAttribute("aria-expanded","true");
  }
  function pick(node) {
    choose(node); input.value = ""; close(); $("ast-canvas").focus({preventScroll:true});
  }
  input.oninput = paint;
  input.onfocus = paint;
  input.onkeydown = event => {
    if (event.key === "Escape") { close(); return; }
    if (menu.hidden || !matches.length) return;
    if (event.key === "Enter") {event.preventDefault(); pick(matches[position]);}
    if (!["ArrowUp","ArrowDown"].includes(event.key)) return;
    event.preventDefault();
    menu.children[position].classList.remove("active");
    position = (position + (event.key === "ArrowDown" ? 1 : -1) + matches.length) % matches.length;
    menu.children[position].classList.add("active");
    menu.children[position].scrollIntoView({block:"nearest"});
  };
  document.addEventListener("pointerdown", e => { if (!input.parentElement.contains(e.target)) close(); });
}

function setupTree($, graph, choose, allowed) {
  const byId = new Map(graph.nodes.map(n => [n.id,n]));
  const depth = new Map(), parents = new Set(graph.edges.map(edge => edge.source));
  for (const node of graph.nodes) depth.set(node.id, node.parent_id ? depth.get(node.parent_id) + 1 : 0);
  const collapsed = new Set(), pageSize = 120;
  let offset = 0, selected = null;

  function visibleNodes() {
    const hidden = new Set(), result = [];
    for (const n of graph.nodes) {
      if (hidden.has(n.parent_id) || collapsed.has(n.parent_id)) hidden.add(n.id);
      else if (allowed.has(n.type)) result.push(n);
    }
    return result;
  }

  function render(rows = visibleNodes()) {
    const fragment = document.createDocumentFragment();
    offset = Math.min(offset, Math.max(0, Math.floor((rows.length - 1) / pageSize) * pageSize));
    for (const n of rows.slice(offset, offset + pageSize)) {
      const row = el("div", "tree-entry");
      row.style.setProperty("--depth", Math.min(depth.get(n.id),7));
      if (parents.has(n.id)) {
        const fold = button(collapsed.has(n.id) ? "›" : "⌄", () => {
          if (collapsed.has(n.id)) collapsed.delete(n.id); else collapsed.add(n.id);
          render();
          $("symbols").querySelector('[data-fold="' + CSS.escape(n.id) + '"]')?.focus();
        },"tree-fold");
        fold.dataset.fold = n.id;
        fold.setAttribute("aria-label", (collapsed.has(n.id) ? "展开 " : "收起 ") + n.qualified_name);
        fold.setAttribute("aria-expanded", String(!collapsed.has(n.id)));
        row.append(fold);
      }
      const item = button("", () => choose(n), "tree-row");
      item.dataset.nodeId = n.id; item.dataset.type = n.type;
      item.setAttribute("aria-pressed", String(selected === n.id));
      item.title = n.signature || n.qualified_name;
      item.append(el("i","kind-icon",MARK[n.type]), el("span","row-label",n.name));
      if (n.signature) item.append(el("span", "sr", n.signature + " · 第 " + n.start_line + "–" + n.end_line + " 行"));
      row.append(item); fragment.append(row);
    }
    if (rows.length > pageSize) {
      const pager = el("div","tree-pager");
      for (const [step,label] of [[-1,"上一页"],[1,"下一页"]]) {
        const control = button(label, () => {offset += step * pageSize; render();});
        control.disabled = step < 0 ? offset === 0 : offset + pageSize >= rows.length;
        pager.append(control);
      }
      fragment.append(pager);
    }
    if (!rows.length) fragment.append(el("p", "muted", "当前筛选没有节点"));
    $("symbols").replaceChildren(fragment);
  }
  render();
  return {
    render,
    select(id) {
      const old = $("symbols").querySelector('[aria-pressed="true"]');
      if (old) old.setAttribute("aria-pressed","false");
      selected = id;
      if (!id) return;
      const query = '[data-node-id="' + CSS.escape(id) + '"]';
      let row = $("symbols").querySelector(query);
      if (!row) {
        for (let n = byId.get(id); n?.parent_id; n = byId.get(n.parent_id)) collapsed.delete(n.parent_id);
        const rows = visibleNodes();
        const index = rows.findIndex(n => n.id === id);
        if (index < 0) return;
        offset = Math.floor(index / pageSize) * pageSize;
        render(rows);
        row = $("symbols").querySelector(query);
      }
      row?.setAttribute("aria-pressed","true");
    },
  };
}

export async function showAnalysis({$, api, link, files, params, fileId, projectId}) {
  let view = null, inspector = null, root = null;
  const counter = document.querySelector(".graph-counts");
  const toolbarWidth = matchMedia("(min-width: 1000px)");
  function placeCounts() {
    const slot = toolbarWidth.matches ? document.querySelector(".utilities") : $("ast-inspector-toggle");
    slot.before(counter);
  }
  placeCounts();
  toolbarWidth.addEventListener("change", placeCounts);
  const options = {labels:true, motion:!matchMedia("(prefers-reduced-motion: reduce)").matches, saved:false,
    update(key, value) {
      this[key] = value;
      if (key === "labels") view?.setLabels(value); else view?.setMotion(value);
    }};
  setupDialog($, options);
  function toggleInspector(open) {
    if (mobile.matches) panel(open ? "inspector" : "graph");
    else document.body.dataset.inspector = open ? "open" : "closed";
  }
  if (window.innerWidth < 1180) document.body.dataset.inspector = "closed";
  $("ast-inspector-toggle").onclick = () => toggleInspector(mobile.matches || document.body.dataset.inspector === "closed");
  $("ast-inspector-close").onclick = () => toggleInspector(false);
  document.querySelectorAll("#ast-panel-nav button").forEach(b => b.onclick = () => panel(b.dataset.panel));
  mobile.addEventListener("change", () => panel("graph"));
  document.addEventListener("keydown", e => {
    if (e.key === "/" && !e.ctrlKey && !e.metaKey && !$("ast-dialog").open &&
        !e.target.closest("input,select,textarea,[contenteditable]")) {
      e.preventDefault(); $("ast-search").focus();
    }
  });
  $("ast-refresh").onclick = requestFreshAnalysis;
  let focusFile = () => panel("graph");
  setupFiles($, files, fileId, link, () => focusFile());
  // The shared selector defaults to the newest item. An explicit stale deep link
  // must never silently display a different project's or revision's evidence.
  if ((params.get("project") && params.get("project") !== projectId) || (params.get("file") && params.get("file") !== fileId)) {
    showMessage($, "找不到指定版本", "该链接中的项目或文件版本已不可用。", {url:link("projects"),label:"选择项目与文件"});
    $("ast-stage").textContent = "UNAVAILABLE";
    status($,"无法定位","error","请求的版本不属于当前项目。"); return;
  }
  if (!fileId) {
    $("ast-stage").textContent = "IDLE";
    status($,"待导入","idle","先在项目中心导入 Python 文件，再查看其中的定义与包含关系。");
    showMessage($,"选择一个 Python 文件","导入后可在图谱中查看类、函数及其源码。",{url:link("projects"),label:"前往项目中心 →"});
    return;
  }
  const url = new URL(location.href);
  const force = url.searchParams.get("refresh") === "1";
  url.searchParams.delete("refresh");
  url.searchParams.set("project",projectId); url.searchParams.set("file",fileId);
  history.replaceState(null,"",url);
  const base = "/api/files/" + fileId;
  const file = await api(base);
  if (String(file.project_id) !== projectId || String(file.id) !== fileId) throw new Error("文件与当前项目不匹配。");
  const key = [projectId,fileId,file.revision,file.filename,file.sha256].join("/");
  let data = !force && snapshots().find(row => row?.key === key)?.data;
  let graph;
  if (data && typeof data.valid === "boolean") {
    try { graph = buildGraph(data, file); } catch { /* Rebuild from the authoritative endpoint. */ }
  }
  const cached = Boolean(graph);
  let timing = "";
  if (!cached) {
    status($,"分析请求中","loading","正在请求 " + file.filename + " · v" + file.revision + " 的 AST 分析…");
    const started = performance.now();
    data = await api(base + "/analysis");
    timing = "分析请求往返 " + Math.round(performance.now() - started) + " ms";
    graph = buildGraph(data, file);
  }
  options.saved = cached || saveSnapshot(key, data);
  const identity = file.filename + " · v" + file.revision;
  $("analysis-meta").textContent = identity;
  $("ast-refresh").disabled = false;
  $("ast-timing").textContent = cached ? "已读取本机分析快照" : timing;
  $("symbol-count").textContent = data.symbols.length + " 个符号";
  if (!data.valid) {
    const error = data.error || {};
    const detail = (error.line == null ? "分析错误" : "语法错误") + " · 行 " + (error.line ?? "—") + "，列 " + (error.column ?? "—") + " · " + (error.message || "分析失败");
    $("symbols").textContent = detail;
    $("ast-stage").textContent = "ERROR";
    $("ast-stats").textContent = identity + " · 1 文件 · 0 个可用符号";
    $("ast-node-count").textContent = "0"; $("ast-edge-count").textContent = "0";
    status($,"分析未完成","error",detail);
    showMessage($,"无法构建结构图谱",detail);
    inspector = createInspector($("inspector-body"),graph,file,{onSelect:()=>{},link});
    inspector.select(graph.nodes[0].id);
    return;
  }
  $("ast-search").disabled = false;
  for (const id of ["ast-minus","ast-plus","ast-fit","ast-reset","ast-pause"]) $(id).disabled = false;
  for (const box of $("ast-types").querySelectorAll("input")) box.disabled = false;
  $("ast-message").hidden = true;
  $("ast-node-count").textContent = graph.nodes.length;
  $("ast-edge-count").textContent = graph.edges.length;
  $("ast-replay").disabled = false;
  const counts = Object.fromEntries(Object.keys(MARK).map(k => [k,graph.nodes.filter(n => n.type === k).length]));
  $("ast-stats").textContent = [identity, counts.file + " 文件", counts.class + " 类", counts.function + " 函数", counts.method + " 方法", graph.edges.length + " 包含关系"].join(" · ");
  const note = cached ? "已恢复此版本的结构与符号。" : "已收到完整分析结果。" + (options.saved ? "已保存本机快照。" : "浏览器存储不可用，可在本页重播。");
  status($,"已解析","ok",identity + " · " + note + (data.symbols.length ? "" : " 此文件没有可展示的函数或类。"));
  const byId = new Map(graph.nodes.map(n => [n.id,n]));
  const eligible = graph.nodes.filter(n => n.topLevelEligible);
  root = graph.nodes[0];
  const allowed = new Set(Object.keys(MARK));
  let selected = null, tree = null, paused = false;
  function select(id, opt = {}) {
    const n = byId.get(id);
    if (n && !allowed.has(n.type)) {
      allowed.add(n.type);
      $("ast-message").hidden = true;
      $("ast-types").querySelector('input[value="' + n.type + '"]').checked = true;
      view?.setTypes(allowed); tree?.render();
    }
    selected = n?.id || null;
    view?.select(selected, opt);
    inspector?.select(selected); tree?.select(selected);
    $("ast-canvas").dataset.selected = selected || "";
    $("ast-selected").textContent = n ? n.qualified_name : "未选择节点";
    const target = n?.topLevelEligible ? n : n?.type === "file" && eligible.length === 1 ? eligible[0] : null;
    const action = $("ast-generation");
    action.hidden = !target;
    if (target) {
      action.href = link("generation",{symbol:target.qualified_name});
      action.title = "为 " + target.qualified_name + " 生成测试";
    } else action.removeAttribute("href");
    const next = new URL(location.href);
    if (selected) next.searchParams.set("node",selected); else next.searchParams.delete("node");
    history.replaceState(null,"",next);
  }
  const locate = n => {panel("graph"); select(n.id,{focus:true});};
  focusFile = () => locate(root);
  tree = setupTree($, graph, locate, allowed);
  inspector = createInspector($("inspector-body"),graph,file,{onSelect:id=>select(id,{focus:true}),link});
  view = createCanvas($("ast-canvas"),graph,{
    onSelect:id=>select(id), onInspect:id=>select(id,{local:true,focus:true}),
    onZoom:scale=>{$("ast-zoom").textContent = Math.round(scale*100) + "%";},
    onStage:(stage,stopped)=>{
      paused = stopped;
      $("ast-stage").textContent = stopped ? stage + " · 已暂停" : stage;
      const btn = $("ast-pause"); btn.disabled = stage === "COMPLETE";
      const label = stopped ? "继续动画" : "暂停动画";
      btn.setAttribute("aria-label",label); btn.title = label; btn.replaceChildren(icon(stopped ? "play":"pause"));
    },
  });
  select(byId.has(params.get("node")) ? params.get("node") : root.id);
  setupSearch($,graph.nodes,locate);
  for (const box of $("ast-types").querySelectorAll("input")) box.onchange = () => {
    if (box.checked) allowed.add(box.value); else allowed.delete(box.value);
    if (selected && !allowed.has(byId.get(selected).type)) select(null);
    view.setTypes(allowed); tree.render(); tree.select(selected);
    if (graph.nodes.some(n => allowed.has(n.type))) $("ast-message").hidden = true;
    else showMessage($,"筛选后没有节点","在 Explorer 的节点类型中重新勾选需要显示的类型。");
  };
  $("ast-plus").onclick = () => view.zoom(1.25);
  $("ast-minus").onclick = () => view.zoom(0.8);
  $("ast-fit").onclick = () => view.fit();
  $("ast-reset").onclick = () => view.reset();
  $("ast-replay").onclick = () => view.replay();
  $("ast-pause").onclick = () => {if (paused) view.resume(); else view.pause();};
  window.addEventListener("pagehide", e => {if (!e.persisted) view.destroy();},{once:true});
}
