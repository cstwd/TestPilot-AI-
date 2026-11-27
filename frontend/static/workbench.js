const $ = id => document.getElementById(id);
const page = document.body.dataset.page;
const params = new URLSearchParams(location.search);
const project = $("project");
const file = $("file");
const notice = $("notice");

function message(value = "", error = false) {
  notice.textContent = value;
  notice.toggleAttribute("data-error", error);
}

async function api(url, body) {
  const options = body === undefined ? {} : {
    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body),
  };
  const response = await fetch(url, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const error = new Error(typeof payload.detail === "string" ? payload.detail : "请求失败（HTTP " + response.status + "）");
    error.status = response.status;
    throw error;
  }
  return response.json();
}

function link(dest, extra = {}) {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries({project: project.value, file: file.value, ...extra})) {
    if (value) query.set(key, value);
  }
  return "/workbench/" + dest + (query.size ? "?" + query : "");
}

function populate(select, rows, label, preferred, empty) {
  select.replaceChildren(...rows.map(row => new Option(label(row), row.id)));
  if (!rows.length) select.add(new Option(empty, ""));
  if (rows.some(row => String(row.id) === preferred)) select.value = preferred;
  select.disabled = !rows.length;
}

function form(id, action) {
  $(id).addEventListener("submit", async event => {
    event.preventDefault();
    const button = event.submitter || event.target.querySelector("button");
    if (button.disabled) return;
    button.disabled = true;
    message("处理中…");
    try { await action(); }
    catch (error) { message(error.message, true); }
    finally { button.disabled = false; }
  });
}

function showEmpty(text, dest = "projects", label = "前往项目与文件") {
  const section = document.createElement("section");
  const prompt = document.createElement("p");
  prompt.textContent = text;
  const anchor = document.createElement("a");
  anchor.href = link(dest);
  anchor.textContent = label;
  section.append(prompt, anchor);
  $("content").replaceChildren(section);
}

async function start() {
  const projectWorkspace = page === "projects" ? await import("./projects.js") : null;
  if (projectWorkspace) projectWorkspace.bindProjectPanels($);
  const changeProject = () => location.assign(link(page, {file: ""}));
  const projects = await api("/api/projects");
  const requireExplicitMatch = ["analysis", "projects", "generation", "runs", "bugs"].includes(page);
  populate(project, projects, row => row.name, params.get("project"), "请先创建项目");
  if (requireExplicitMatch && params.get("project") && project.value !== params.get("project")) project.selectedIndex = -1;
  if (projectWorkspace) {
    project.onchange = changeProject;
    projectWorkspace.showProjectList($, projects, project.value, link);
  }
  const files = project.value ? await api("/api/projects/" + project.value + "/files") : [];
  populate(file, files, row => row.filename + " · v" + row.revision, params.get("file"), "请先导入文件");
  if (requireExplicitMatch && params.get("file") && file.value !== params.get("file")) file.selectedIndex = -1;
  if (!projectWorkspace) project.onchange = changeProject;
  file.onchange = () => location.assign(link(page));
  document.querySelectorAll("[data-dest]").forEach(a => { a.href = link(a.dataset.dest); });
  if (projectWorkspace) {
    await projectWorkspace.showProjects({$, api, link, projects, files, projectId: project.value, fileId: file.value, params, form, message});
  }
  if (page === "analysis") {
    const {showAnalysis} = await import("./analysis.js");
    await showAnalysis({$, api, link, files, params, fileId: file.value, projectId: project.value});
  }
  if (page === "generation") {
    const {showGeneration} = await import("./generation.js");
    await showGeneration({$, api, link, params, projectId: project.value, file: files.find(row => String(row.id) === file.value)});
  }
  if (page === "runs") {
    const {showRuns} = await import("./runs.js");
    await showRuns({$, api, link, params, files, projectId: project.value, fileId: file.value});
  }
  if (page === "bugs") {
    const {showBugs} = await import("./bugs.js");
    await showBugs({$, api, link, params, files, projectId: project.value});
  }
  if (page === "reports") {
    const {showReports} = await import("./reports.js");
    if (!project.value) return showEmpty("先创建项目并执行测试，质量报告将使用该次运行的结果。");
    await showReports({$, api, link, populate, params, projectId: project.value, showEmpty});
  }
}

start().catch(async error => {
  message(error.message, true);
  if (page === "projects") {
    const {showProjectsError} = await import("./projects.js");
    showProjectsError($, error);
  }
  if (page === "analysis") {
    const {showAnalysisError} = await import("./analysis.js");
    showAnalysisError($, error);
  }
  if (page === "generation") {
    const {showGenerationError} = await import("./generation.js");
    showGenerationError($, error, link);
  }
  if (page === "runs") {
    const {showRunsError} = await import("./runs.js");
    showRunsError($, error);
  }
  if (page === "bugs") {
    const {showBugsError} = await import("./bugs.js");
    showBugsError($, error);
  }
});
