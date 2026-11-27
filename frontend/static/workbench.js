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

function syncModuleLinks(extra) {
  document.querySelectorAll("[data-dest]").forEach(anchor => { anchor.href = link(anchor.dataset.dest, extra); });
}

function bindModuleMenu() {
  const menu = $("mobile-navigation");
  if (!menu) return;
  const lifetime = new AbortController();
  const options = {signal: lifetime.signal};
  menu.addEventListener("keydown", event => {
    if (event.key === "Escape" && menu.open) {
      menu.open = false;
      menu.querySelector("summary").focus();
    }
  }, options);
  menu.addEventListener("click", event => {
    if (event.target.closest("[data-dest]")) menu.open = false;
  }, options);
  document.addEventListener("pointerdown", event => {
    if (menu.open && !menu.contains(event.target)) menu.open = false;
  }, options);
  window.addEventListener("pagehide", event => {
    menu.open = false;
    if (!event.persisted) lifetime.abort();
  }, options);
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

async function start() {
  bindModuleMenu();
  const projectWorkspace = page === "projects" ? await import("./projects.js") : null;
  if (projectWorkspace) projectWorkspace.bindProjectPanels();
  const changeProject = () => location.assign(link(page, {file: ""}));
  const projects = await api("/api/projects");
  const requireExplicitMatch = ["analysis", "projects", "generation", "runs", "bugs", "reports"].includes(page);
  populate(project, projects, row => row.name, params.get("project"), "请先创建项目");
  if (requireExplicitMatch && params.get("project") && project.value !== params.get("project")) project.selectedIndex = -1;
  project.onchange = changeProject;
  syncModuleLinks({file: ""});
  if (projectWorkspace) {
    projectWorkspace.showProjectList($, projects, project.value, link);
  }
  const files = project.value ? await api("/api/projects/" + project.value + "/files") : [];
  populate(file, files, row => row.filename + " · v" + row.revision, params.get("file"), "请先导入文件");
  if (requireExplicitMatch && params.get("file") && file.value !== params.get("file")) file.selectedIndex = -1;
  file.onchange = () => location.assign(link(page));
  syncModuleLinks();
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
    await showBugs({$, api, link, syncModuleLinks, params, files, projectId: project.value});
  }
  if (page === "reports") {
    const {showReports} = await import("./reports.js");
    await showReports({$, api, link, params, projectId: project.value, files});
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
  if (page === "reports") {
    const {showReportsError} = await import("./reports.js");
    showReportsError($, error);
  }
});
