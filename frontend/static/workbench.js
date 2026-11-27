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
    throw new Error(typeof payload.detail === "string" ? payload.detail : "请求失败（HTTP " + response.status + "）");
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

async function showProjects() {
  form("create-project", async () => {
    const row = await api("/api/projects", {name: $("project-name").value});
    location.assign(link(page, {project: row.id, file: ""}));
  });
  $("import-button").disabled = !project.value;
  form("import-file", async () => {
    const selected = $("upload").files[0];
    if (selected.size > 131072) throw new Error("文件超过 128 KiB。");
    let source;
    try { source = new TextDecoder("utf-8", {fatal: true}).decode(await selected.arrayBuffer()); }
    catch { throw new Error("无法读取 UTF-8 源码。请检查文件编码。"); }
    const row = await api("/api/projects/" + project.value + "/files", {filename: selected.name, source});
    location.assign(link(page, {file: row.id}));
  });
  if (file.value) {
    const row = await api("/api/files/" + file.value);
    $("digest").textContent = row.filename + " · v" + row.revision + " · SHA-256 " + row.sha256;
    $("source").textContent = row.source;
    $("source-panel").hidden = false;
  }
}

async function start() {
  const projects = await api("/api/projects");
  populate(project, projects, row => row.name, params.get("project"), "请先创建项目");
  const files = project.value ? await api("/api/projects/" + project.value + "/files") : [];
  populate(file, files, row => row.filename + " · v" + row.revision, params.get("file"), "请先导入文件");
  project.onchange = () => location.assign(link(page, {file: ""}));
  file.onchange = () => location.assign(link(page));
  document.querySelectorAll("[data-dest]").forEach(a => { a.href = link(a.dataset.dest); });
  if (page === "projects") await showProjects();
  if (page === "analysis") {
    const {showAnalysis} = await import("./analysis.js");
    if (!file.value) return showEmpty("先导入一个 Python 文件，即可查看其函数、类和源码位置。");
    await showAnalysis({$, api, link, fileId: file.value});
  }
  if (page === "generation") {
    const {showGeneration} = await import("./generation.js");
    if (!file.value) return showEmpty("请先选择项目并导入需要生成测试的文件。");
    await showGeneration({$, api, link, form, populate, params, fileId: file.value});
  }
  if (page === "runs") {
    const {showRuns} = await import("./runs.js");
    if (!file.value) return showEmpty("请先导入源码并生成测试，再启动执行。");
    await showRuns({$, api, link, form, populate, params, files, projectId: project.value, fileId: file.value});
  }
}

start().catch(error => message(error.message, true));
