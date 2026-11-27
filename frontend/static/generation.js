import {labelStatus} from "./runs.js";

export async function showGeneration({$, api, link, form, populate, params, fileId}) {
  const base = "/api/files/" + fileId;
  const [analysis, suites] = await Promise.all([api(base + "/analysis"), api(base + "/suites")]);
  const functions = analysis.symbols.filter(item => item.kind === "function" && !item.name.includes("."));
  const target = $("target");
  populate(target, functions.map(item => ({...item, id: item.name})), item => item.name,
    params.get("symbol"), "没有可用的顶层函数");
  $("generate-button").disabled = !target.value;
  if (!functions.length) $("generation-hint").textContent = analysis.valid ?
    "当前版本没有可用的顶层同步函数。" : "源码存在语法错误，请先修复并重新导入。";
  form("generate", async () => {
    $("notice").textContent = "正在生成测试并核对首次 Pytest 运行，请等待执行完成。";
    const saved = await api(base + "/suites", {target: target.value, mode: "template"}).catch(error => {
      if (error.status === 409) throw new Error("执行器忙。请稍后重试生成，已保存的候选套件会复用。");
      throw error;
    });
    location.assign(link("generation", {suite: saved.id, symbol: saved.target}));
  });
  const select = $("suite");
  populate(select, suites, item => "#" + item.id + " · " + item.target + " · " + item.mode,
    params.get("suite"), "此版本尚无测试");
  select.onchange = () => location.assign(link("generation", {suite: select.value, symbol: target.value}));
  if (!select.value) return;
  const saved = await api("/api/suites/" + select.value);
  $("suite-detail").textContent = saved.mode + " · " + (saved.format_checked ? "语法检查通过" : "语法待核验") +
    " · SHA-256 " + saved.sha256;
  $("test-source").textContent = saved.source;
  for (const item of saved.suggestions.length ? saved.suggestions : ["暂无适用建议。"]) {
    const li = document.createElement("li");
    li.textContent = item;
    $("suggestions").append(li);
  }
  if (saved.initial_run) {
    $("initial-status").textContent = "首次 Pytest 运行 #" + saved.initial_run.id + " · " + labelStatus(saved.initial_run.status);
    $("run-suite").textContent = "查看首次执行记录";
    $("run-suite").href = link("runs", {suite: saved.id, run: saved.initial_run.id});
  } else {
    $("initial-status").textContent = "尚无首次执行记录。";
    $("run-suite").href = link("runs", {suite: saved.id});
  }
  $("suite-panel").hidden = false;
}
