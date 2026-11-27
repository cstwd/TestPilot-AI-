"use strict";

const $ = id => document.getElementById(id);
const projectPicker = $("activity-project");
const activityButton = $("refresh-activity");
const recent = Object.fromEntries([...document.querySelectorAll("[data-kind]")].map(row =>
  [row.dataset.kind, {row, link: row.querySelector("a"), note: row.querySelector("[data-note]")}]));
const missing = {project: "暂无项目", file: "暂无文件版本", run: "暂无执行记录",
  bug: "暂无缺陷记录", report: "暂无质量报告"};
const runStates = {passed: "通过", failed: "用例失败", error: "执行错误", timeout: "超时", skipped: "全部跳过"};
const issueStates = {open: "待修复", resolved: "已解决"};
const expandOutput = $("expand-self-test");
const moduleLinks = [...document.querySelectorAll("[data-module]")];
const workspacePaths = new Set(moduleLinks.map(link => link.pathname));
const recentProjectKey = "testpilot.home.lastProject";
const referrer = document.referrer ? new URL(document.referrer) : null;
const displayTime = new Intl.DateTimeFormat("zh-CN", {hour: "2-digit", minute: "2-digit", second: "2-digit"});
const activityTime = new Intl.DateTimeFormat("zh-CN", {month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit"});
let activityRequest;
let createThenImport = false;
let knownProjects = [];
let incomingWorkspace = referrer?.origin === location.origin && workspacePaths.has(referrer.pathname) ? referrer : null;

function showStatus(id, text, state = "loading") {
  const indicator = $(id);
  indicator.textContent = text;
  indicator.dataset.state = state;
}

function setTime(id) {
  const time = $(id);
  const now = new Date();
  time.dateTime = now.toISOString();
  time.textContent = displayTime.format(now);
}

async function readJson(url, {method = "GET", timeout = 8000, signal, expected} = {}) {
  const timer = AbortSignal.timeout(timeout);
  const response = await fetch(url, {
    method, cache: "no-store", headers: {Accept: "application/json"},
    signal: signal ? AbortSignal.any([signal, timer]) : timer,
  });
  const data = await response.json();
  if (expected ? expected[data?.status] !== response.status : !response.ok) {
    throw new Error("请求未返回可用数据");
  }
  return data;
}

async function checkConnections() {
  const button = $("refresh-button");
  if (button.disabled) return;
  button.disabled = true;
  showStatus("api-status", "检查中");
  showStatus("database-status", "检查中");
  showStatus("service-indicator", "检查中");
  const detail = $("connection-detail");
  detail.hidden = true;
  try {
    const health = await readJson("/api/health", {expected: {ok: 200, degraded: 503}});
    const ready = health.status === "ok" && health.database === "ok";
    if (!ready && (health.status !== "degraded" || health.database !== "error")) throw new Error("服务状态异常");
    showStatus("api-status", "已连接", "ok");
    showStatus("database-status", ready ? "已连接" : "异常", ready ? "ok" : "error");
    showStatus("service-indicator", ready ? "服务在线" : "数据库异常", ready ? "ok" : "error");
    if (!ready) {
      detail.textContent = "服务有响应。请检查 SQLite 数据目录和运行日志。";
      detail.hidden = false;
    }
  } catch {
    showStatus("api-status", "检查失败", "error");
    showStatus("database-status", "无法确认", "error");
    showStatus("service-indicator", "服务状态未确认", "error");
    detail.textContent = "请检查本地服务连接和运行日志，然后重新检查。";
    detail.hidden = false;
  } finally {
    setTime("health-checked");
    button.disabled = false;
  }
}

async function runSelfTest() {
  const button = $("self-test-button");
  if (button.disabled) return;
  button.disabled = true;
  showStatus("self-test-status", "运行中");
  const output = $("self-test-output");
  const detail = $("self-test-detail");
  output.hidden = true;
  output.open = false;
  detail.textContent = "";
  try {
    const result = await readJson("/api/self-test", {
      method: "POST", timeout: 60000, expected: {passed: 200, failed: 503, busy: 409, rejected: 403},
    });
    const statuses = {passed: ["通过", "ok"], failed: ["未通过", "error"],
      busy: ["执行器忙碌", "loading"], rejected: ["请求被拒绝", "error"]};
    showStatus("self-test-status", ...statuses[result.status]);
    if (result.status === "passed" || result.status === "failed") setTime("self-test-checked");
    detail.textContent = result.detail || "服务未返回输出。";
  } catch {
    showStatus("self-test-status", "无法获取结果", "error");
    detail.textContent = "请检查服务连接和本地运行日志。";
  } finally {
    output.hidden = false;
    output.open = expandOutput.checked;
    button.disabled = false;
  }
}

function route(page, params, fragment = "") {
  return "/workbench/" + page + "?" + new URLSearchParams(params) + fragment;
}

function rememberProject(project) {
  try { localStorage.setItem(recentProjectKey, project); }
  catch { /* The newest known project remains available without browser storage. */ }
}

function selectResumeProject(newest) {
  let previous;
  try { previous = localStorage.getItem(recentProjectKey); }
  catch { /* Storage is optional. */ }
  const incomingProject = incomingWorkspace ? incomingWorkspace.searchParams.get("project") ?? String(newest.id) : null;
  if (knownProjects.some(row => String(row.id) === incomingProject)) {
    previous = incomingProject;
    rememberProject(previous);
  }
  incomingWorkspace = null;
  const resumed = knownProjects.find(row => String(row.id) === previous);
  const target = resumed || newest;
  const link = $("quick-resume");
  link.href = route("projects", {project: target.id});
  link.title = (resumed ? "上次打开：" : "最近创建：") + target.name;
}

function paint(kind, record, state = "empty", message = missing[kind]) {
  const {row, link, note} = recent[kind];
  row.dataset.state = record ? "ok" : state;
  link.hidden = !record;
  if (record) {
    link.href = record.href;
    link.textContent = record.label;
  } else {
    link.removeAttribute("href");
    link.textContent = "";
  }
  note.textContent = record ? record.note : message;
}

function beginActivity() {
  activityRequest?.abort();
  activityRequest = new AbortController();
  $("activity").setAttribute("aria-busy", "true");
  activityButton.disabled = true;
  return activityRequest.signal;
}

function finishActivity(signal) {
  if (signal.aborted) return;
  $("activity").setAttribute("aria-busy", "false");
  activityButton.disabled = false;
}

function message(text, state) {
  const label = $("activity-message");
  label.hidden = !text;
  label.textContent = text;
  label.dataset.state = state;
}

async function latest(url, signal) {
  const rows = await readJson(url, {signal});
  if (!Array.isArray(rows)) throw new Error("列表格式异常");
  return rows[0];
}

function describeRun(project, run, page) {
  return {label: "运行 #" + run.id,
    note: (runStates[run.status] ?? run.status) + (run.created_at ? " · " + activityTime.format(new Date(run.created_at)) : ""),
    href: route(page, {project, file: run.file_id, suite: run.suite_id, run: run.id})};
}

function showLatest(kind, task, describe, signal) {
  return task.then(row => {
    if (!signal.aborted) paint(kind, row ? describe(row) : null);
    return row;
  }).catch(error => {
    if (!signal.aborted) paint(kind, null, "error", "读取失败，可刷新重试");
    throw error;
  });
}

async function loadActivity(project, signal = beginActivity()) {
  for (const kind of ["file", "run", "bug", "report"]) paint(kind, null, "loading", "正在读取…");
  $("quick-import").href = route("projects", {project}, "#upload");
  for (const link of moduleLinks) link.href = route(link.dataset.module, {project});
  message("", "");
  const endpoint = "/api/projects/" + project;
  const files = showLatest("file", latest(endpoint + "/files", signal), row => ({
    label: row.filename, note: "版本 v" + row.revision, href: route("projects", {project, file: row.id}),
  }), signal);
  const runs = showLatest("run", latest(endpoint + "/runs", signal),
    row => describeRun(project, row, "runs"), signal);
  const bugs = showLatest("bug", latest(endpoint + "/bugs", signal), row => ({
    label: row.title, note: (issueStates[row.status] ?? row.status) + " · #" + row.id,
    href: route("bugs", {project, file: row.file_id, bug: row.id, run: row.run_id}),
  }), signal);
  const report = showLatest("report", runs.then(async run => {
    if (!run) return null;
    const data = await readJson("/api/runs/" + run.id + "/report", {signal});
    if (data.run?.id !== run.id || String(data.project?.id) !== project || data.source?.id !== run.file_id) {
      throw new Error("报告与运行身份不匹配");
    }
    return data;
  }), data => ({
    label: data.source.filename + " v" + data.source.revision,
    note: "关联运行 #" + data.run.id,
    href: route("reports", {project, file: data.source.id, run: data.run.id}),
  }), signal);
  await Promise.allSettled([files, runs, bugs, report]);
  finishActivity(signal);
}

async function loadProjects() {
  const signal = beginActivity();
  const previousProject = projectPicker.value;
  knownProjects = [];
  projectPicker.disabled = true;
  projectPicker.replaceChildren(new Option("正在读取…", ""));
  $("quick-import").href = "/workbench/projects#project-name";
  $("quick-import").onclick = null;
  $("quick-resume").href = "/workbench/projects";
  $("quick-resume").removeAttribute("title");
  for (const link of moduleLinks) link.href = "/workbench/" + link.dataset.module;
  message("正在读取项目记录…", "loading");
  for (const kind of Object.keys(recent)) paint(kind, null, "loading", "正在读取…");
  try {
    const projects = await readJson("/api/projects", {signal});
    if (!Array.isArray(projects)) throw new Error("项目列表格式异常");
    if (signal.aborted) return;
    knownProjects = projects;
    const latestProject = projects[0];
    if (!latestProject) {
      projectPicker.replaceChildren(new Option("暂无项目", ""));
      $("quick-import").onclick = event => {
        event.preventDefault();
        openCreate(true);
      };
      message("创建项目并导入代码后，活动将显示在这里。", "empty");
      Object.keys(recent).forEach(kind => paint(kind, null));
      return;
    }
    const href = route("projects", {project: latestProject.id});
    selectResumeProject(latestProject);
    paint("project", {label: latestProject.name, note: "项目 #" + latestProject.id, href});
    projectPicker.replaceChildren(...projects.map(project => new Option(project.name, project.id)));
    projectPicker.value = projects.some(project => String(project.id) === previousProject) ?
      previousProject : String(latestProject.id);
    projectPicker.disabled = false;
    await loadActivity(projectPicker.value, signal);
  } catch {
    if (signal.aborted) return;
    projectPicker.replaceChildren(new Option("项目暂不可用", ""));
    message("无法读取项目记录。请检查服务连接或刷新最近活动。", "error");
    Object.keys(recent).forEach(kind => paint(kind, null, "error", "项目记录不可用"));
  } finally {
    finishActivity(signal);
  }
}

function openCreate(importAfter) {
  createThenImport = importAfter;
  $("home-create-error").hidden = true;
  $("home-create").showModal();
}

$("home-create-form").onsubmit = async event => {
  event.preventDefault();
  const button = $("home-create-submit");
  if (button.disabled) return;
  const error = $("home-create-error");
  const fragment = createThenImport ? "#upload" : "";
  error.hidden = true;
  button.disabled = true;
  try {
    const response = await fetch("/api/projects", {
      method: "POST", headers: {"Content-Type": "application/json"}, signal: AbortSignal.timeout(8000),
      body: JSON.stringify({name: $("home-project-name").value}),
    });
    const data = await response.json();
    if (response.status !== 201) {
      throw new Error(typeof data.detail === "string" ? data.detail : "请检查项目名称后重试。");
    }
    if (!Number.isInteger(data.id)) throw new Error("服务未返回新项目编号。");
    rememberProject(String(data.id));
    location.assign(route("projects", {project: data.id}, fragment));
  } catch (failure) {
    error.textContent = failure.message;
    error.hidden = false;
  } finally {
    button.disabled = false;
  }
};

for (const button of document.querySelectorAll("[data-dialog]")) {
  button.onclick = () => button.dataset.dialog === "home-create" ? openCreate(false) : $(button.dataset.dialog).showModal();
}
try { expandOutput.checked = localStorage.getItem("testpilot.home.expandSelfTest") !== "false"; }
catch { /* The session control works without browser storage. */ }
expandOutput.onchange = () => {
  if (!$("self-test-output").hidden) $("self-test-output").open = expandOutput.checked;
  try { localStorage.setItem("testpilot.home.expandSelfTest", String(expandOutput.checked)); }
  catch { /* A storage failure leaves this session's preference intact. */ }
};
$("refresh-button").onclick = checkConnections;
$("self-test-button").onclick = runSelfTest;
projectPicker.onchange = () => loadActivity(projectPicker.value);
activityButton.onclick = loadProjects;
document.addEventListener("click", event => {
  const link = event.target.closest("a");
  if (event.defaultPrevented || !link || link.origin !== location.origin || !workspacePaths.has(link.pathname)) return;
  const project = new URLSearchParams(link.search).get("project");
  if (knownProjects.some(row => String(row.id) === project)) rememberProject(project);
});
window.addEventListener("pageshow", event => {
  if (event.persisted) {
    checkConnections();
    loadProjects();
  }
});
window.addEventListener("pagehide", () => activityRequest?.abort());
checkConnections();
loadProjects();
