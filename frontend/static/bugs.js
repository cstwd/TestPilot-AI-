import {sameFilename} from "./runs.js";
import {duration, element, labelStatus, readout, runState, setStatus} from "./run-evidence.js";
import {assertionEvidence, renderDiff} from "./bug-evidence.js";
import {bindAiRepair} from "./bug-repair.js";

const issueLabels = {open: "待修复", resolved: "已解决", verified: "已验证", closed: "已关闭"};
const issueLabel = status => issueLabels[status] || status;
const issueState = status => [issueLabel(status), status === "resolved" ? "ok" : status === "open" ? "warning" : "idle"];
const fileLabel = row => row.filename + " · v" + row.revision + " · #" + row.id;
const versionLabel = row => row ? "v" + row.revision + " · #" + row.id : "—";
const idLabel = id => id == null ? "—" : "#" + id;

function message($, value, error = false) {
  $("notice").textContent = value;
  $("notice").toggleAttribute("data-error", error);
}

function state(node, kind, title, detail) {
  node.hidden = false;
  node.dataset.state = kind;
  node.querySelector("h3").textContent = title;
  node.querySelector("p").textContent = detail;
}

function bindPanels() {
  const buttons = document.querySelectorAll(".bug-panel-nav button");
  const select = panel => {
    document.body.dataset.bugPanel = panel;
    for (const button of buttons) button.setAttribute("aria-pressed", String(button.dataset.panel === panel));
  };
  for (const button of buttons) button.onclick = () => select(button.dataset.panel);
  return select;
}

export function showBugsError($, error) {
  bindPanels();
  $("issue-list-empty").textContent = "缺陷列表暂不可用。";
  state($("issues-empty"), "error", "无法读取缺陷上下文", error.message);
  $("retry-bugs").hidden = false;
  $("retry-bugs").onclick = () => location.reload();
  message($, error.message, true);
}

function isDefectCase(item) {
  return ["failed", "error"].includes(item.outcome) && item.nodeid.includes("::") && [...item.nodeid].length <= 2048;
}

function options(select, rows, title, selected, empty) {
  select.replaceChildren(...(rows.length ? rows.map(row => new Option(title(row), row.id)) : [new Option(empty, "")]));
  select.value = selected ? String(selected) : "";
  select.disabled = !rows.length;
}

function bindIssues($, issues, selectedId, href) {
  const search = $("issue-search");
  const status = $("issue-status");
  status.replaceChildren(new Option("全部状态", ""), ...[...new Set(issues.map(issue => issue.status))]
    .map(value => new Option(issueLabel(value), value)));
  function render() {
    const term = search.value.trim().toLowerCase();
    const filtered = issues.filter(row => (!status.value || row.status === status.value) &&
      (!term || [row.title, "#" + row.id, "运行 #" + row.run_id, row.nodeid].join(" ").toLowerCase().includes(term)));
    const rows = document.createDocumentFragment();
    for (const issue of filtered) {
      const a = element("a", "tree-row");
      a.href = href(issue);
      a.dataset.issueId = issue.id;
      if (issue.id === selectedId) a.setAttribute("aria-current", "page");
      const top = element("div", "bug-issue-top");
      const badge = element("span", "bug-pill");
      setStatus(badge, issueState(issue.status));
      top.append(element("span", "", "#" + issue.id), badge);
      const node = element("code", "bug-issue-node", issue.nodeid);
      node.title = issue.nodeid;
      a.append(top, element("p", "bug-issue-title", issue.title), element("span", "bug-issue-line", "来源运行 #" + issue.run_id), node);
      rows.append(a);
    }
    $("issue-list").replaceChildren(rows);
    $("issue-list-empty").hidden = Boolean(filtered.length);
    $("issue-list-empty").textContent = issues.length ? "没有匹配的缺陷。" : "此项目尚无登记缺陷。";
  }
  search.disabled = status.disabled = !issues.length;
  search.oninput = status.onchange = render;
  render();
}

export async function showBugs({$, api, link, syncModuleLinks, params, files, projectId}) {
  const selectPanel = bindPanels();
  if (!projectId) {
    selectPanel("explorer");
    $("issue-list-empty").textContent = "选择项目后查看缺陷。";
    state($("issues-empty"), "empty", "先选择项目", "选择含有真实失败运行的项目，或先执行测试。");
    message($, params.get("project") ? "链接中的项目不可用，请重新选择。" : "等待选择项目。", Boolean(params.get("project")));
    return;
  }
  const index = new Map(files.map(row => [row.id, row]));
  const base = "/api/projects/" + projectId;
  const [runRows, issues] = await Promise.all([api(base + "/runs"), api(base + "/bugs")]);
  const failures = runRows.filter(row => ["failed", "error"].includes(row.status));
  const byRun = new Map(runRows.map(row => [row.id, row]));
  const routeToIssue = (issue, version = issue.file_id) => link("bugs", {file: version, bug: issue.id, run: issue.run_id, nodeid: issue.nodeid});
  const requestedId = params.get("bug");
  const requestedRun = params.get("run");
  const requestedNode = params.get("nodeid");
  const intake = params.has("entry");
  const runCache = new Map();

  function readRun(id) {
    const listed = byRun.get(id);
    if (!listed) return Promise.reject(new Error("运行不属于当前项目。"));
    if (!runCache.has(id)) {
      runCache.set(id, api("/api/runs/" + id).then(run => {
        if (run.id !== id || run.project_id !== Number(projectId) || run.file_id !== listed.file_id ||
            run.suite_id !== listed.suite_id || run.status !== listed.status) {
          throw new Error("返回的运行与原始记录身份不一致。");
        }
        return run;
      }).catch(error => { runCache.delete(id); throw error; }));
    }
    return runCache.get(id);
  }

  $("open-intake").href = link("bugs", {file: "", entry: "1"});
  let issue = requestedId ? issues.find(row => String(row.id) === requestedId) :
    !requestedRun && !intake ? issues[0] : undefined;
  let originalRun, selectedCase;
  if (!issue && !requestedId) {
    const row = requestedRun ? failures.find(run => String(run.id) === requestedRun) : failures[0];
    if (row) {
      originalRun = await readRun(row.id);
      const eligible = originalRun.cases.filter(isDefectCase);
      selectedCase = requestedNode ? eligible.find(item => item.nodeid === requestedNode) : eligible[0];
      if (selectedCase && !intake) {
        issue = issues.find(saved => saved.run_id === row.id && saved.nodeid === selectedCase.nodeid);
      }
    }
  }
  bindIssues($, issues, issue?.id, routeToIssue);
  if (requestedId && !issue) throw new Error("该缺陷不属于当前项目，或记录不存在。");
  const issueSummary = issue;
  if (issue) {
    issue = await api("/api/bugs/" + issue.id);
    if (issue.id !== issueSummary.id || issue.project_id !== Number(projectId) || issue.run_id !== issueSummary.run_id ||
        issue.file_id !== issueSummary.file_id || issue.suite_id !== issueSummary.suite_id || issue.nodeid !== issueSummary.nodeid) {
      throw new Error("返回的缺陷详情与项目清单不一致。");
    }
    originalRun = await readRun(issue.run_id);
    selectedCase = originalRun.cases.find(item => item.nodeid === issue.nodeid && isDefectCase(item));
    if (!selectedCase || originalRun.file_id !== issue.file_id || originalRun.suite_id !== issue.suite_id ||
        !["failed", "error"].includes(originalRun.status)) throw new Error("缺陷关联的原始证据无法核对。");
  }
  const original = originalRun && index.get(originalRun.file_id);
  if (originalRun && !original) throw new Error("原始被测版本不在当前项目中。");
  let suite, suiteOrigin;
  let candidate, compared, selectedRegression;
  let waiting = false, compareSequence = 0, regressionSequence = 0;
  if (originalRun) {
    suite = await api("/api/suites/" + originalRun.suite_id);
    suiteOrigin = index.get(suite.file_id);
    if (suite.id !== originalRun.suite_id || !suiteOrigin || !sameFilename(suiteOrigin.filename, original.filename)) {
      throw new Error("原始套件和被测文件的版本关系无法核对。");
    }
  }

  const regressions = () => issue?.regressions || [];
  function updateIdentity() {
    readout($("identity-facts"), [
      ["项目 ID", idLabel(projectId)], ["文件 ID（原始）", idLabel(original?.id)],
      ["原始版本", versionLabel(original)], ["候选版本", versionLabel(candidate)],
      ["套件 ID", idLabel(suite?.id)], ["套件来源", versionLabel(suiteOrigin)],
      ["原始运行 ID", idLabel(originalRun?.id)], ["回归运行 ID", idLabel(selectedRegression)],
    ]);
    $("inspect-nodeid").textContent = selectedCase?.nodeid || "—";
  }
  function paintOriginal() {
    $("original-evidence").hidden = !originalRun;
    if (!originalRun) return;
    syncModuleLinks({file: original.id});
    $("original-run").href = link("runs", {file: original.id, suite: suite.id, run: originalRun.id});
    setStatus($("original-outcome"), runState(originalRun));
    $("failure-node").textContent = "运行 #" + originalRun.id + " · 套件 #" + suite.id + " · " + fileLabel(original) +
      (selectedCase ? " · " + selectedCase.nodeid : "");
    const evidence = selectedCase && assertionEvidence(originalRun, selectedCase);
    $("original-assertion").hidden = !evidence;
    $("original-assertion").textContent = evidence?.text || "";
    $("assertion-status").textContent = evidence ? (evidence.structured ? "原始运行保存的断言证据。" : "原始 Pytest 日志中的断言片段。") :
      "该用例没有可单独核对的断言片段。可查阅保存的原始运行日志。";
    $("original-log-box").hidden = !originalRun.log;
    $("original-log").textContent = originalRun.log || "";
    $("open-suite").disabled = false;
    $("suite-drawer-meta").textContent = "套件 #" + suite.id + " · " + suite.target + " · " + suite.mode + " · " + fileLabel(suiteOrigin);
    $("suite-drawer-sha").textContent = "SHA-256 " + suite.sha256;
    $("suite-drawer-source").textContent = suite.source;
    $("open-suite").onclick = () => $("suite-drawer").showModal();
  }
  paintOriginal();
  updateIdentity();

  if (!issue) {
    $("intake-panel").hidden = false;
    $("issues-empty").hidden = true;
    const runSelect = $("bug-run"), nodeSelect = $("nodeid");
    options(runSelect, failures, row => "#" + row.id + " · " + labelStatus(row.status), originalRun?.id, "没有失败运行");
    const cases = (originalRun?.cases || []).filter(isDefectCase);
    options(nodeSelect, cases.map(item => ({id: item.nodeid})), row => row.id, selectedCase?.nodeid, "无可登记失败用例");
    const goToCase = (run, nodeid) => location.assign(link("bugs", {file: "", run, nodeid}));
    runSelect.onchange = () => goToCase(runSelect.value, "");
    nodeSelect.onchange = () => goToCase(runSelect.value, nodeSelect.value);
    $("create-bug-button").disabled = !selectedCase;
    $("failure-hint").textContent = selectedCase ? "登记后可比较同名文件的新版本。" :
      requestedNode ? "指定的 nodeid 不属于该运行的可登记失败项。请重新选择。" :
      requestedRun && !originalRun ? "指定运行不在本项目的失败记录中。" :
      "需要可重跑的失败用例。收集错误可在原始执行日志中查看。";
    $("create-bug").onsubmit = async event => {
      event.preventDefault();
      if (!selectedCase || waiting) return;
      waiting = true;
      $("create-bug-button").disabled = true;
      message($, "正在登记真实失败用例。");
      try {
        const saved = await api("/api/runs/" + originalRun.id + "/bugs", {nodeid: selectedCase.nodeid, title: $("bug-title").value});
        if (saved.run_id !== originalRun.id || saved.nodeid !== selectedCase.nodeid || saved.project_id !== Number(projectId)) {
          throw new Error("登记响应与所选失败证据不一致。");
        }
        const nominated = index.get(Number(params.get("file")));
        const keepCandidate = nominated && sameFilename(nominated.filename, original.filename) && nominated.revision > original.revision;
        location.assign(routeToIssue(saved, keepCandidate ? nominated.id : original.id));
      } catch (error) {
        waiting = false;
        $("create-bug-button").disabled = false;
        message($, error.message, true);
      }
    };
    message($, selectedCase ? "已定位原始运行 #" + originalRun.id + " 的失败用例。" : $("failure-hint").textContent);
    return;
  }

  function paintIssue() {
    $("issues-empty").hidden = true;
    $("bug-detail").hidden = false;
    $("history-panel").hidden = false;
    $("bug-key").textContent = "缺陷 #" + issue.id;
    $("bug-name").textContent = issue.title;
    setStatus($("bug-state"), issueState(issue.status));
  }
  function syncRoute() {
    const version = candidate?.id || original.id;
    syncModuleLinks({file: version});
    history.replaceState(null, "", link("bugs", {
      file: version, bug: issue.id, run: originalRun.id,
      nodeid: selectedCase.nodeid, regression: selectedRegression,
    }));
  }
  function runHref(row) {
    return link("runs", {file: row.file_id, suite: suite.id, run: row.run_id});
  }
  function paintRegressionList() {
    $("regression-count").textContent = regressions().length + " 条";
    $("regressions-empty").hidden = Boolean(regressions().length);
    const list = document.createDocumentFragment();
    for (const row of regressions()) {
      const line = element("div", "bug-regression-row");
      line.dataset.runId = row.run_id;
      line.toggleAttribute("data-selected", row.run_id === selectedRegression);
      const inspect = element("button", "", "#" + row.run_id + " · v" + row.revision);
      inspect.type = "button";
      inspect.setAttribute("aria-pressed", String(row.run_id === selectedRegression));
      inspect.onclick = () => { void focusRegression(row.run_id); };
      const status = element("span", "bug-pill");
      const recorded = byRun.get(row.run_id);
      const [outcome, tone] = recorded ? runState(recorded) : ["运行未读取", "idle"];
      setStatus(status, [outcome + " · " + issueLabel(row.status), row.status === "resolved" ? "ok" : tone === "error" ? "error" : "warning"]);
      const open = element("a", "bug-link", "运行记录");
      open.href = runHref(row);
      line.append(inspect, status, open);
      list.append(line);
    }
    $("regressions").replaceChildren(list);
  }
  async function focusRegression(id) {
    const sequence = ++regressionSequence;
    const row = regressions().find(entry => entry.run_id === id);
    selectedRegression = row?.run_id;
    updateIdentity();
    syncRoute();
    paintRegressionList();
    $("regression-facts").hidden = true;
    $("regression-run").hidden = $("regression-log-box").hidden = true;
    if (!row) {
      $("regression-evidence").textContent = "暂无选中的回归记录。";
      return;
    }
    $("regression-evidence").textContent = "正在读取回归运行 #" + row.run_id + "…";
    try {
      const run = await readRun(row.run_id);
      if (sequence !== regressionSequence) return;
      if (run.file_id !== row.file_id || run.suite_id !== suite.id || index.get(row.file_id)?.revision !== row.revision) {
        throw new Error("回归运行与缺陷历史关联不一致。");
      }
      const outcome = run.cases.find(item => item.nodeid === selectedCase.nodeid)?.outcome;
      $("regression-evidence").textContent = runState(run)[0] + " · 回归判定" + issueLabel(row.status);
      readout($("regression-facts"), [
        ["被测版本", "v" + row.revision + " · #" + row.file_id], ["该用例", outcome ? labelStatus(outcome) : "未记录"],
        ["耗时", duration(run.duration_ms)], ["失败（修复前 → 修复后）", (originalRun.failed ?? "—") + " → " + (run.failed ?? "—")],
        ["通过 / 失败 / 错误", [run.passed, run.failed, run.errors].map(value => value ?? "—").join(" / ")],
      ]);
      $("regression-facts").hidden = false;
      $("regression-run").href = runHref(row);
      $("regression-run").hidden = false;
      $("regression-log").textContent = run.log || "";
      $("regression-log-box").hidden = !run.log;
    } catch (error) {
      if (sequence === regressionSequence) $("regression-evidence").textContent = "无法读取回归运行：" + error.message;
    }
  }

  const fixes = files.filter(row => sameFilename(row.filename, original.filename) && row.revision > original.revision);
  const fix = $("fix-file");
  const dialog = $("confirm-regression");
  const fileCache = new Map();
  function readFile(row) {
    if (!fileCache.has(row.id)) {
      fileCache.set(row.id, api("/api/files/" + row.id).then(file => {
        if (file.id !== row.id || file.project_id !== Number(projectId) || file.filename !== row.filename ||
            file.revision !== row.revision || file.sha256 !== row.sha256 || typeof file.source !== "string") {
          throw new Error("版本详情与所选文件的记录不一致。");
        }
        return file;
      }).catch(error => { fileCache.delete(row.id); throw error; }));
    }
    return fileCache.get(row.id);
  }

  async function compare() {
    const sequence = ++compareSequence;
    const next = fixes.find(row => String(row.id) === fix.value);
    candidate = next;
    compared = undefined;
    updateIdentity();
    syncRoute();
    $("regress-button").disabled = true;
    $("diff-workspace").hidden = $("diff-summary").hidden = $("retry-diff").hidden = true;
    if (!next) {
      state($("diff-empty"), "empty", fixes.length ? "请选择候选版本" : "没有可用候选版本",
        fixes.length ? "当前选项必须是同名文件的更新修订。" : "请在项目中心导入同项目且同名文件的新修订。");
      return;
    }
    $("fix-hint").textContent = "原样使用套件 #" + suite.id + " 执行所选版本。状态以服务端回归结果为准。";
    state($("diff-empty"), "loading", "正在核对两个版本", "读取原始和候选源码。");
    try {
      const [left, right] = await Promise.all([readFile(original), readFile(next)]);
      if (sequence !== compareSequence) return;
      renderDiff($, left, right);
      $("diff-from").textContent = fileLabel(left);
      $("diff-to").textContent = fileLabel(right);
      $("diff-from-sha").textContent = "SHA-256 " + left.sha256;
      $("diff-to-sha").textContent = "SHA-256 " + right.sha256;
      $("diff-empty").hidden = true;
      $("diff-workspace").hidden = false;
      compared = next;
      $("regress-button").disabled = waiting;
    } catch (error) {
      if (sequence !== compareSequence) return;
      state($("diff-empty"), "error", "版本读取失败", error.message);
      $("retry-diff").hidden = false;
    }
  }

  $("regress").hidden = false;
  const requestedVersion = params.get("file");
  const initialVersion = !requestedVersion || requestedVersion === String(original.id) ? fixes[0] :
    fixes.find(row => String(row.id) === requestedVersion);
  options(fix, fixes, fileLabel, initialVersion?.id, "尚无合法候选版本");
  const updateAiRepair = bindAiRepair($, api, issue, original, readFile, async saved => {
    index.set(saved.id, saved);
    if (!fixes.some(row => row.id === saved.id)) fixes.unshift(saved);
    options(fix, fixes, fileLabel, saved.id, "尚无合法候选版本");
    await compare();
  });
  fix.onchange = () => { void compare(); };
  $("retry-diff").onclick = () => { void compare(); };
  $("regress").onsubmit = event => {
    event.preventDefault();
    if (!compared || waiting) return;
    dialog.returnValue = "cancel";
    $("confirm-regression-detail").textContent = "以原始套件 #" + suite.id + " 对 " + fileLabel(compared) +
      " 执行回归。原始失败运行 #" + originalRun.id + " 将继续保留。";
    dialog.showModal();
  };
  dialog.onclose = async () => {
    if (dialog.returnValue !== "run" || waiting || !compared || compared !== candidate) return;
    waiting = true;
    fix.disabled = $("regress-button").disabled = $("project").disabled = true;
    const submitted = compared;
    const known = new Set(regressions().map(row => row.run_id));
    message($, "回归执行中 · 等待原始套件 #" + suite.id + " 返回已保存的结果。");
    try {
      const saved = await api("/api/bugs/" + issue.id + "/regressions", {file_id: submitted.id});
      if (saved.id !== issue.id || saved.project_id !== Number(projectId) || saved.file_id !== original.id ||
          saved.run_id !== originalRun.id || saved.nodeid !== selectedCase.nodeid || saved.suite_id !== suite.id) {
        throw new Error("回归响应与原始缺陷的身份不一致。");
      }
      issue = saved;
      updateAiRepair(regressions());
      const latest = await api(base + "/runs");
      for (const row of latest) byRun.set(row.id, row);
      const added = regressions().filter(row => !known.has(row.run_id) && row.file_id === submitted.id);
      const updatedIssues = issues.map(row => row.id === issue.id ? issue : row);
      bindIssues($, updatedIssues, issue.id, routeToIssue);
      paintIssue();
      const id = added.length === 1 ? added[0].run_id : selectedRegression || regressions()[0]?.run_id;
      await focusRegression(id);
      message($, added.length === 1 ? "已保存回归运行 #" + id + " · 缺陷状态：" + issueLabel(issue.status) :
        "已读取服务端回归历史 · 缺陷状态：" + issueLabel(issue.status));
    } catch (error) {
      message($, error.status === 409 ? "执行器忙，请稍后重试回归。" : error.message, true);
    } finally {
      waiting = false;
      fix.disabled = !fixes.length;
      $("project").disabled = false;
      $("regress-button").disabled = !compared;
    }
  };

  paintIssue();
  const requestedRegression = regressions().find(row => String(row.run_id) === params.get("regression"));
  await Promise.all([compare(), focusRegression(requestedRegression?.run_id || regressions()[0]?.run_id)]);
  message($, "缺陷 #" + issue.id + " · 原始运行 #" + originalRun.id + " · 套件 #" + suite.id + "。");
}
