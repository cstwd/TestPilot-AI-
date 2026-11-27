import {buildGraph} from "./ast-model.js";
import {labelStatus} from "./runs.js";
import {colorLine, splitSource, tokenize} from "./studio-source.js";

const MODE = "template";
const PAGE_LINES = 96;

function stage(node, value, kind) {
  node.textContent = value;
  node.dataset.state = kind;
}

function state(node, kind, title, detail) {
  node.hidden = false;
  node.dataset.state = kind;
  node.querySelector("h3").textContent = title;
  node.querySelector("p").textContent = detail;
}

function announce($, message, error = false) {
  $("notice").textContent = message;
  $("notice").toggleAttribute("data-error", error);
}

function facts(node, rows) {
  const content = document.createDocumentFragment();
  for (const [label, value] of rows) {
    const term = document.createElement("dt");
    term.textContent = label;
    const detail = document.createElement("dd");
    detail.textContent = value ?? "未记录";
    content.append(term, detail);
  }
  node.replaceChildren(content);
  node.hidden = false;
}

function runTone(value) {
  if (value === "passed") return "ok";
  if (["failed", "error", "timeout"].includes(value)) return "error";
  return "warning";
}

function showCode($, {source, view, pager, copy, range}) {
  const {lines, offsets} = splitSource(source);
  const lower = range ? range[0] - 1 : 0;
  const upper = range ? range[1] : lines.length;
  const snippet = source.slice(offsets[lower], offsets[upper]);
  // Tokenize the original lines for multiline string state, then paint just the visible page.
  const tokens = tokenize(lines.slice(0, upper));
  let first = lower;
  const controls = $(pager);
  const previous = controls.querySelector('[data-step="-1"]');
  const next = controls.querySelector('[data-step="1"]');
  function render() {
    const stop = Math.min(first + PAGE_LINES, upper);
    const rows = document.createDocumentFragment();
    for (let i = first; i < stop; i++) {
      const line = document.createElement("span");
      line.className = "ai-source-line";
      const no = document.createElement("span");
      no.className = "ai-line-no";
      no.dataset.number = i + 1;
      no.setAttribute("aria-hidden", "true");
      line.append(no, colorLine(lines[i], tokens[i]));
      rows.append(line);
    }
    const code = $(view);
    code.replaceChildren(rows);
    code.parentElement.scrollTop = code.parentElement.scrollLeft = 0;
    controls.hidden = upper - lower <= PAGE_LINES;
    previous.disabled = first === lower;
    next.disabled = stop === upper;
    controls.querySelector("span").textContent = "第 " + (first + 1) + "–" + stop + " 行";
  }
  previous.onclick = () => { first -= PAGE_LINES; render(); };
  next.onclick = () => { first += PAGE_LINES; render(); };
  $(copy).disabled = !snippet;
  $(copy).onclick = async () => {
    try {
      await navigator.clipboard.writeText(snippet);
      announce($, "已复制源码。");
    } catch {
      announce($, "剪贴板权限不可用，可在源码区选中文本。", true);
    }
  };
  render();
}

function resetSuite($) {
  $("suite-panel").hidden = true;
  $("suite-facts").hidden = true;
  $("suite-facts-empty").hidden = false;
  $("run-facts").hidden = true;
  $("run-suite").hidden = true;
  $("run-suite").removeAttribute("href");
  $("console-suite").hidden = true;
  $("static-detail").textContent = "暂无检查记录。";
  $("run-detail").textContent = "暂无运行记录。";
  stage($("stage-static"), "暂无记录", "idle");
  stage($("stage-run"), "暂无记录", "idle");
}

export function showGenerationError($, error, link) {
  resetSuite($);
  stage($("stage-request"), "读取失败", "error");
  state($("target-empty"), "error", "无法加载目标函数", error.message);
  state($("suite-empty"), "error", "无法读取测试套件", "请重新读取，或切换来源版本。");
  $("target-meta").textContent = "当前上下文暂不可用。";
  $("gen-retry").hidden = false;
  $("gen-retry").onclick = () => location.reload();
  $("gen-return-context").href = link("projects", {file: $("file").value});
  $("gen-return-context").hidden = false;
  announce($, error.message, true);
}

export async function showGeneration({$, api, link, params, projectId, file}) {
  const nav = document.querySelector(".gen-mobile-nav");
  nav.addEventListener("keydown", event => {
    if (event.key === "Escape" && nav.open) {
      nav.open = false;
      nav.querySelector("summary").focus();
    }
  });
  $("gen-return-context").href = link("projects");
  if (!file) {
    const invalid = (params.get("project") && projectId !== params.get("project")) || params.get("file");
    stage($("stage-request"), "尚未就绪", "idle");
    $("target-meta").textContent = "尚无可选择的函数。";
    state($("target-empty"), invalid ? "error" : "empty", invalid ? "当前来源版本不可用" : "先选择源码版本",
      invalid ? "请核对链接中的项目和文件版本，或在 Explorer 重新选择。" : "在项目中心导入 Python 文件，再选择要生成测试的版本。");
    state($("suite-empty"), "", "暂无套件", "选择文件版本后可读取该版本的历史套件。");
    $("gen-return-context").hidden = false;
    announce($, invalid ? "当前项目或文件版本不匹配。" : "等待选择项目和文件版本。", Boolean(invalid));
    return;
  }
  const base = "/api/files/" + file.id;
  const [analysis, detail, savedRows] = await Promise.all([api(base + "/analysis"), api(base), api(base + "/suites")]);
  if (detail.project_id !== Number(projectId) || detail.id !== file.id || detail.sha256 !== file.sha256 ||
      detail.filename !== file.filename || detail.revision !== file.revision) {
    throw new Error("返回的源码与所选版本不一致。");
  }
  const {nodes} = buildGraph(analysis, detail);
  const functions = nodes.filter(node => node.topLevelEligible && [...node.qualified_name].length <= 256);
  const target = $("target");
  const search = $("target-search");
  const suites = $("suite");
  const byName = new Map(functions.map(node => [node.qualified_name, node]));
  let rows = [];
  let selectedSuite = "";
  let targetName = "";
  let suiteRead = 0;
  let running = false;

  const safeRows = incoming => incoming.filter(row => row.file_id === file.id);
  const findSuite = id => rows.find(row => String(row.id) === String(id));
  function syncUrl() {
    history.replaceState(null, "", link("generation", {symbol: targetName, suite: selectedSuite}) + location.hash);
  }
  function paintSuiteList(preferred) {
    selectedSuite = findSuite(preferred) ? String(preferred) : "";
    const placeholder = new Option(rows.length ? "选择历史测试套件" : "此版本尚无套件", "");
    suites.replaceChildren(placeholder, ...rows.map(row => new Option("#" + row.id + " · " + row.target + " · " + row.mode, row.id)));
    suites.value = selectedSuite;
    suites.disabled = running || !rows.length;
  }
  function paintTargets() {
    const term = search.value.trim().toLowerCase();
    const matches = functions.filter(node => node.qualified_name.toLowerCase().includes(term));
    const options = matches.map(node => new Option(node.qualified_name, node.qualified_name));
    if (targetName && !matches.some(node => node.qualified_name === targetName)) {
      options.unshift(new Option(targetName + "（当前目标）", targetName));
    }
    target.replaceChildren(...(options.length ? options : [new Option("没有匹配函数", "")]));
    target.value = targetName;
    target.disabled = running || !options.length;
    search.disabled = running || !functions.length;
    $("target-meta").textContent = functions.length ?
      (term ? matches.length + " 个匹配 / " : "") + functions.length + " 个可生成函数" :
      "当前版本没有可生成的模块顶层同步函数。";
    $("generate-button").disabled = !targetName || running;
  }
  function paintTarget() {
    const node = byName.get(targetName);
    $("target-preview").hidden = $("inspect-target").hidden = $("target-lines").hidden = !node;
    $("inspect-target-empty").hidden = Boolean(node);
    if (!node) {
      const error = analysis.error;
      const wanted = params.get("symbol");
      const at = error?.line != null ? "第 " + error.line + " 行：" : "";
      state($("target-empty"), error ? "error" : "", error ? "源码分析未通过" : "选择目标函数",
        error ? at + error.message : wanted && !byName.has(wanted) ?
          "链接中的函数不可生成，请选择当前版本的模块顶层同步函数。" :
          "生成模板仅接收唯一的模块顶层同步函数。");
      return;
    }
    $("target-empty").hidden = true;
    $("target-lines").textContent = "L" + node.start_line + "–" + node.end_line;
    $("target-filename").textContent = file.filename + " / " + node.qualified_name;
    $("target-signature").textContent = node.signature;
    $("target-docstring").textContent = node.docstring;
    $("target-docstring").hidden = !node.docstring;
    facts($("target-facts"), [
      ["函数限定名", node.qualified_name], ["源码行范围", node.start_line + "–" + node.end_line],
      ["参数数", node.parameters.length], ["返回标注", node.returns ?? "未声明"],
    ]);
    showCode($, {source: detail.source, view: "target-source", pager: "target-pager", copy: "copy-target",
      range: [node.start_line, node.end_line]});
  }
  function showSaved(saved) {
    $("suite-empty").hidden = true;
    $("suite-panel").hidden = false;
    const checked = saved.format_checked === true;
    const initial = saved.initial_run;
    const initialText = initial ? "首次 Pytest 运行 #" + initial.id + " · " + labelStatus(initial.status) : "尚无首次执行记录。";
    $("suite-detail").textContent = "#" + saved.id + " · " + saved.mode + " · " + (checked ? "语法检查通过" : "无检查通过记录");
    $("initial-status").textContent = initialText;
    $("initial-status").dataset.state = initial ? runTone(initial.status) : "idle";
    $("console-suite").textContent = "套件 #" + saved.id;
    $("console-suite").hidden = false;
    stage($("stage-static"), checked ? "已通过" : "无通过记录", checked ? "ok" : "idle");
    stage($("stage-run"), initial ? labelStatus(initial.status) + " #" + initial.id : "尚无记录", initial ? runTone(initial.status) : "idle");
    $("static-detail").textContent = checked ?
      "服务端已解析并编译生成源码，确认存在顶层 test_ 函数。" : "服务端未提供通过记录。";
    $("run-detail").textContent = initialText;
    $("suite-facts-empty").hidden = true;
    const provenance = [
      ["套件 ID", "#" + saved.id], ["函数限定名", saved.target], ["生成模式", saved.mode],
      ["来源文件", file.filename], ["文件版本", "v" + file.revision + " · #" + file.id],
      ["套件 SHA-256", saved.sha256],
    ];
    if (saved.created_at) provenance.push(["生成时间", saved.created_at]);
    facts($("suite-facts"), provenance);
    const suggestions = saved.suggestions.map(value => {
      const item = document.createElement("li");
      item.textContent = value;
      return item;
    });
    $("suggestions").replaceChildren(...suggestions);
    if (!suggestions.length) {
      const item = document.createElement("li");
      item.textContent = "暂无适用建议。";
      $("suggestions").append(item);
    }
    showCode($, {source: saved.source, view: "test-source", pager: "suite-pager", copy: "copy-suite"});
    const action = $("run-suite");
    action.href = link("runs", {suite: saved.id, run: initial?.id || ""});
    action.querySelector("span").textContent = initial ? "查看首次执行记录" : "前往 F04 执行此套件";
    action.hidden = false;
  }
  async function loadSuite(id, provided) {
    const reading = ++suiteRead;
    resetSuite($);
    $("gen-retry").hidden = true;
    const listed = findSuite(id);
    if (!listed) {
      state($("suite-empty"), id ? "error" : "", id ? "套件不属于当前版本" : "此版本尚未选择测试套件",
        id ? "请从当前文件版本的历史套件中选择。" : "生成并验证后，或选择历史套件，即可查看 Pytest 源码和验证结果。");
      return;
    }
    state($("suite-empty"), "loading", "正在读取套件 #" + listed.id, "正在核对生成源码与验证记录。");
    let saved;
    try {
      saved = provided || await api("/api/suites/" + listed.id);
      if (reading !== suiteRead) return;
      if (saved.id !== listed.id || saved.file_id !== file.id || saved.target !== listed.target ||
          saved.mode !== listed.mode || saved.sha256 !== listed.sha256) {
        throw new Error("套件与当前文件版本不一致。");
      }
      showSaved(saved);
    } catch (error) {
      if (reading === suiteRead) {
        state($("suite-empty"), "error", "读取套件失败", error.message);
        $("gen-retry").hidden = false;
        $("gen-retry").onclick = () => location.reload();
      }
      return;
    }
    const initial = saved.initial_run;
    if (!initial) return;
    try {
      const run = await api("/api/runs/" + initial.id);
      if (reading !== suiteRead) return;
      if (run.id !== initial.id || run.file_id !== file.id || run.suite_id !== saved.id ||
          run.project_id !== Number(projectId) || run.status !== initial.status) {
        throw new Error("运行记录与当前套件不一致。");
      }
      facts($("run-facts"), [
        ["运行 ID", "#" + run.id], ["通过", run.passed], ["失败", run.failed],
        ["错误", run.errors], ["跳过", run.skipped], ["耗时", run.duration_ms == null ? null : run.duration_ms + " ms"],
        ["运行记录时间", run.created_at],
      ]);
    } catch (error) {
      if (reading === suiteRead) $("run-detail").textContent += " 无法读取运行摘要。可在 F04 查看。";
    }
  }

  $("gen-version").hidden = false;
  $("gen-file-name").textContent = file.filename;
  $("gen-file-name").title = file.filename;
  $("gen-revision").textContent = "v" + file.revision + " · #" + file.id;
  rows = safeRows(savedRows);
  const wantedSuite = params.get("suite");
  paintSuiteList(wantedSuite || rows[0]?.id || "");
  const wantedTarget = params.get("symbol") || findSuite(selectedSuite)?.target || functions[0]?.qualified_name;
  targetName = byName.has(wantedTarget) ? wantedTarget : "";
  paintTargets();
  paintTarget();
  stage($("stage-request"), "等待操作", "idle");
  announce($, "正在查看 " + file.filename + " · v" + file.revision + " · 版本 #" + file.id + "。");
  search.oninput = paintTargets;
  target.onchange = () => {
    targetName = target.value;
    paintTargets();
    paintTarget();
    syncUrl();
  };
  suites.onchange = () => {
    selectedSuite = suites.value;
    syncUrl();
    void loadSuite(selectedSuite);
  };
  $("generate").onsubmit = async event => {
    event.preventDefault();
    if (running || !targetName) return;
    running = true;
    paintTargets();
    suites.disabled = true;
    stage($("stage-request"), "请求处理中", "pending");
    announce($, "正在提交 " + targetName + " 的生成与验证请求，等待服务返回结果。");
    try {
      const saved = await api(base + "/suites", {target: targetName, mode: MODE});
      if (saved.file_id !== file.id || saved.target !== targetName || saved.mode !== MODE) {
        throw new Error("生成响应与所选函数或来源版本不一致。");
      }
      rows = [saved, ...rows.filter(row => row.id !== saved.id)].sort((a, b) => b.id - a.id);
      paintSuiteList(saved.id);
      syncUrl();
      stage($("stage-request"), "套件已生成", "ok");
      announce($, "已取得套件 #" + saved.id + " 的生成结果。");
      await loadSuite(selectedSuite, saved);
    } catch (error) {
      if (error.status === 409) {
        stage($("stage-request"), "执行器忙", "warning");
        announce($, "执行器忙（HTTP 409）。稍后可重试；后端会复用内容相同的套件。", true);
        try {
          const existing = new Set(rows.map(row => row.id));
          rows = safeRows(await api(base + "/suites"));
          const added = rows.filter(row => !existing.has(row.id) && row.target === targetName && row.mode === MODE);
          paintSuiteList(added.length === 1 ? added[0].id : selectedSuite);
          syncUrl();
          await loadSuite(selectedSuite);
        } catch {
          announce($, "执行器忙（HTTP 409），暂时无法刷新套件列表。稍后可重试。", true);
        }
      } else {
        stage($("stage-request"), "请求失败", "error");
        announce($, error.message, true);
      }
    } finally {
      running = false;
      paintTargets();
      suites.disabled = !rows.length;
    }
  };
  await loadSuite(wantedSuite || selectedSuite);
}
