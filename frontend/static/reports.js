import {sameFilename} from "./runs.js";
import {duration, element, readout, runState, setStatus, setupPager} from "./run-evidence.js";
import {issueLabel, metricValues, renderMetrics} from "./report-metrics.js";

const fileLabel = row => row.filename + " · v" + row.revision + " · #" + row.id;
const runLabel = (row, files) => "运行 #" + row.id + (files.has(row.file_id) ? " · " + fileLabel(files.get(row.file_id)) : "");
const defectState = status => [issueLabel(status), status === "resolved" ? "ok" : status === "open" ? "warning" : "idle"];

function timeLabel(value) {
  return typeof value === "string" && Number.isFinite(Date.parse(value)) ?
    new Date(value).toISOString().slice(0, 19).replace("T", " ") + " UTC" : "未记录";
}

function announce($, text, error = false) {
  $("notice").textContent = text;
  $("notice").toggleAttribute("data-error", error);
}

function emptyState($, kind, title, detail, href) {
  const node = $("quality-empty");
  node.hidden = false;
  node.dataset.state = kind;
  node.querySelector("h3").textContent = title;
  node.querySelector("p").textContent = detail;
  node.querySelector("a")?.remove();
  if (href) {
    const go = element("a", "", "前往测试执行");
    go.href = href;
    node.append(go);
  }
}

function bindMobileMenu() {
  const nav = document.querySelector(".quality-mobile-nav");
  nav.onkeydown = event => {
    if (event.key === "Escape" && nav.open) {
      nav.open = false;
      nav.querySelector("summary").focus();
    }
  };
}

export function showReportsError($, error) {
  bindMobileMenu();
  if (!$("report-history").childElementCount) $("quality-history-empty").textContent = "没有可显示的运行历史。";
  emptyState($, "error", "无法读取质量报告", error.message);
  $("retry-report").hidden = false;
  $("retry-report").onclick = () => location.reload();
  announce($, error.message, true);
}

function bindHistory($, rows, files, selected, route) {
  const fileSelect = $("report-file-filter");
  const statusSelect = $("report-status-filter");
  const fileIds = new Set(rows.map(row => row.file_id));
  fileSelect.replaceChildren(new Option("全部版本", ""), ...[...files.values()].filter(row => fileIds.has(row.id))
    .map(row => new Option(fileLabel(row), row.id)));
  const states = [...new Map(rows.map(row => [row.status, runState(row)[0]])).entries()];
  statusSelect.replaceChildren(new Option("全部状态", ""), ...states.map(([value, text]) => new Option(text, value)));
  fileSelect.disabled = statusSelect.disabled = !rows.length;
  const list = $("report-history");
  const pager = setupPager($("report-history-pager"), 8, render, rows.indexOf(selected));
  function render() {
    const filtered = rows.filter(row => (!fileSelect.value || String(row.file_id) === fileSelect.value) &&
      (!statusSelect.value || statusSelect.value === row.status));
    $("quality-history-empty").hidden = Boolean(filtered.length);
    $("quality-history-empty").textContent = rows.length ? "没有匹配的运行。" : "此项目暂无运行记录。";
    const items = document.createDocumentFragment();
    for (const row of pager.slice(filtered)) {
      const a = element("a", "tree-row");
      a.href = route(row);
      a.dataset.runId = row.id;
      if (row.id === selected?.id) a.setAttribute("aria-current", "page");
      const header = element("span", "quality-run-label");
      const badge = element("span", "quality-badge");
      setStatus(badge, runState(row));
      header.append(element("strong", "", "运行 #" + row.id), badge);
      const time = element("time", "quality-run-time", timeLabel(row.created_at));
      if (row.created_at) time.dateTime = row.created_at;
      a.append(header, element("span", "quality-run-file", files.has(row.file_id) ?
        fileLabel(files.get(row.file_id)) : "文件 #" + row.file_id), time);
      items.append(a);
    }
    list.replaceChildren(items);
  }
  fileSelect.onchange = statusSelect.onchange = () => { pager.reset(); render(); };
  render();
}

function paintInspector($, data, link) {
  const {project, run, source, suite} = data;
  readout($("quality-identities"), [
    ["运行 ID", "#" + run.id], ["项目 ID", "#" + project.id], ["文件 ID", "#" + source.id],
    ["文件版本", "v" + source.revision], ["测试套件 ID", "#" + suite.id], ["套件来源文件 ID", "#" + suite.file_id],
    ["原始运行状态", run.status], ["执行耗时", duration(run.duration_ms)],
  ]);
  $("report-run").href = link("runs", {file: source.id, suite: suite.id, run: run.id});
  $("report-hashes").textContent = "源码 SHA-256\n" + source.sha256 + "\n\n套件 SHA-256\n" + suite.sha256 +
    "\n\n套件 #" + suite.id + " · " + suite.mode + " · 来源文件 #" + suite.file_id;
  $("quality-defect-caveat").textContent = "包含本次原始失败或回归关联的缺陷。状态为本次读取时的记录。";
  const list = $("report-bugs");
  const entries = document.createDocumentFragment();
  for (const bug of data.bugs) {
    const article = element("article", "quality-issue");
    article.dataset.bugId = bug.id;
    const header = element("div", "quality-issue-head");
    const anchor = element("a", "quality-link", "缺陷 #" + bug.id + " · " + bug.title);
    anchor.href = link("bugs", {file: bug.file_id, bug: bug.id, run: bug.run_id, nodeid: bug.nodeid});
    const badge = element("span", "quality-badge");
    setStatus(badge, defectState(bug.status));
    header.append(anchor, badge);
    article.append(header, element("p", "", "原始运行 #" + bug.run_id + " · " + bug.nodeid));
    if (bug.regressions.length) {
      const history = element("ul", "quality-regressions");
      history.setAttribute("aria-label", "已保存回归判定");
      for (const row of bug.regressions) {
        const item = element("li");
        item.dataset.regressionId = row.run_id;
        const open = element("a", "quality-link", "运行 #" + row.run_id + " · v" + row.revision + " (#" + row.file_id + ")");
        open.href = link("runs", {file: row.file_id, suite: bug.suite_id, run: row.run_id});
        const status = element("span", "quality-badge");
        setStatus(status, ["判定 " + issueLabel(row.status), defectState(row.status)[1]]);
        item.append(open, status);
        history.append(item);
      }
      article.append(history);
    } else article.append(element("p", "", "暂无回归记录"));
    entries.append(article);
  }
  list.replaceChildren(data.bugs.length ? entries : element("p", "quality-muted", "没有与此运行关联的缺陷。"));
}

function compareColumns($, current, other) {
  const heading = data => "#" + data.run.id + " · " + data.source.filename + " v" + data.source.revision;
  $("compare-current").textContent = heading(current);
  $("compare-other").textContent = heading(other);
  const values = report => {
    const q = report.quality, display = metricValues(q);
    return [
      display.rate + " · " + q.passed + "/" + display.measured,
      q.total,
      q.passed + " / " + q.failed + " / " + q.errors + " / " + q.skipped,
      display.coverage + " · " + display.base,
    ];
  };
  const a = values(current), b = values(other);
  const rows = ["测试通过率", "收录用例", "通过 / 失败 / 错误 / 跳过", "行覆盖率"].map((name, i) => {
    const line = element("tr");
    const label = element("th", "", name);
    label.scope = "row";
    line.append(label, element("td", "", a[i]), element("td", "", b[i]));
    return line;
  });
  $("compare-metrics").replaceChildren(...rows);
  $("quality-compare-results").hidden = false;
}

function bindComparison($, data, rows, files, loadReport) {
  const available = rows.filter(row => row.id !== data.run.id && row.suite_id === data.suite.id &&
    files.has(row.file_id) && sameFilename(files.get(row.file_id).filename, data.source.filename));
  if (!available.length) return;
  const select = $("quality-compare-select");
  const message = $("quality-compare-message");
  select.replaceChildren(new Option("选择对照运行", ""), ...available.map(row => new Option(runLabel(row, files), row.id)));
  $("quality-comparison").hidden = false;
  let sequence = 0;
  select.onchange = async () => {
    const attempt = ++sequence;
    const row = available.find(row => String(row.id) === select.value);
    $("quality-compare-results").hidden = true;
    if (!row) {
      message.textContent = "比较范围为同项目、同名文件、同套件。各列保留自己的分母。";
      return;
    }
    message.textContent = "正在读取运行 #" + row.id + " 的报告…";
    try {
      const other = await loadReport(row);
      if (attempt !== sequence) return;
      compareColumns($, data, other);
      message.textContent = "两个已保存报告独立列出。每列使用自己的用例和覆盖率分母。";
    } catch (error) {
      if (attempt === sequence) message.textContent = "无法读取对照报告：" + error.message;
    }
  };
}

function bindReportActions($, data, route, initialHtml) {
  const json = $("export-report");
  // Pin the download to this rendered read snapshot. The original public /export endpoint
  // remains available for callers that ask the server for a fresh read.
  json.href = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2) + "\n"], {type: "application/json;charset=utf-8"}));
  json.download = "testpilot-run-" + data.run.id + ".json";
  const drawer = $("metric-notes-drawer");
  $("open-metric-notes").onclick = () => drawer.showModal();
  function setView(html) {
    document.body.dataset.reportView = html ? "html" : "workspace";
    document.title = html ? "运行 #" + data.run.id + " · HTML 质量报告 · TestPilot AI" : "质量分析 · TestPilot AI";
  }
  function navigate(html) {
    setView(html);
    history.pushState(null, "", route(html));
    window.scrollTo(0, 0);
    (html ? $("back-to-quality") : $("html-report")).focus();
  }
  $("html-report").onclick = () => navigate(true);
  $("back-to-quality").onclick = () => navigate(false);
  $("print-report").onclick = () => window.print();
  window.addEventListener("popstate", () => setView(new URLSearchParams(location.search).get("view") === "html"));
  setView(initialHtml);
  history.replaceState(null, "", route(initialHtml));
  $("quality-actions").hidden = false;
}

export async function showReports({$, api, link, params, projectId, files}) {
  bindMobileMenu();
  if (!projectId) {
    $("quality-history-empty").textContent = "请选择项目。";
    emptyState($, "", "先选择项目", "选择包含已保存运行的项目，或先执行一次测试。");
    announce($, params.get("project") ? "链接中的项目不可用，请重新选择。" : "等待选择项目。", Boolean(params.get("project")));
    return;
  }
  const index = new Map(files.map(row => [row.id, row]));
  const rows = await api("/api/projects/" + projectId + "/runs");
  const requested = params.get("run"), requestedFile = params.get("file");
  const current = requested ? rows.find(row => String(row.id) === requested) :
    requestedFile ? rows.find(row => String(row.file_id) === requestedFile) : rows[0];
  const route = (row, html) => link("reports", {file: row.file_id, run: row.id, view: html ? "html" : ""});
  bindHistory($, rows, index, current, route);
  if (!current) {
    if (requested) throw new Error("指定运行不属于当前项目，或记录不存在。");
    const info = requestedFile ? "所选文件版本尚无运行。可选择其他版本或执行测试。" : "项目尚无运行记录。";
    emptyState($, "", "暂无质量报告", info, link("runs"));
    announce($, info);
    return;
  }
  async function loadReport(row) {
    const file = index.get(row.file_id);
    const snapshot = await api("/api/runs/" + row.id + "/report");
    if (!file || snapshot.schema !== "testpilot.quality.v1" || snapshot.project.id !== Number(projectId) ||
        snapshot.run.id !== row.id || snapshot.run.status !== row.status || snapshot.source.id !== file.id ||
        snapshot.source.filename !== file.filename || snapshot.source.revision !== file.revision ||
        snapshot.source.sha256 !== file.sha256 || snapshot.suite.id !== row.suite_id) {
      throw new Error("返回的报告与所选项目、运行、文件版本或套件不一致。");
    }
    return snapshot;
  }
  const data = await loadReport(current);
  const {project, run, source, suite} = data;
  $("file").value = String(source.id);
  document.querySelectorAll("[data-dest]").forEach(a => { a.href = link(a.dataset.dest); });
  $("quality-run-number").textContent = "运行 #" + run.id;
  setStatus($("quality-run-status"), runState({...run, log: data.log, cases: data.cases}));
  $("report-origin").textContent = source.filename + " v" + source.revision;
  $("quality-context").textContent = project.name + " · 文件 #" + source.id + " · 套件 #" + suite.id + " / " + suite.target +
    " · 运行记录时间 " + timeLabel(run.created_at);
  $("assessment").textContent = data.quality.assessment;
  renderMetrics($, data);
  paintInspector($, data, link);
  bindComparison($, data, rows, index, loadReport);
  bindReportActions($, data, html => route(current, html), params.get("view") === "html");
  $("quality-empty").hidden = true;
  $("report").hidden = false;
  announce($, "已读取运行 #" + run.id + " 的质量报告。HTML 与下载共享当前快照。");
}
