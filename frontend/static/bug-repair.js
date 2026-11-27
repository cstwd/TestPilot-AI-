import {element} from "./run-evidence.js";
import {renderDiff} from "./bug-evidence.js";

const ACTIVE = new Set(["queued", "analyzing", "generating"]);
const STATES = {
  queued: "等待 AI 分析",
  analyzing: "正在分析原始失败",
  generating: "正在生成修复",
  ready: "修复已生成，等待应用",
  applied: "候选版本已保存，等待回归",
  failed: "AI 修复失败",
};

export function bindAiRepair($, api, issue, original, readFile, onApplied) {
  const node = name => $("ai-repair-" + name);
  const endpoint = "/api/bugs/" + issue.id + "/ai-repairs";
  const generate = node("generate");
  const apply = node("apply");
  const status = node("status");
  let record, locked = false, unableToRead = false, regressions = issue.regressions;
  let timer;

  function controls() {
    generate.disabled = locked || (!unableToRead && ACTIVE.has(record?.state));
    generate.textContent = unableToRead ? "重新读取 AI 修复状态" :
      record ? "重新生成修复" : "AI 分析并生成修复";
    apply.hidden = record?.state !== "ready" || node("preview").hidden || unableToRead;
    generate.classList.toggle("primary", apply.hidden);
    apply.disabled = locked;
  }

  function statusText() {
    if (!record) return "使用原始源码、测试套件和失败日志生成候选修复。";
    const last = regressions.find(row => row.file_id === record.applied_file_id);
    const state = last ? (last.status === "resolved" ? "候选回归通过" : "候选回归未通过") :
      STATES[record.state];
    return [state, record.error, record.applied_file_id && "候选文件 #" + record.applied_file_id, record.model]
      .filter(Boolean).join(" · ");
  }

  async function paint(saved) {
    if (saved && (saved.bug_id !== issue.id || saved.base_file_id !== original.id ||
        saved.original_run_id !== issue.run_id || saved.suite_id !== issue.suite_id || !STATES[saved.state])) {
      throw new Error("AI 修复记录与原始失败证据不一致。");
    }
    if (record?.id === saved?.id && record?.state === saved?.state && record?.error === saved?.error &&
        !(saved?.source && node("preview").hidden)) {
      status.textContent = statusText();
      controls();
      return;
    }
    record = saved;
    status.textContent = statusText();
    node("findings").hidden = true;
    node("preview").hidden = true;
    controls();
    if (saved?.analysis) {
      const fields = [["根因", saved.analysis.cause], ["原始位置", "第 " + saved.analysis.line + " 行"],
        ["预期行为", saved.analysis.expected], ["实际行为", saved.analysis.observed], ["修复方案", saved.analysis.plan]];
      node("findings").replaceChildren(...fields.map(([label, value]) => {
        const row = element("div");
        row.append(element("dt", "", label), element("dd", "", value));
        return row;
      }));
      node("findings").hidden = false;
    }
    if (saved?.source) {
      const base = await readFile(original);
      renderDiff(node, base, saved);
      node("base").textContent = original.filename + " · v" + original.revision;
      node("reasons").replaceChildren(...saved.edits.map(edit =>
        element("li", "", "原始第 " + edit.start_line + (edit.start_line === edit.end_line ? "" : "–" + edit.end_line) +
          " 行 · " + edit.reason)));
      node("preview").hidden = false;
      controls();
    }
  }

  function poll() {
    clearTimeout(timer);
    if (ACTIVE.has(record?.state)) timer = setTimeout(refresh, 1500);
  }

  async function refresh() {
    locked = true;
    controls();
    try {
      unableToRead = false;
      await paint((await api(endpoint)).repair);
      poll();
    } catch (error) {
      unableToRead = true;
      status.textContent = "AI 修复状态读取失败 · " + error.message;
    } finally {
      locked = false;
      controls();
    }
  }

  generate.onclick = async () => {
    if (unableToRead) return refresh();
    locked = true;
    controls();
    try {
      await paint(await api(endpoint, {}));
      poll();
    } catch (error) {
      status.textContent = "无法请求 AI 修复 · " + error.message;
    } finally {
      locked = false;
      controls();
    }
  };

  apply.onclick = async () => {
    if (locked || record?.state !== "ready") return;
    locked = true;
    controls();
    try {
      const saved = await api(endpoint + "/" + record.id + "/apply", {});
      if (saved.project_id !== original.project_id || saved.filename !== original.filename ||
          saved.revision <= original.revision || saved.sha256 !== record.sha256) {
        throw new Error("保存的候选文件与预览不一致。");
      }
      await paint({...record, state: "applied", applied_file_id: saved.id});
      await onApplied(saved);
    } catch (error) {
      status.textContent = "应用 AI 修复失败 · " + error.message;
    } finally {
      locked = false;
      controls();
    }
  };

  $("ai-repair").hidden = false;
  controls();
  void refresh();
  return rows => {
    regressions = rows;
    if (record?.state === "applied") status.textContent = statusText();
  };
}
