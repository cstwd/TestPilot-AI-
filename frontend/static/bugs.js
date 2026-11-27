import {labelStatus, sameFilename} from "./runs.js";

const bugStatus = value => ({open: "待修复", verified: "已验证", resolved: "已解决", closed: "已关闭"}[value] || value);

export async function showBugs({$, api, link, form, populate, params, files, projectId}) {
  const [runs, bugs] = await Promise.all([api("/api/projects/" + projectId + "/runs"), api("/api/projects/" + projectId + "/bugs")]);
  const failures = runs.filter(run => ["failed", "error"].includes(run.status));
  const runSelect = $("bug-run");
  populate(runSelect, failures, run => "#" + run.id + " · " + labelStatus(run.status),
    params.get("run"), "没有失败运行");
  runSelect.onchange = () => location.assign(link("bugs", {run: runSelect.value, bug: params.get("bug")}));
  const run = runSelect.value ? await api("/api/runs/" + runSelect.value) : null;
  const nodes = (run?.cases || []).filter(item => item.nodeid.includes("::") && ["failed", "error"].includes(item.outcome));
  populate($("nodeid"), nodes.map(item => ({id: item.nodeid})), item => item.id, "", "无失败用例");
  $("create-bug-button").disabled = !nodes.length;
  if (!nodes.length) $("failure-hint").textContent = "请选择包含失败用例的运行。收集阶段的错误可在执行日志中查看。";
  form("create-bug", async () => {
    const saved = await api("/api/runs/" + run.id + "/bugs", {title: $("bug-title").value, nodeid: $("nodeid").value});
    location.assign(link("bugs", {bug: saved.id, run: run.id}));
  });
  const chooser = $("bug");
  populate(chooser, bugs, item => "#" + item.id + " · " + item.title, params.get("bug"), "尚未登记缺陷");
  chooser.onchange = () => location.assign(link("bugs", {bug: chooser.value}));
  if (!chooser.value) return;
  const bug = await api("/api/bugs/" + chooser.value);
  const original = files.find(row => row.id === bug.file_id);
  const fixes = files.filter(row => original && sameFilename(row.filename, original.filename) &&
    row.revision > original.revision);
  $("bug-state").textContent = bug.title + " · " + bugStatus(bug.status);
  $("failure-node").textContent = "用例 " + bug.nodeid + " · 固定套件 #" + bug.suite_id;
  $("original-run").href = link("runs", {file: bug.file_id, run: bug.run_id, suite: bug.suite_id});
  populate($("fix-file"), fixes, item => item.filename + " · v" + item.revision, params.get("file"), "尚无修复版本");
  $("regress-button").disabled = !fixes.length;
  $("fix-hint").textContent = fixes.length ? "将使用原始套件对所选修复版本执行回归。" : "请到“项目与文件”重新导入同名文件的修复版本。";
  form("regress", async () => {
    $("notice").textContent = "正在运行原始套件以复核缺陷。";
    const saved = await api("/api/bugs/" + bug.id + "/regressions", {file_id: Number($("fix-file").value)});
    location.assign(link("bugs", {bug: saved.id, run: bug.run_id, file: $("fix-file").value}));
  });
  for (const evidence of bug.regressions) {
    const li = document.createElement("li");
    const anchor = document.createElement("a");
    anchor.href = link("runs", {file: evidence.file_id, suite: bug.suite_id, run: evidence.run_id});
    anchor.textContent = "运行 #" + evidence.run_id + " · v" + evidence.revision + " · " + bugStatus(evidence.status);
    li.append(anchor);
    $("regressions").append(li);
  }
  $("bug-detail").hidden = false;
}
