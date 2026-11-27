const byId = id => document.getElementById(id);
const task = document.body.dataset.task;
const historyList = byId("history");
let selected = "", poll = null, inFlight = false;
const names = {killed:"已杀死", survived:"存活", timeout:"超时", execution_error:"执行错误", unrun:"未运行",
  cancelled:"已终止", completed:"已完成", running:"执行中", ready:"已创建", error:"会话出错",
  generated:"已生成候选", rejected:"未采纳", unavailable:"模型不可用", baseline_failed:"原始测试基线失败",
  feedback_unavailable:"模型不可用", feedback_rejected:"补测未采纳", feedback_baseline_failed:"补测基线失败"};

async function api(url, method = "GET", body) {
  const r = await fetch(url, {method, headers: {"Content-Type":"application/json"}, body: body && JSON.stringify(body)});
  const data = await r.json();
  if (!r.ok) throw Error(data.detail || r.statusText);
  return data;
}
function summary(stats) {
  if (!stats) return "尚无有效基线";
  const score = stats.score_pct == null ? "无适用变异" : stats.score_pct + "%";
  return score + "（" + stats.killed + "/" + stats.total + "） · 存活 " + stats.survived + " · 超时 " + stats.timeout +
    " · 执行错误 " + stats.execution_error + " · 已终止 " + stats.cancelled + " · 未运行 " + stats.unrun +
    " · 等价候选 " + stats.equivalent_candidates;
}
function note(title, lines) {
  const item = document.createElement("article");
  const heading = document.createElement("h3");
  heading.textContent = title;
  item.append(heading);
  for (const line of lines.filter(Boolean)) {
    const p = document.createElement("p");
    p.textContent = line;
    item.append(p);
  }
  return item;
}
function renderEvidence(row, statuses) {
  const baselines = row.events.filter(e => e.kind === "baseline" || e.kind === "validation");
  byId("baseline-panel").hidden = !baselines.length;
  byId("baseline-evidence").replaceChildren(...baselines.map(event => {
    const run = event.summary;
    const label = event.phase === "before" ? "原始测试" : event.kind === "validation" ? "全套候选校验" : "采纳后的补测基线";
    const counts = [["通过",run.passed],["失败",run.failed],["错误",run.errors],["跳过",run.skipped]]
      .filter(([,n]) => Number.isInteger(n)).map(([k,n]) => k + " " + n);
    if (Number.isInteger(run.exit_code)) counts.push("退出码 " + run.exit_code);
    return note(label, [event.reason, counts.join(" · "), run.diagnostic,
      ...run.failures.map(f => [f.nodeid, f.exception_type, f.message].filter(Boolean).join(" · "))]);
  }));
  const event = row.events.find(e => e.kind === "feedback");
  const feedback = event?.summary;
  const selection = row.events.find(e => e.kind === "selection");
  const added = feedback?.added_code || "";
  byId("feedback-panel").hidden = false;
  byId("feedback-code").textContent = added;
  byId("feedback-source").hidden = !added;
  const model = feedback?.model ? [feedback.provider, feedback.model].filter(Boolean).join(" / ") :
    feedback?.requested_model ? "已请求模型 " + feedback.requested_model : "";
  const status = event ? [names[event.status] || event.status, model, event.reason] :
    [!row.feedback_enabled ? "本次未启用模型补测" : row.diagnostic || "等待存活变异的实测结果"];
  if (selection) status.push(selection.reason);
  byId("feedback-status").textContent = status.filter(Boolean).join(" · ");
  const sites = new Map(row.manifest.map(m => [m.id, "L" + m.line + ":" + m.column]));
  byId("feedback-cases").replaceChildren(...(feedback?.cases || []).map(c => {
    let decision = "等待原版验证";
    if (selection?.summary.rejected_names.includes(c.test_name)) decision = "未采纳";
    else if (selection?.summary.accepted_names.includes(c.test_name) || row.after) decision = "已通过原版验证";
    else if (row.status === "feedback_baseline_failed") decision = "未通过整套补测验证";
    const outcome = statuses.get("after" + c.mutant_id);
    return note([sites.get(c.mutant_id), c.test_name].filter(Boolean).join(" · "), [
      c.call + " → " + c.expected, "选例理由　" + c.reason, decision,
      outcome && "该位置整套补测结果　" + (names[outcome.status] || outcome.status)]);
  }));
  const attempts = (feedback?.attempts || []).map(a => note(
    [sites.get(a.focus_id), "尝试 " + a.number, names[a.status] || a.status].filter(Boolean).join(" · "), [a.reason]));
  if (feedback?.pending_ids.length) {
    attempts.push(note("未尝试的位置", [feedback.pending_ids.map(id => sites.get(id) || id).join("、")]));
  }
  byId("feedback-attempts").replaceChildren(...attempts);
}
function render(row) {
  if (row.id !== selected) return;
  const active = ["ready","running"].includes(row.status);
  byId("status").textContent = (names[row.status] || row.status) + " " + row.diagnostic;
  byId("before").textContent = "原始测试　" + summary(row.before);
  byId("after").textContent = "追加补测　" + summary(row.after);
  byId("cancel").hidden = !active;
  byId("resume").hidden = !active || inFlight;
  byId("export").hidden = false;
  byId("export").href = "/api/mutations/" + row.id + "/report";
  const statuses = new Map(row.events.filter(e=>e.kind==="observation").map(e=>[e.phase+e.mutant_id,e]));
  renderEvidence(row, statuses);
  byId("sites").replaceChildren(...row.manifest.map(m=>{
    const item = document.createElement("article");
    const first = statuses.get("before"+m.id), second = statuses.get("after"+m.id);
    item.textContent = "L" + m.line + ":" + m.column + "  " + m.before + " → " + m.after +
      " · " + (first ? names[first.status] : "未运行") + (second ? " → "+names[second.status] : "") +
      (m.equivalent_candidate ? " · 等价候选" : "");
    return item;
  }));
  if (!active) clearInterval(poll);
}
function notify(e) { byId("status").textContent = e.message; }
async function refresh() {
  if (selected) render(await api("/api/mutations/"+selected));
}
function select(key) {
  clearInterval(poll);
  selected = key;
  historyList.value = key;
  if (!key) {
    for (const id of ["status","before","after","sites"]) byId(id).replaceChildren();
    for (const id of ["cancel","resume","export","feedback-panel","baseline-panel"]) byId(id).hidden = true;
    byId("export").removeAttribute("href");
    return;
  }
  refresh().catch(notify);
  if (key) poll = setInterval(()=>refresh().catch(notify), 1500);
}
async function run() {
  const key = selected;
  inFlight = true;
  byId("resume").hidden = true;
  try {render(await api("/api/mutations/"+key+"/run", "POST"));}
  finally {inFlight = false; await refresh();}
}
historyList.addEventListener("change", ()=>select(historyList.value));
byId("resume").addEventListener("click", ()=>run().catch(notify));
byId("cancel").addEventListener("click", async ()=> {
  try {render(await api("/api/mutations/"+selected+"/cancel", "POST"));} catch(e) {notify(e);}
});
byId("experiment").addEventListener("submit", async e=>{
  e.preventDefault();
  const button = e.target.querySelector("button");
  button.disabled = true;
  try {
    const r = await api("/api/engine/tasks/"+task+"/mutations", "POST", {feedback:e.target.elements.feedback.checked});
    historyList.add(new Option(r.created_at, r.id), 1);
    select(r.id); await run();
  } catch(error) {notify(error);} finally {button.disabled = false;}
});
if (historyList.options.length > 1) select(historyList.options[1].value);
