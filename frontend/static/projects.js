import {splitSource, tokenize, colorLine} from "./studio-source.js";

const PAGE_LINES = 100;
const flashKey = "testpilot.project-notice.v1";

function element(tag, className, text) {
  const result = document.createElement(tag);
  if (className) result.className = className;
  if (text !== undefined) result.textContent = text;
  return result;
}

function glyph(name) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "ico");
  svg.setAttribute("aria-hidden", "true");
  const use = document.createElementNS(svg.namespaceURI, "use");
  use.setAttribute("href", "#i-" + name);
  svg.append(use);
  return svg;
}

function setPanel(name) {
  document.body.dataset.panel = name;
  for (const button of document.querySelectorAll("#project-panels button")) {
    button.setAttribute("aria-pressed", String(button.dataset.panel === name));
  }
}

function state(box, kind, title, detail) {
  box.hidden = false;
  box.dataset.state = kind;
  box.querySelector("h3").textContent = title;
  box.querySelector("p").textContent = detail;
}

// Feedback belongs to a single navigation and only to the returned immutable record.
function announceAfterNavigation(project, file, message) {
  try { sessionStorage.setItem(flashKey, JSON.stringify({project: String(project), file: String(file), message})); }
  catch { /* Private browsing can disable session storage. */ }
}

function readAnnouncement(project, file) {
  try {
    const value = sessionStorage.getItem(flashKey);
    sessionStorage.removeItem(flashKey);
    const item = JSON.parse(value);
    if (item?.project === project && item.file === file) return item.message;
  } catch { /* Selection and import remain available without browser storage. */ }
  return "";
}

function groupFiles(files) {
  const groups = new Map();
  for (const file of files) {
    // The column uses SQLite NOCASE, which folds ASCII letters only.
    const key = file.filename.replace(/[A-Z]/g, c => c.toLowerCase());
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(file);
  }
  for (const versions of groups.values()) versions.sort((a, b) => b.revision - a.revision);
  return groups;
}

export function showProjectList($, projects, projectId, link) {
  const search = $("project-search");
  function render() {
    const term = search.value.trim().toLowerCase();
    const items = projects.filter(p => p.name.toLowerCase().includes(term)).map(p => {
      const selected = String(p.id) === projectId;
      const a = element("a", "tree-row project-row");
      a.dataset.projectId = p.id;
      a.href = link("projects", {project: p.id, file: ""});
      a.title = p.name;
      if (selected) a.setAttribute("aria-current", "page");
      a.append(glyph(selected ? "folder-open" : "folder"), element("span", "row-label", p.name));
      if (selected) a.append(element("span", "chosen-dot"));
      return a;
    });
    $("project-list").replaceChildren(...items);
    $("project-empty").hidden = items.length > 0;
    $("project-empty").textContent = projects.length ? "没有匹配的项目。" : "尚无项目。可在下方创建。";
  }
  $("project-total").textContent = projects.length;
  search.oninput = render;
  render();
}

function setupVersions($, groups, current, project, link) {
  const expanded = new Set();
  const search = $("file-search");
  const host = $("file-groups");
  const versionLink = f => link("projects", {project: project.id, file: f.id});
  for (const [key, versions] of groups) {
    if (versions.some(v => v.id === current?.id)) expanded.add(key);
  }

  function render() {
    const blocks = [];
    const term = search.value.trim().toLowerCase();
    for (const [key, versions] of groups) {
      const latest = versions[0];
      if (!latest.filename.toLowerCase().includes(term)) continue;
      const open = expanded.has(key);
      const block = element("section", "file-family");
      const active = versions.some(v => v.id === current?.id);
      if (active) block.dataset.selected = "";
      const head = element("div", "file-family-head");
      const toggle = element("button", "family-toggle");
      toggle.type = "button";
      toggle.dataset.groupToggle = key;
      toggle.setAttribute("aria-label", (open ? "收起 " : "展开 ") + latest.filename + " 的版本");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-controls", "revisions-" + latest.id);
      toggle.append(glyph("chevron-right"));
      toggle.onclick = () => {
        if (open) expanded.delete(key); else expanded.add(key);
        render();
        host.querySelector('[data-group-toggle="' + CSS.escape(key) + '"]')?.focus({preventScroll:true});
      };
      const a = element("a", "file-title");
      a.href = versionLink(latest);
      a.dataset.fileLatest = latest.id;
      a.title = latest.filename;
      a.append(glyph("file"), element("span", "row-label", latest.filename));
      const count = element("span", "versions-count", versions.length + " 个版本");
      const headRevision = element("span", "row-version head-latest", "v" + latest.revision);
      headRevision.title = "最新修订 v" + latest.revision;
      head.append(toggle, a, headRevision, count);
      const history = element("div", "version-history");
      history.id = "revisions-" + latest.id;
      history.hidden = !open;
      if (open) {
        for (const f of versions) {
          const item = element("a", "version-entry");
          item.href = versionLink(f);
          item.dataset.fileId = f.id;
          item.title = f.filename + " · v" + f.revision + " · SHA-256 " + f.sha256;
          if (f.id === current?.id) item.setAttribute("aria-current","true");
          item.append(element("span","timeline-dot"), element("span","row-version revision-badge","v" + f.revision));
          if (f.id === latest.id) item.append(element("span","latest-badge","最新"));
          item.append(element("code","hash-short",f.sha256.slice(0, 10)), element("span","record-id","#" + f.id));
          history.append(item);
        }
      }
      block.append(head, history);
      blocks.push(block);
    }
    host.replaceChildren(...blocks);
    if (blocks.length) $("files-empty").hidden = true;
    else if (!project) state($("files-empty"),"empty","选择一个项目","创建项目后即可导入 Python 文件。");
    else if (groups.size) state($("files-empty"),"empty","没有匹配的文件","更换文件名关键词，或清空搜索条件。");
    else state($("files-empty"),"empty","项目中尚无文件","在上方选择 .py 文件，点击“导入文件”保存第一个版本。");
  }
  search.disabled = !groups.size;
  search.oninput = render;
  render();
}

function setupSource($, source) {
  const {lines, offsets} = splitSource(source);
  const spans = tokenize(lines);
  let start = 0;
  function render() {
    const end = Math.min(start + PAGE_LINES, lines.length);
    const rows = document.createDocumentFragment();
    for (let i = start; i < end; i++) {
      const row = element("span", "ai-source-line pc-source-line");
      const number = element("span", "ai-line-no");
      number.dataset.number = i + 1;
      number.setAttribute("aria-hidden", "true");
      row.append(number, colorLine(lines[i], spans[i]));
      // Preserve original CR, LF, or CRLF for raw text selection and tests.
      const newline = element("span", "", source.slice(offsets[i] + lines[i].length, offsets[i + 1]));
      newline.hidden = true;
      row.append(newline);
      rows.append(row);
    }
    $("source").replaceChildren(rows);
    $("source").parentElement.scrollTop = 0;
    $("source").parentElement.hidden = !lines.length;
    $("source-empty").hidden = Boolean(lines.length);
    $("source-pager").hidden = lines.length <= PAGE_LINES;
    $("source-prev").disabled = start === 0;
    $("source-next").disabled = end === lines.length;
    $("source-page-range").textContent = (start + 1) + "–" + end + " / " + lines.length + " 行";
  }
  $("source-prev").onclick = () => { start -= PAGE_LINES; render(); };
  $("source-next").onclick = () => { start += PAGE_LINES; render(); };
  render();
}

function showInspector($, detail, project, link, message) {
  $("inspect-project").textContent = project.name;
  $("inspect-file").textContent = detail.filename;
  $("file-id").textContent = detail.id;
  $("file-version-id").textContent = detail.id;
  $("revision").textContent = "v" + detail.revision;
  $("digest-revision").textContent = "v" + detail.revision;
  $("digest-value").textContent = detail.sha256;
  $("file-byte-size").textContent = new TextEncoder().encode(detail.source).length + " B";
  setupSource($, detail.source);
  $("copy-source").onclick = async () => {
    try {
      await navigator.clipboard.writeText(detail.source);
      message("已复制 " + detail.filename + " · v" + detail.revision + " 的完整源码。");
    } catch { message("浏览器未允许复制，可在源码预览中选择文本。", true); }
  };
  $("analyze-version").href = link("analysis", {project: project.id, file: detail.id});
  $("inspect-empty").hidden = true;
  $("source-panel").hidden = false;
}

export function showProjectsError($, error) {
  $("connection-state").dataset.state = "error";
  $("connection-state").textContent = "读取失败";
  $("source-panel").hidden = true;
  $("analyze-version").removeAttribute("href");
  $("notice").textContent = error.message;
  $("notice").setAttribute("data-error","");
  state($("inspect-empty"), "error", "无法读取项目数据", error.message);
  if (!$("file-groups").childElementCount) state($("files-empty"), "error", "读取失败", "请重新读取项目与版本。");
  if (!$("project-list").childElementCount) $("project-empty").textContent = "项目列表暂不可用。";
  $("project-retry").hidden = false;
  $("project-retry").onclick = () => location.reload();
}

export function bindProjectPanels() {
  for (const tab of document.querySelectorAll("#project-panels button")) tab.onclick = () => setPanel(tab.dataset.panel);
}

export async function showProjects({$, api, link, projects, files, projectId, fileId, params, form, message}) {
  const project = projects.find(p => String(p.id) === projectId);
  const listed = files.find(f => String(f.id) === fileId);
  const groups = groupFiles(files);
  setPanel(!project ? "projects" : listed && params.has("file") ? "details" : "files");
  setupVersions($, groups, listed, project, link);
  $("project-title").textContent = project?.name || "项目工作区";
  $("project-key").textContent = project ? "项目 #" + project.id : "尚未选择项目";
  $("project-file-totals").textContent = groups.size + " 个文件 · " + files.length + " 个版本";
  $("create-button").disabled = false;
  $("upload").disabled = $("import-button").disabled = !project;
  $("upload").onchange = () => {
    const label = $("upload").files[0]?.name || "选择 .py 文件";
    $("upload-name").textContent = label;
    $("upload-name").title = label;
  };

  form("create-project", async () => {
    const row = await api("/api/projects", {name: $("project-name").value});
    announceAfterNavigation(row.id, "", "已创建项目 " + row.name + "。");
    location.assign(link("projects", {project: row.id, file: ""}));
  });
  form("import-file", async () => {
    const selected = $("upload").files[0];
    if (!project || !selected) throw new Error("请选择项目和本地 Python 文件。");
    if (selected.size > 131072) throw new Error("文件超过 128 KiB。");
    let source;
    try { source = new TextDecoder("utf-8", {fatal:true}).decode(await selected.arrayBuffer()); }
    catch { throw new Error("无法读取 UTF-8 源码。请检查文件编码。"); }
    const row = await api("/api/projects/" + project.id + "/files", {filename:selected.name, source});
    if (row.project_id !== project.id) throw new Error("导入结果与当前项目不匹配，请重新读取。");
    const reused = files.some(f => f.id === row.id);
    announceAfterNavigation(project.id, row.id, (reused ? "相同内容，已复用 " : "已导入 ") + row.filename + " · v" + row.revision + "。");
    location.assign(link("projects", {project:project.id, file:row.id}));
  });

  const invalid = (params.has("project") && projectId !== params.get("project"))
    || (params.has("file") && fileId !== params.get("file"));
  if (invalid) {
    showProjectsError($, new Error("当前链接的项目或文件版本不可用。请重新选择项目或文件。"));
    return;
  }
  if (listed) {
    const detail = await api("/api/files/" + listed.id);
    if (!project || detail.project_id !== project.id || detail.id !== listed.id ||
        detail.filename !== listed.filename || detail.revision !== listed.revision || detail.sha256 !== listed.sha256) {
      throw new Error("返回的文件与所选不可变版本不一致。请重新读取。");
    }
    showInspector($, detail, project, link, message);
  }
  $("connection-state").dataset.state = "ok";
  $("connection-state").textContent = "已连接";
  message(readAnnouncement(projectId, fileId) || (project ? "已载入项目 " + project.name + "。" : "创建第一个项目后即可导入文件。"));
}
