const labels = {
  passed: "通过", failed: "失败", error: "错误", timeout: "超时",
  skipped: "跳过", unavailable: "执行器不可用", running: "运行中",
};
export const labelStatus = value => labels[value] || value || "未记录";

export function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text;
  return node;
}

export function readout(node, values) {
  node.replaceChildren();
  for (const [term, value, tone] of values) {
    const cell = element("div");
    if (tone) cell.dataset.tone = tone;
    cell.append(element("dt", "", term), element("dd", "", value ?? "未记录"));
    node.append(cell);
  }
}

const truncatedNotice = "输出达到上限，本次日志不完整，结果无效。";

export function isTruncated(run) {
  // The legacy result exposes the worker's cut flag only through this appended diagnostic.
  return run.truncated === true || (run.status === "error" && !run.cases?.length &&
    (run.log === truncatedNotice || run.log?.endsWith("\n" + truncatedNotice)));
}

export function runState(run) {
  const {status, log} = run;
  if (status === "passed") return ["执行通过", "ok"];
  if (status === "failed") return ["用例失败", "error"];
  if (status === "timeout") return ["执行超时", "warning"];
  if (status === "skipped") return ["全部跳过", "warning"];
  if (status === "unavailable" || (status === "error" && run.exit_code == null && !run.cases?.length &&
      /(?:^|\n)执行器环境错误：[^\n]*$/u.test(log || ""))) {
    return ["执行器不可用", "warning"];
  }
  if (status === "error") {
    if (isTruncated(run)) return ["执行错误 · 输出截断", "warning"];
    if (log === "隔离执行器忙，请稍后重试。") return ["执行器忙", "warning"];
    return ["执行错误", "error"];
  }
  return [labelStatus(status), status === "running" ? "pending" : "idle"];
}

function caseState(value) {
  const tone = {passed: "ok", failed: "error", error: "error", skipped: "warning"}[value];
  return [labelStatus(value), tone || "idle"];
}

export function setStatus(node, [label, tone]) {
  node.textContent = label;
  node.dataset.tone = tone;
}

export function duration(value) {
  return typeof value === "number" && Number.isFinite(value) ? value + " ms" : "未记录";
}

function badCase(item) {
  return item.outcome === "failed" || item.outcome === "error";
}

function caseName(nodeid) {
  const bracket = nodeid.indexOf("[");
  const delimiter = nodeid.lastIndexOf("::", bracket === -1 ? nodeid.length : bracket - 1);
  return delimiter >= 0 ? nodeid.slice(delimiter + 2) : "收集 · " + nodeid;
}

export function setupPager(node, size, render) {
  let page = 0;
  const previous = node.querySelector('[data-step="-1"]');
  const next = node.querySelector('[data-step="1"]');
  previous.onclick = () => { page--; render(); };
  next.onclick = () => { page++; render(); };
  return {
    reset() { page = 0; },
    slice(items) {
      const start = page * size;
      const end = Math.min(start + size, items.length);
      previous.disabled = page === 0;
      next.disabled = end === items.length;
      node.hidden = items.length <= size;
      node.querySelector("span").textContent = (start + 1) + "–" + end + " / " + items.length;
      return items.slice(start, end);
    },
  };
}

export function bindLog($, announce) {
  let output = "";
  const box = $("run-log");
  const search = $("log-search");
  const copy = $("copy-log");
  search.oninput = () => {
    const query = search.value;
    if (!query) {
      box.textContent = output;
      $("log-match").textContent = "";
      return;
    }
    const literal = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const pattern = new RegExp(literal, "giu");
    const contents = document.createDocumentFragment();
    const markLimit = 300;
    let offset = 0;
    let count = 0;
    for (const match of output.matchAll(pattern)) {
      count++;
      if (count > markLimit) continue;
      contents.append(document.createTextNode(output.slice(offset, match.index)), element("mark", "", match[0]));
      offset = match.index + match[0].length;
    }
    contents.append(document.createTextNode(output.slice(offset)));
    box.replaceChildren(contents);
    $("log-match").textContent = count + " 处匹配" + (count > markLimit ? "，高亮前 " + markLimit + " 处" : "");
    const first = box.querySelector("mark");
    if (first) box.scrollTop = Math.max(0, box.scrollTop + first.getBoundingClientRect().top - box.getBoundingClientRect().top - 8);
  };
  copy.onclick = async () => {
    try {
      await navigator.clipboard.writeText(output);
      announce("已复制原始执行日志。");
    } catch {
      announce("剪贴板不可用，可在终端中选中日志文本。", true);
    }
  };
  return (run, waiting = false) => {
    output = typeof run?.log === "string" ? run.log : "";
    box.textContent = output;
    box.scrollTop = box.scrollLeft = 0;
    box.hidden = search.disabled = copy.disabled = !output.length;
    search.value = "";
    $("log-match").textContent = "";
    $("log-truncation").hidden = !run || !isTruncated(run);
    $("log-empty").hidden = Boolean(output.length);
    $("log-empty").textContent = waiting ? "请求等待中。运行结束并保存后才会返回日志。" :
      run ? "本次运行没有日志输出。" : "选择运行后可读取保存的日志。";
    $("console-run").textContent = run ? "#" + run.id : "";
    $("console-indicator").textContent = waiting ? "等待执行响应" :
      run ? output.length ? "已保存日志" : "无日志输出" : "等待选择运行";
  };
}

export function bindCases($, link, setPanel) {
  let run = null;
  let ordered = [];
  let selected = "";
  let evidence = new Map();
  const search = $("case-search");
  const pager = setupPager($("case-pager"), 32, render);

  function bugLink(item) {
    if (!badCase(item) || !["failed", "error"].includes(run.status) ||
        !item.nodeid.includes("::") || [...item.nodeid].length > 2048) return "";
    return link("bugs", {file: run.file_id, run: run.id, nodeid: item.nodeid});
  }
  function paintInspector(item) {
    $("case-inspector").hidden = !item;
    $("case-inspector-empty").hidden = Boolean(item);
    if (!item) return;
    const name = caseName(item.nodeid);
    $("case-name").textContent = name;
    $("case-nodeid").textContent = item.nodeid;
    setStatus($("case-status"), caseState(item.outcome));
    const details = evidence.get(item.nodeid) || [];
    const frames = details.flatMap(entry => Array.isArray(entry.frames) ? entry.frames : []);
    const locations = frames.filter(frame => frame.path && Number.isInteger(frame.line)).map(frame => frame.path + ":" + frame.line);
    const exceptions = details.map(entry => entry.exception_type).filter(Boolean);
    readout($("case-facts"), [
      ["耗时", duration(item.duration_ms)],
      ["错误类型", [...new Set(exceptions)].join(" / ") || "未记录"],
      ["文件与行号", [...new Set(locations)].join(" / ") || "未记录"],
    ]);
    $("case-evidence").textContent = badCase(item) ?
      (details.length ? "以下明细来自本次运行记录。" : "此用例没有独立的断言与堆栈字段。") :
      "此用例没有失败证据。";
    const assertions = details.map(entry => entry.assertion_diff).filter(Boolean).join("\n\n");
    const stack = details.map(entry => [
      [entry.exception_type, entry.message].filter(Boolean).join(" · "),
      ...((entry.frames || []).map(frame => [frame.path + ":" + frame.line, frame.function, frame.source].filter(Boolean).join("  "))),
    ].filter(Boolean).join("\n")).filter(Boolean).join("\n\n");
    for (const [id, text] of [["case-assertion", assertions], ["case-stack", stack]]) {
      $(id).textContent = text;
      $(id).hidden = !text;
    }
    $("case-log-link").hidden = !badCase(item) || !run.log;
    const href = bugLink(item);
    $("case-bug-section").hidden = !href;
    if (href) $("case-bug").href = href;
    else $("case-bug").removeAttribute("href");
  }
  function render() {
    $("run-cases").replaceChildren();
    const term = search.value.trim().toLowerCase();
    const matched = ordered.filter(item => item.nodeid.toLowerCase().includes(term));
    $("case-count").textContent = term ? matched.length + " / " + ordered.length : String(ordered.length);
    $("case-table").hidden = !matched.length;
    $("case-empty").hidden = Boolean(matched.length);
    $("case-empty").textContent = ordered.length ? "没有匹配的用例。" : "本次运行没有可核对的用例记录。";
    for (const item of pager.slice(matched)) {
      const row = element("tr");
      row.dataset.outcome = item.outcome;
      if (item.nodeid === selected) row.setAttribute("aria-current", "true");
      const identity = element("td");
      const button = element("button", "", caseName(item.nodeid));
      button.type = "button";
      button.onclick = () => {
        for (const entry of $("run-cases").querySelectorAll("[aria-current]")) entry.removeAttribute("aria-current");
        row.setAttribute("aria-current", "true");
        selected = item.nodeid;
        paintInspector(item);
        setPanel("inspector", true);
        if (matchMedia("(max-width: 900px)").matches) $("exec-inspector").scrollIntoView({block: "start"});
      };
      identity.append(button, element("code", "", item.nodeid));
      const status = element("span", "exec-status");
      setStatus(status, caseState(item.outcome));
      const statusCell = element("td");
      statusCell.append(status);
      const error = evidence.get(item.nodeid)?.find(entry => entry.message)?.message;
      const bugCell = element("td");
      const href = bugLink(item);
      if (href) {
        const anchor = element("a", "exec-link", "F05");
        anchor.href = href;
        anchor.setAttribute("aria-label", "在 F05 查看 " + caseName(item.nodeid) + " 的缺陷");
        bugCell.append(anchor);
      } else bugCell.textContent = "—";
      row.append(identity, statusCell, element("td", "", duration(item.duration_ms)),
        element("td", "exec-muted", error || (badCase(item) && run.log ? "详见运行日志" : "—")), bugCell);
      $("run-cases").append(row);
    }
  }
  search.oninput = () => { pager.reset(); render(); };
  $("case-log-link").onclick = () => {
    $("exec-console").open = true;
    const name = selected.includes("::") ? caseName(selected) : selected;
    const input = $("log-search");
    if (run.log.includes(name)) {
      input.value = name;
      input.dispatchEvent(new Event("input"));
    }
  };
  return result => {
    run = result;
    ordered = [...(run?.cases || [])].sort((a, b) => Number(badCase(b)) - Number(badCase(a)));
    evidence = new Map();
    for (const detail of run?.failures || []) {
      if (!evidence.has(detail.nodeid)) evidence.set(detail.nodeid, []);
      evidence.get(detail.nodeid).push(detail);
    }
    selected = ordered[0]?.nodeid || "";
    search.value = "";
    search.disabled = !ordered.length;
    pager.reset();
    render();
    paintInspector(ordered[0]);
  };
}
