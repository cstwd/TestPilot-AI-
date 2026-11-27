import {bindCases, bindLog, duration, element, labelStatus, readout, runState, setStatus, setupPager} from "./run-evidence.js";
export {labelStatus, readout} from "./run-evidence.js";

// SQLite's NOCASE comparison folds only the ASCII letters.
export const sameFilename = (a, b) => {
  const fold = name => name.replace(/[A-Z]/g, char => char.toLowerCase());
  return fold(a) === fold(b);
};

function announce($, text, error = false) {
  $("notice").textContent = text;
  $("notice").toggleAttribute("data-error", error);
}

function emptyState(node, state, title, detail) {
  node.hidden = false;
  node.dataset.state = state;
  node.querySelector("h3").textContent = title;
  node.querySelector("p").textContent = detail;
}

function bindPanels($) {
  const nav = document.querySelector(".exec-mobile-nav");
  nav.onkeydown = event => {
    if (event.key === "Escape" && nav.open) {
      nav.open = false;
      nav.querySelector("summary").focus();
    }
  };
  const titles = {history: "运行历史", inspector: "用例详情"};
  const setPanel = (key, open) => {
    const button = $("toggle-" + key);
    const label = (open ? "折叠" : "展开") + titles[key];
    button.setAttribute("aria-expanded", String(open));
    button.setAttribute("aria-label", label);
    button.title = label;
    $(button.getAttribute("aria-controls")).hidden = !open;
    document.body.toggleAttribute("data-" + key + "-closed", !open);
  };
  for (const key of Object.keys(titles)) {
    const button = $("toggle-" + key);
    button.onclick = () => setPanel(key, button.getAttribute("aria-expanded") === "false");
  }
  return setPanel;
}

export function showRunsError($, error) {
  bindPanels($);
  $("run-result").hidden = true;
  $("execute").disabled = true;
  $("history-empty").textContent = "运行历史暂不可用。";
  $("exec-config-note").textContent = "请重新读取，或切换项目与文件。";
  emptyState($("run-empty"), "error", "执行上下文无法读取", error.message);
  setStatus($("exec-run-state"), ["读取失败", "error"]);
  setStatus($("request-state"), ["读取失败", "error"]);
  $("exec-retry").hidden = false;
  $("exec-retry").onclick = () => location.reload();
  announce($, error.message, true);
}

function fileLabel(row) {
  return row ? row.filename + " · v" + row.revision : "—";
}

function revisionLabel(row) {
  return row ? "v" + row.revision + " · #" + row.id : "—";
}

function displayRunTime(value) {
  if (!value || !Number.isFinite(Date.parse(value))) return "时间未记录";
  return new Date(value).toISOString().slice(0, 19).replace("T", " ") + " UTC";
}

function bindHistory($, records, byId, opened, details, route) {
  const search = $("history-search");
  const status = $("history-status");
  const host = $("run-history");
  const pager = setupPager($("history-pager"), 6, render);

  function render() {
    host.replaceChildren();
    const term = search.value.trim().toLowerCase();
    const filtered = records.filter(row => (!status.value || row.status === status.value) &&
      (!term || ("#" + row.id + " " + (byId.get(row.file_id)?.filename || "")).toLowerCase().includes(term)));
    $("history-empty").hidden = Boolean(filtered.length);
    $("history-empty").textContent = records.length ? "没有匹配的运行。" : "此项目暂无运行记录。";
    for (const row of pager.slice(filtered)) {
      const item = element("a", "tree-row");
      item.href = route(row);
      item.dataset.runId = row.id;
      if (row.id === opened?.id) item.setAttribute("aria-current", "page");
      const pill = element("span", "exec-status");
      setStatus(pill, runState(row));
      const line = element("div", "exec-history-line");
      line.append(element("strong", "", "运行 #" + row.id), pill);
      const time = element("time", "exec-history-time", displayRunTime(row.created_at));
      if (row.created_at) {
        time.dateTime = row.created_at;
        time.title = row.created_at;
      }
      const stats = element("span", "exec-history-counts", "读取用例统计…");
      item.append(line, element("span", "exec-history-file", fileLabel(byId.get(row.file_id))), time, stats);
      host.append(item);
      void details(row).then(result => {
        if (!item.isConnected) return;
        setStatus(pill, runState(result));
        const values = [["通过", result.passed], ["失败", result.failed], ["错误", result.errors], ["跳过", result.skipped]];
        stats.textContent = values.every(([, value]) => value == null) ? "用例统计未记录" :
          values.map(([name, value]) => name + " " + (value ?? "—")).join(" / ");
      }).catch(() => {
        if (item.isConnected) stats.textContent = "用例统计暂不可用";
      });
    }
  }
  search.disabled = status.disabled = !records.length;
  search.oninput = status.onchange = () => { pager.reset(); render(); };
  render();
}

export async function showRuns({$, api, link, params, files, projectId, fileId}) {
  const setPanel = bindPanels($);
  const showLog = bindLog($, (text, error) => announce($, text, error));
  const showCases = bindCases($, link, setPanel);
  const fileSelect = $("file");
  const originSelect = $("suite-file");
  const suiteSelect = $("run-suite");
  let current = files.find(row => String(row.id) === fileId);
  let selectedSuite;
  let viewed;
  let pending = false;

  function paintContext(run, suite = selectedSuite) {
    const subject = run ? fileIndex.get(run.file_id) : current;
    const origin = suite && fileIndex.get(suite.file_id);
    const projectName = $("project").selectedOptions[0]?.textContent;
    const labels = [
      ["exec-project", projectId && projectName ? projectName + " · #" + projectId : "—"],
      ["exec-filename", subject?.filename || "—"], ["exec-revision", revisionLabel(subject)],
      ["exec-suite", suite ? "#" + suite.id + " · " + suite.target : "—"], ["exec-suite-origin", revisionLabel(origin)],
    ];
    for (const [id, value] of labels) {
      $(id).textContent = value;
      $(id).title = value;
    }
    $("exec-run-id").textContent = run ? "#" + run.id : "—";
    setStatus($("exec-run-state"), run ? runState(run) : pending ? ["请求等待中", "pending"] : ["尚未选择运行", "idle"]);
  }

  const fileIndex = new Map(files.map(row => [row.id, row]));
  const explicitContextMismatch = (params.get("project") && params.get("project") !== projectId) ||
    (params.get("file") && !current);
  if (explicitContextMismatch) {
    showRunsError($, new Error("链接中的项目或被测版本不可用。请重新选择。"));
    return;
  }
  if (!projectId) {
    paintContext();
    $("history-empty").textContent = "选择项目后可查看运行历史。";
    $("exec-config-note").textContent = "请先在项目中心创建项目、导入文件并生成套件。";
    emptyState($("run-empty"), "", "先准备测试套件", "在项目中心导入源码，再前往 F03 生成测试。");
    setStatus($("request-state"), ["尚未执行", "idle"]);
    announce($, "等待选择项目。");
    return;
  }

  const historyRows = await api("/api/projects/" + projectId + "/runs");
  const requestedRun = params.get("run");
  const requestedSuite = params.get("suite");
  const requestedOrigin = params.get("suite_file");
  const picked = requestedRun ? historyRows.find(row => String(row.id) === requestedRun) :
    requestedOrigin && !requestedSuite ? null : historyRows.find(row => row.file_id === current?.id &&
      (!requestedSuite || String(row.suite_id) === requestedSuite));
  if (picked) {
    current = fileIndex.get(picked.file_id);
    if (!current) throw new Error("此运行的被测版本不属于当前项目。");
    fileSelect.value = String(current.id);
    document.querySelectorAll("[data-dest]").forEach(anchor => { anchor.href = link(anchor.dataset.dest); });
  }
  const recordRoute = row => link("runs", {file: row.file_id, suite: row.suite_id, run: row.id});
  const cache = new Map();
  function details(row) {
    if (!cache.has(row.id)) {
      const loading = api("/api/runs/" + row.id).then(record => {
        if (record.id !== row.id || record.project_id !== Number(projectId) || record.file_id !== row.file_id ||
            record.suite_id !== row.suite_id || record.status !== row.status) {
          throw new Error("运行记录与项目、套件或版本不一致。");
        }
        return record;
      }).catch(error => { cache.delete(row.id); throw error; });
      cache.set(row.id, loading);
    }
    return cache.get(row.id);
  }
  bindHistory($, historyRows, fileIndex, picked, details, recordRoute);

  const suiteKey = picked ? String(picked.suite_id) : requestedSuite;
  let expectedSuite;
  let setupError = "";
  const revisions = current ? files.filter(row => sameFilename(row.filename, current.filename)) : [];
  if (suiteKey) {
    try {
      const suite = await api("/api/suites/" + encodeURIComponent(suiteKey));
      if (String(suite.id) !== suiteKey || !revisions.some(row => row.id === suite.file_id)) {
        throw new Error("套件来源必须属于当前项目的同名文件。");
      }
      expectedSuite = suite;
    } catch (error) {
      setupError = error.message;
    }
  }
  const sourceId = expectedSuite?.file_id ?? (requestedOrigin ? Number(requestedOrigin) : current?.id);
  const origin = revisions.find(row => row.id === sourceId);
  if (!origin && requestedOrigin) setupError = "套件来源版本不可用，请重新选择。";
  const suites = origin ? (await api("/api/files/" + origin.id + "/suites")).filter(row => row.file_id === origin.id) : [];
  if (expectedSuite && !suites.some(row => row.id === expectedSuite.id && row.sha256 === expectedSuite.sha256 &&
      row.target === expectedSuite.target && row.mode === expectedSuite.mode)) {
    expectedSuite = undefined;
    setupError = "套件详情与来源版本清单不一致。";
  }
  selectedSuite = expectedSuite ? suites.find(row => row.id === expectedSuite.id) : suiteKey ? undefined : suites[0];
  const originPlaceholder = new Option("重新选择来源版本", "");
  originSelect.replaceChildren(...(origin ? [] : [originPlaceholder]),
    ...revisions.map(row => new Option(fileLabel(row) + " · #" + row.id, row.id)));
  originSelect.value = origin ? String(origin.id) : "";
  suiteSelect.replaceChildren(new Option(suites.length ? "选择测试套件" : "此来源版本暂无套件", ""),
    ...suites.map(row => new Option("#" + row.id + " · " + row.target, row.id)));
  suiteSelect.value = selectedSuite ? String(selectedSuite.id) : "";

  function configure() {
    if (!pending) {
      const note = setupError || (selectedSuite ? "套件 " + revisionLabel(fileIndex.get(selectedSuite.file_id)) +
        " → 被测 " + revisionLabel(current) : "从当前项目的同名文件修订中选择一个已保存套件。");
      $("exec-config-note").textContent = note;
      $("exec-config-note").toggleAttribute("data-error", Boolean(setupError));
    }
    const projectSelect = $("project");
    projectSelect.disabled = pending || !projectSelect.value;
    fileSelect.disabled = pending || !files.length;
    originSelect.disabled = pending || !revisions.length;
    suiteSelect.disabled = pending || !suites.length;
    $("execute").disabled = pending || !selectedSuite || !current;
    $("exec-history-content").inert = pending;
  }

  function paintRun(run) {
    $("run-result").hidden = !run;
    $("run-empty").hidden = Boolean(run);
    paintContext(run, run ? expectedSuite : selectedSuite);
    showCases(run);
    showLog(run, pending);
    if (!run) {
      emptyState($("run-empty"), pending ? "loading" : "", pending ? "等待执行响应" : "尚无运行结果",
        pending ? "受限 Pytest 完成并保存后，将在此显示真实结果。" : "执行当前套件，或从运行历史选择已保存记录。");
      return;
    }
    $("run-identity").textContent = "运行 #" + run.id + " · 套件 #" + run.suite_id + " · " + current.filename + " v" + current.revision;
    readout($("run-summary"), [
      ["Passed / 通过", run.passed, "ok"], ["Failed / 失败", run.failed, run.failed ? "error" : ""],
      ["Error / 错误", run.errors, run.errors ? "error" : ""],
      ["Skipped / 跳过", run.skipped, run.skipped ? "warning" : ""], ["执行耗时", duration(run.duration_ms)],
    ]);
    $("coverage").textContent = run.coverage_pct == null ? "行覆盖率未采集" :
      "行覆盖率 " + run.coverage_pct + "%（" + run.covered_lines + "/" + run.total_lines + " 行）";
    $("to-bugs").href = link("bugs", {file: run.file_id, run: run.id});
    $("to-report").href = link("reports", {file: run.file_id, run: run.id});
  }

  originSelect.onchange = () => location.assign(link("runs", {suite_file: originSelect.value}));
  fileSelect.onchange = () => {
    const next = fileIndex.get(Number(fileSelect.value));
    const preserve = selectedSuite && next && current && sameFilename(next.filename, current.filename);
    location.assign(link("runs", {suite: preserve ? selectedSuite.id : ""}));
  };
  suiteSelect.onchange = () => {
    selectedSuite = suites.find(row => String(row.id) === suiteSelect.value);
    setupError = "";
    configure();
    if (!viewed) {
      paintContext();
      history.replaceState(null, "", link("runs", {suite: selectedSuite?.id, suite_file: origin?.id}));
    }
  };

  if (picked) {
    try {
      if (expectedSuite?.id !== picked.suite_id) throw new Error(setupError || "无法验证套件的来源版本。");
      viewed = await details(picked);
      paintRun(viewed);
      if (requestedRun) history.replaceState(null, "", recordRoute(picked));
      setStatus($("request-state"), ["记录已载入", "idle"]);
      announce($, "已载入运行 #" + viewed.id + "。");
    } catch (error) {
      paintRun(null);
      emptyState($("run-empty"), "error", "无法显示所选运行", error.message);
      setStatus($("request-state"), ["读取失败", "error"]);
      $("exec-retry").hidden = false;
      $("exec-retry").onclick = () => location.reload();
      announce($, error.message, true);
    }
  } else {
    paintRun(null);
    if (requestedRun) emptyState($("run-empty"), "error", "运行不属于当前项目", "请从左侧选择本项目的运行记录。");
    setStatus($("request-state"), requestedRun ? ["运行不可用", "error"] : ["尚未执行", "idle"]);
    announce($, requestedRun ? "链接中的运行不可用。" : "选择套件执行，或打开历史运行。", Boolean(requestedRun));
  }

  $("start-run").onsubmit = async event => {
    event.preventDefault();
    if (pending || !selectedSuite || !current) return;
    const suiteId = selectedSuite.id;
    const subjectId = current.id;
    pending = true;
    setStatus($("request-state"), ["请求等待中", "pending"]);
    $("exec-config-note").textContent = "请求已发送。等待受限执行器返回已保存结果。";
    $("exec-config-note").removeAttribute("data-error");
    announce($, "正在等待本次 Pytest 请求。");
    configure();
    paintRun(null);
    try {
      const result = await api("/api/suites/" + suiteId + "/runs", {file_id: subjectId});
      if (result.file_id !== subjectId || result.suite_id !== suiteId || result.project_id !== Number(projectId) ||
          !Number.isInteger(result.id) || result.id < 1) {
        throw new Error("服务返回的运行身份与此次执行配置不一致。");
      }
      location.assign(recordRoute(result));
    } catch (error) {
      pending = false;
      configure();
      paintRun(viewed);
      const busy = error.status === 409;
      setStatus($("request-state"), busy ? ["并发冲突", "warning"] : ["请求失败", "error"]);
      announce($, busy ? "HTTP 409 · 执行器忙，请稍后重试。" : error.message, true);
    }
  };
  configure();
}
