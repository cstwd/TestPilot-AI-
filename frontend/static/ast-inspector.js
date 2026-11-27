import {splitSource, tokenize, colorLine} from "./studio-source.js";

const TYPE_NAMES = {file: "File", class: "Class", function: "Function", method: "Method"};
const TYPE_MARKS = {file: "Py", class: "C", function: "ƒ", method: "m"};
const PARAM_KINDS = {
  positional_only: "仅位置", positional_or_keyword: "位置或关键字", keyword_only: "仅关键字",
  var_positional: "可变位置", var_keyword: "可变关键字",
};
const SOURCE_PAGE = 80;

function element(tag, className, text) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (text != null) el.textContent = text;
  return el;
}

function button(text, label) {
  const el = element("button", "", text);
  el.type = "button";
  if (label) el.setAttribute("aria-label", label);
  return el;
}

function typeMark(node) {
  const mark = element("span", "ai-type-mark", TYPE_MARKS[node.type]);
  mark.dataset.type = node.type;
  mark.setAttribute("aria-hidden", "true");
  return mark;
}

function relationButton(node, onSelect) {
  const control = button("", "定位 " + node.qualified_name);
  control.className = "ai-relation";
  control.dataset.nodeId = node.id;
  control.append(typeMark(node), element("code", "", node.qualified_name), element("span", "ai-arrow", "›"));
  control.onclick = () => onSelect(node.id);
  return control;
}

export function createInspector(container, graph, file, {onSelect}) {
  const byId = new Map(graph.nodes.map(node => [node.id, node]));
  const children = new Map();
  for (const node of graph.nodes) {
    if (!node.parent_id) continue;
    if (!children.has(node.parent_id)) children.set(node.parent_id, []);
    children.get(node.parent_id).push(node);
  }
  const {lines, offsets} = splitSource(file.source);
  let tokens;
  let current = null;
  let tab = "overview";
  let pageStart = 0;
  let focusedLine = 1;
  const tabBar = element("div", "ai-tabs");
  tabBar.setAttribute("role", "tablist");
  tabBar.setAttribute("aria-label", "节点检查器");
  const identity = element("div", "ai-identity");
  identity.hidden = true;
  identity.setAttribute("aria-live", "polite");
  identity.setAttribute("aria-atomic", "true");
  const panel = element("div", "ai-inspect-panel");
  panel.id = "ast-inspector-panel";
  panel.setAttribute("role", "tabpanel");
  const tabs = new Map();
  for (const name of ["Overview", "Source", "Structure"]) {
    const key = name.toLowerCase();
    const control = button(name);
    control.id = "ast-tab-" + key;
    control.setAttribute("role", "tab");
    control.setAttribute("aria-controls", panel.id);
    control.onclick = () => showTab(key);
    tabs.set(key, control);
    tabBar.append(control);
  }
  tabBar.onkeydown = event => {
    const keys = [...tabs.keys()];
    const pos = keys.indexOf(tab);
    const next = {ArrowRight: (pos + 1) % 3, ArrowLeft: (pos + 2) % 3, Home: 0, End: 2}[event.key];
    if (next == null) return;
    event.preventDefault();
    showTab(keys[next]);
    tabs.get(tab).focus();
  };
  container.replaceChildren(tabBar, identity, panel);

  function heading(label, trailing = "") {
    const h = element("h3", "ai-section-heading", label);
    if (trailing) h.append(element("span", "", trailing));
    return h;
  }

  function property(rows, label, value) {
    rows.append(element("dt", "", label), element("dd", "", value));
  }

  function overview() {
    const node = current;
    const group = element("div", "ai-overview");
    if (node.signature) {
      const sig = element("pre", "ai-signature", node.signature);
      group.append(heading(node.type === "class" ? "类定义" : "函数签名"), sig);
    }
    const props = element("dl", "ai-facts");
    property(props, "文件", file.filename);
    property(props, "版本", "v" + file.revision + " · #" + file.id);
    property(props, "行范围", node.start_line == null ? "空文件" : "第 " + node.start_line + "–" + node.end_line + " 行");
    const parent = byId.get(node.parent_id);
    property(props, "父级", parent ? parent.qualified_name : "无（文件根节点）");
    group.append(heading("定义位置"), props);
    if (node.type === "file") {
      group.append(heading("文件摘要", "SHA-256"), element("code", "ai-digest", file.sha256));
    } else {
      if (node.type !== "class") {
        group.append(heading("参数", String(node.parameters.length)));
        const params = element("ul", "ai-params");
        for (const arg of node.parameters) {
          const item = element("li");
          const prefix = {var_positional: "*", var_keyword: "**"}[arg.kind] || "";
          const text = prefix + arg.name + (arg.annotation ? ": " + arg.annotation : "") +
            (arg.default == null ? "" : " = " + arg.default);
          item.append(element("code", "", text), element("small", "", PARAM_KINDS[arg.kind]));
          params.append(item);
        }
        group.append(node.parameters.length ? params : element("p", "ai-empty", "无参数"));
        const ret = element("dl", "ai-facts");
        property(ret, "返回注解", node.returns || "未声明");
        group.append(ret);
      }
      group.append(heading("文档字符串"), element("p", node.docstring ? "ai-docstring" : "ai-empty", node.docstring || "未声明文档字符串"));
    }
    return group;
  }

  function structure() {
    const content = element("div", "ai-structure");
    const parent = byId.get(current.parent_id);
    const direct = children.get(current.id) || [];
    content.append(heading("父节点"), parent ? relationButton(parent, onSelect) : element("p", "ai-empty", "当前为文件根节点"));
    content.append(heading("直接子节点", String(direct.length)));
    if (!direct.length) content.append(element("p", "ai-empty", "此定义没有直接子定义"));
    for (const node of direct) content.append(relationButton(node, onSelect));
    return content;
  }

  function selectLine(number) {
    // Preorder guarantees the last containing definition is the innermost.
    let owner = null;
    for (const node of graph.nodes) {
      if (node.type !== "file" && node.start_line <= number && number <= node.end_line) owner = node;
    }
    if (owner && owner.id !== current?.id) onSelect(owner.id);
    focusedLine = number;
    pageStart = Math.floor((number - 1) / SOURCE_PAGE) * SOURCE_PAGE;
    render();
    panel.querySelector('[data-line="' + number + '"]')?.focus({preventScroll: true});
  }

  function sourceView() {
    const content = element("div", "ai-source");
    const toolbar = element("div", "ai-source-tools");
    toolbar.append(element("code", "ai-filename", file.filename));
    const copy = button("复制代码");
    const selection = current;
    copy.disabled = !lines.length;
    copy.onclick = async () => {
      const text = selection.type === "file" ? file.source : file.source.slice(offsets[selection.start_line - 1], offsets[selection.end_line]);
      try {
        await navigator.clipboard.writeText(text);
        copy.textContent = "已复制";
      } catch {
        copy.textContent = "复制失败，请检查权限";
      }
    };
    toolbar.append(copy);
    content.append(toolbar);
    if (!lines.length) {
      content.append(element("p", "ai-empty", "当前文件没有源码行。"));
      return content;
    }
    if (!tokens) tokens = tokenize(lines);
    const list = element("div", "ai-source-lines");
    list.setAttribute("role", "group");
    list.setAttribute("aria-label", "只读源码，方向键选择行");
    const end = Math.min(pageStart + SOURCE_PAGE, lines.length);
    for (let i = pageStart; i < end; i++) {
      const number = i + 1;
      const row = button("", "第 " + number + " 行 " + lines[i]);
      row.className = "ai-source-line";
      row.dataset.line = number;
      row.tabIndex = number === focusedLine ? 0 : -1;
      if (current.type !== "file" && number >= current.start_line && number <= current.end_line) row.dataset.range = "";
      if (number === focusedLine) row.setAttribute("aria-current", "true");
      row.append(element("span", "ai-line-no", String(number)), colorLine(lines[i], tokens[i]));
      list.append(row);
    }
    list.onclick = event => {
      const row = event.target.closest("[data-line]");
      if (row) selectLine(Number(row.dataset.line));
    };
    list.onkeydown = event => {
      const target = {ArrowDown: focusedLine + 1, ArrowUp: focusedLine - 1, Home: 1, End: lines.length}[event.key];
      if (target == null) return;
      event.preventDefault();
      selectLine(Math.min(lines.length, Math.max(1, target)));
    };
    content.append(list);
    if (lines.length > SOURCE_PAGE) {
      const pager = element("div", "ai-pager");
      for (const [step, label] of [[-1, "上一段"], [1, "下一段"]]) {
        const move = button(label);
        move.disabled = step < 0 ? pageStart === 0 : end === lines.length;
        move.onclick = () => {
          pageStart += step * SOURCE_PAGE;
          focusedLine = pageStart + 1;
          render();
          panel.querySelector('[data-line="' + focusedLine + '"]')?.focus({preventScroll: true});
        };
        pager.append(move);
      }
      pager.append(element("span", "", (pageStart + 1) + "–" + end + " / " + lines.length));
      content.append(pager);
    }
    return content;
  }

  function render() {
    for (const [key, control] of tabs) {
      control.tabIndex = key === tab ? 0 : -1;
      control.setAttribute("aria-selected", String(key === tab));
    }
    panel.setAttribute("aria-labelledby", tabs.get(tab).id);
    const view = current ? {overview, structure, source: sourceView}[tab]() :
      element("p", "ai-empty", "选择画布节点或 Explorer 中的符号，查看定义与源码。");
    panel.replaceChildren(view);
    if (current && tab === "source") {
      const line = panel.querySelector('[data-line="' + focusedLine + '"]');
      if (line) {
        const list = line.parentElement;
        list.scrollTop = Math.max(0, line.offsetTop - list.clientHeight / 3);
      }
    }
  }

  function showTab(name) {
    const key = String(name).toLowerCase();
    if (!tabs.has(key)) return;
    tab = key;
    render();
  }

  function select(id) {
    const next = byId.get(id) || null;
    if (next !== current) {
      identity.hidden = !next;
      identity.toggleAttribute("data-switch", Boolean(current && next));
      if (next) {
        const summary = element("div");
        const title = element("h3", "ai-node-name", next.qualified_name);
        title.title = next.qualified_name;
        summary.append(element("span", "ai-kind", TYPE_NAMES[next.type] + (next.kind === "async_function" ? " · async" : "")), title);
        identity.replaceChildren(typeMark(next), summary);
      } else identity.replaceChildren();
      panel.scrollTop = 0;
    }
    current = next;
    focusedLine = current?.start_line || 1;
    pageStart = Math.floor((focusedLine - 1) / SOURCE_PAGE) * SOURCE_PAGE;
    render();
  }

  render();
  return {select, showTab};
}
