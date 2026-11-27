const labels = {
  passed: "通过", failed: "失败", error: "错误", timeout: "超时",
  skipped: "跳过", unavailable: "执行器不可用", running: "运行中",
};
export const labelStatus = value => labels[value] || value || "未记录";

export function readout(node, values) {
  node.replaceChildren();
  for (const [term, value] of values) {
    const cell = document.createElement("div");
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = term;
    dd.textContent = value ?? "未记录";
    cell.append(dt, dd);
    node.append(cell);
  }
}

export async function showRuns({$, api, link, form, populate, params, files, projectId, fileId}) {
  const current = files.find(item => String(item.id) === fileId);
  const revisions = files.filter(item => item.filename.toLowerCase() === current.filename.toLowerCase());
  // Read older suites on demand so large histories don't fan out into many requests.
  const sourceSelect = document.createElement("select");
  const sourceLabel = document.createElement("label");
  sourceLabel.textContent = "套件来源版本";
  sourceLabel.append(sourceSelect);
  $("start-run").prepend(sourceLabel);
  const runs = await api("/api/projects/" + projectId + "/runs");
  const chosenRun = runs.find(item => String(item.id) === params.get("run"));
  const requestedSuite = params.get("suite") || (chosenRun ? String(chosenRun.suite_id) : "");
  let suiteFile = fileId;
  if (requestedSuite) {
    const suite = await api("/api/suites/" + encodeURIComponent(requestedSuite));
    if (revisions.some(item => item.id === suite.file_id)) suiteFile = String(suite.file_id);
  }
  populate(sourceSelect, revisions, item => item.filename + " · v" + item.revision,
    params.get("suite_file") || suiteFile, "没有可选版本");
  sourceSelect.onchange = () => location.assign(link("runs", {suite_file: sourceSelect.value}));
  const suites = await api("/api/files/" + sourceSelect.value + "/suites");
  populate($("run-suite"), suites, item => "#" + item.id + " · " + item.target, requestedSuite, "此版本尚无套件");
  $("execute").disabled = !suites.length;
  form("start-run", async () => {
    $("notice").textContent = "正在受限环境中运行 Pytest，请等待结果。";
    const result = await api("/api/suites/" + $("run-suite").value + "/runs", {file_id: Number(fileId)});
    location.assign(link("runs", {suite: result.suite_id, run: result.id}));
  });
  const history = $("run-history");
  populate(history, runs, item => "#" + item.id + " · 套件 " + item.suite_id + " · " + labelStatus(item.status),
    params.get("run"), "项目尚无运行记录");
  history.onchange = () => {
    const item = runs.find(run => String(run.id) === history.value);
    location.assign(link("runs", {file: item.file_id, suite: item.suite_id, run: item.id}));
  };
  if (!history.value) return;
  const result = await api("/api/runs/" + history.value);
  const version = files.find(item => item.id === result.file_id);
  $("run-identity").textContent = "运行 #" + result.id + " · 套件 #" + result.suite_id + " · " +
    (version ? version.filename + " v" + version.revision : "文件 #" + result.file_id);
  readout($("run-summary"), [["结果", labelStatus(result.status)], ["耗时 (ms)", result.duration_ms],
    ["通过", result.passed], ["失败", result.failed], ["错误", result.errors], ["跳过", result.skipped]]);
  $("coverage").textContent = result.coverage_pct == null ? "行覆盖率未采集" :
    "行覆盖率 " + result.coverage_pct + "%（" + result.covered_lines + "/" + result.total_lines + " 行）";
  $("run-log").textContent = result.log || "无日志输出。";
  for (const entry of result.cases || []) {
    const li = document.createElement("li");
    li.textContent = entry.nodeid + " · " + labelStatus(entry.outcome);
    $("run-cases").append(li);
  }
  $("to-bugs").href = link("bugs", {run: result.id, file: result.file_id});
  $("to-report").href = link("reports", {run: result.id, file: result.file_id});
  $("run-result").hidden = false;
}
