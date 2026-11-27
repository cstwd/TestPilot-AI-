import {labelStatus, readout} from "./runs.js";

export async function showReports({$, api, link, populate, params, projectId, showEmpty}) {
  const runs = await api("/api/projects/" + projectId + "/runs");
  if (!runs.length) return showEmpty("项目尚无运行记录。请先执行一次测试，再查看质量报告。", "runs", "前往测试执行");
  const history = $("report-history");
  populate(history, runs, item => "#" + item.id + " · 套件 " + item.suite_id + " · " + labelStatus(item.status),
    params.get("run"), "");
  history.onchange = () => {
    const chosen = runs.find(item => String(item.id) === history.value);
    location.assign(link("reports", {run: chosen.id, file: chosen.file_id}));
  };
  const endpoint = "/api/runs/" + history.value + "/report";
  const data = await api(endpoint);
  const {run, suite, source, quality} = data;
  $("report-origin").textContent = "运行 #" + run.id + " · " + source.filename + " v" + source.revision +
    " · " + suite.target + " · " + run.created_at;
  readout($("report-quality"), [["结果", labelStatus(run.status)], ["收录用例", quality.total],
    ["通过", quality.passed], ["失败", quality.failed], ["错误", quality.errors], ["跳过", quality.skipped],
    ["通过率", quality.pass_rate_pct == null ? "未采集" : quality.pass_rate_pct + "%"]]);
  $("assessment").textContent = quality.assessment;
  $("metric-notes").textContent = data.metric_notes;
  $("report-coverage").textContent = quality.coverage_pct == null ? "本次运行未采集行覆盖率。" :
    "被测文件行覆盖率 " + quality.coverage_pct + "%（" + quality.covered_lines + "/" + quality.total_lines + " 行）";
  $("report-hashes").textContent = "源码 SHA-256  " + source.sha256 + "\n套件 SHA-256  " + suite.sha256 +
    "\n套件 #" + suite.id + " · " + suite.mode + " · 源版本 ID " + suite.file_id;
  $("export-report").href = endpoint + "/export";
  $("report-run").href = link("runs", {file: source.id, suite: suite.id, run: run.id});
  if (!data.bugs.length) $("report-bugs").textContent = "没有与此运行关联的缺陷。";
  for (const bug of data.bugs) {
    const row = document.createElement("article");
    const a = document.createElement("a");
    a.href = link("bugs", {bug: bug.id, run: bug.run_id});
    a.textContent = "#" + bug.id + " · " + bug.title;
    const status = document.createElement("p");
    status.className = "hint";
    status.textContent = (bug.status === "resolved" ? "已解决" : bug.status === "open" ? "待修复" : bug.status) +
      " · " + bug.regressions.length + " 条回归记录";
    row.append(a, status);
    $("report-bugs").append(row);
  }
  $("report").hidden = false;
}
