
(() => {
  const $ = (id) => document.getElementById(`lab-${id}`);
  const tabs = [...document.querySelectorAll("[data-tab]")];
  const root = "/api/demo-lab";
  const stageLabels = {
    import: "导入", analysis: "静态分析", generation: "生成测试", execution: "执行",
    repair: "修复版本", regression: "回归", mutation: "变异测试", report: "报告",
  };
  const labels = {
    pending: "待执行", running: "执行中", completed: "完成", passed: "通过", failed: "失败",
    error: "执行错误", execution_error: "执行错误", skipped: "已跳过", timeout: "超时", interrupted: "已中断",
    needs_review: "待复核", killed: "杀死", survived: "存活", unrun: "未运行", cancelled: "已取消",
    resolved: "已关闭", open: "待修复",
  };
  const families = {comparison: "比较", arithmetic: "算术", boolean: "布尔",
                    return: "返回值", condition: "条件", exception: "异常"};
  const state = {rows: [], selection: 0, runSelection: 0, item: null, run: null, active: null,
                 submitting: false, timer: null};
  const params = new URLSearchParams(location.search);
  const display = (value) => labels[value] || value || "—";

  function node(tag, text, className) {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    if (className) element.className = className;
    return element;
  }

  function actionLink(text, href) {
    const link = node("a", text);
    link.href = href;
    return link;
  }

  function detail(title, text, open = false) {
    const block = node("details");
    block.open = open;
    block.append(node("summary", title), node("pre", text));
    return block;
  }

  function metric(list, title, value) {
    const wrap = node("div");
    wrap.append(node("dt", title), node("dd", value));
    list.append(wrap);
  }

  async function request(path, body) {
    const response = await fetch(root + path, body ? {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body),
    } : undefined);
    const payload = await response.json();
    if (!response.ok) {
      const reason = payload.detail;
      throw new Error(typeof reason === "string" ? reason : reason?.message || `服务返回 HTTP ${response.status}`);
    }
    return payload;
  }

  function tab(name) {
    for (const button of tabs) {
      const active = button.dataset.tab === name;
      button.setAttribute("aria-pressed", active);
      $(button.dataset.tab).hidden = !active;
    }
  }

  function updateUrl() {
    const url = new URL(location.href);
    url.searchParams.set("sample", state.item.name);
    if (state.run) url.searchParams.set("run", state.run.id);
    else url.searchParams.delete("run");
    history.replaceState(null, "", url);
  }

  async function reportCenter(visible) {
    $("report-center").hidden = !visible;
    $("layout").hidden = visible;
    const url = new URL(location.href);
    if (visible) url.searchParams.set("view", "reports");
    else url.searchParams.delete("view");
    history.replaceState(null, "", url);
    if (!visible) return;
    $("reports-heading").focus();
    $("reports-list").replaceChildren(node("p", "正在读取报告…"));
    const records = await request("/runs");
    const list = document.createDocumentFragment();
    for (const record of records) {
      const row = node("div", undefined, "lab-report-row");
      const button = node("button");
      button.type = "button";
      button.dataset.reportSample = record.sample;
      button.dataset.run = record.id;
      button.append(node("code", record.sample + ".py"),
        node("span", `${display(record.status)} · ${new Date(record.created_at).toLocaleString("zh-CN")}`));
      row.append(button);
      if (record.status !== "running") {
        const download = actionLink("下载 JSON", `${root}/runs/${record.id}/export`);
        download.download = "";
        row.append(download);
      }
      list.append(row);
    }
    $("reports-list").replaceChildren(records.length ? list : node("p", "尚无演示记录"));
  }

  function filter() {
    const term = $("search").value.trim().toLowerCase();
    const rows = state.rows.filter((row) => (!$("tier").value || row.tier === $("tier").value) &&
      (!$("domain").value || row.domain === $("domain").value) &&
      (!term || [row.name, ...row.targets].some((value) => value.includes(term))));
    $("count").textContent = `${rows.length} / ${state.rows.length}`;
    const list = document.createDocumentFragment();
    for (const row of rows) {
      const item = node("li");
      const button = node("button");
      button.type = "button";
      button.dataset.sample = row.name;
      if (state.item?.name === row.name) button.setAttribute("aria-current", "true");
      const badge = node("span", row.tier.toUpperCase(), "lab-tier");
      badge.dataset.tier = row.tier;
      const defect = row.latest?.defect_status;
      const defectLabel = defect ? display(defect) : row.repair_sha256 ? "含预置缺陷" : "无预置缺陷";
      button.append(node("strong", row.name), badge,
        node("small", `${row.domain_label} · ${defectLabel}`),
        node("small", row.latest ? display(row.latest.status) : "未运行"));
      item.append(button);
      list.append(item);
    }
    if (!rows.length) list.append(node("li", "没有匹配的样本", "lab-inline-note"));
    $("samples").replaceChildren(list);
  }

  async function loadIndex(initial = false) {
    const result = await request("/samples");
    state.rows = result.samples;
    state.active = result.active?.id ?? null;
    if (initial) {
      for (const [key, label] of new Map(state.rows.map((row) => [row.domain, row.domain_label]))) {
        $("domain").add(new Option(label, key));
      }
      metric($("totals"), "模块", state.rows.length);
      for (const tier of ["good", "buggy", "challenge"]) {
        metric($("totals"), tier.toUpperCase(), state.rows.filter((row) => row.tier === tier).length);
      }
    }
    filter();
    controls();
  }

  function codePane(title, sha, source) {
    const panel = node("div");
    const heading = node("div", undefined, "lab-code-title");
    const hash = node("code", sha.slice(0, 12));
    hash.title = sha;
    heading.append(node("h4", title), hash);
    panel.append(heading, node("pre", source));
    return panel;
  }

  function renderSample() {
    const item = state.item;
    $("detail").hidden = false;
    $("meta").textContent = `${item.tier.toUpperCase()} · ${item.domain_label} · ${item.corrected ? "有修复版" : "原版"}`;
    $("name").textContent = item.name + ".py";
    $("target").textContent = `${item.target}() · ${item.docstring.split("\n")[0]}`;
    const pair = node("div", undefined, item.corrected ? "lab-code-pair" : "");
    pair.append(codePane("原始源码", item.sha256, item.source));
    if (item.corrected) pair.append(codePane("修复版本", item.repair_sha256, item.corrected));
    $("source").replaceChildren(pair);
    const contract = item.contract;
    $("contract").replaceChildren(node("h4", "可执行的公开测试"),
      node("p", contract.provenance === "classroom" ? "课堂合同" : "产品本地模板", "lab-inline-note"),
      ...contract.cases.map((entry) => node("p", entry.label)), node("pre", contract.code));
    controls();
  }

  function controls() {
    const busy = Boolean(state.active || state.submitting);
    $("run").disabled = busy || !state.item;
    $("run").querySelector("span").textContent = busy ? "演示执行中" : state.run ? "重新执行" : "运行演示";
    $("source-mode").textContent = $("mode").value === "ai" ? "使用 Qwen 源码理解与生成" :
      state.item?.classroom ? "样本提供公开课堂合同" : "使用产品本地模板";
  }

  async function renderHistory(item, token) {
    const rows = await request(`/samples/${item.name}/runs`);
    if (token !== state.selection) return;
    const list = node("ul", undefined, "lab-history-list");
    for (const row of rows) {
      const li = node("li");
      const button = node("button");
      button.type = "button";
      button.dataset.run = row.id;
      if (state.run?.id === row.id) button.setAttribute("aria-current", "true");
      button.append(node("span", `${new Date(row.created_at).toLocaleString("zh-CN")} · ${display(row.status)}`),
        node("code", row.id.slice(0, 8)), node("span", row.mode === "ai" ? "本机 AI" : "模板"));
      li.append(button);
      list.append(li);
    }
    $("history").replaceChildren(rows.length ? list : node("p", "此样本尚无演示记录", "lab-inline-note"));
    return rows;
  }

  async function selectSample(name, runId) {
    const token = ++state.selection;
    $("message").textContent = "";
    const item = await request(`/samples/${name}`);
    if (token !== state.selection) return;
    state.item = item;
    state.run = null;
    renderSample();
    renderRun();
    filter();
    tab("source");
    updateUrl();
    const rows = await renderHistory(item, token);
    if (token !== state.selection) return;
    const chosen = rows.find((row) => row.id === runId) || rows[0];
    if (chosen) await loadRun(chosen.id, token, Boolean(runId));
  }

  function renderStages(run) {
    const list = document.createDocumentFragment();
    for (const [key, title] of Object.entries(stageLabels)) {
      const step = run?.stages[key];
      const li = node("li");
      li.dataset.state = step?.status ?? "pending";
      const time = step?.duration_ms !== undefined ? ` · ${(step.duration_ms / 1000).toFixed(1)} s` : "";
      li.append(node("strong", title), node("span", display(li.dataset.state) + time));
      if (step?.message) li.append(node("span", step.message));
      list.append(li);
    }
    $("steps").replaceChildren(list);
    $("run-state").textContent = run ? `${display(run.status)} · ${run.id.slice(0, 8)}` : "尚未运行";
  }

  function executionCard(title, run, revision, labRun, side) {
    const panel = node("article", undefined, "lab-result-card");
    panel.dataset.outcome = run.status;
    panel.append(node("h4", `${title} · v${revision.revision}`), node("strong", display(run.status)),
      node("p", `通过 ${run.passed ?? "—"} · 失败 ${run.failed ?? "—"} · 错误 ${run.errors ?? "—"} · 跳过 ${run.skipped ?? "—"}`),
      node("p", `运行 #${run.id} · 套件 #${run.suite_id} · ${run.duration_ms} ms`, "lab-inline-note"));
    if (labRun.quality?.[side]) {
      panel.append(actionLink("F06 质量报告", `${root}/runs/${labRun.id}/quality/${side}`));
    }
    return panel;
  }

  function mutations(record, labRun) {
    const block = node("section", undefined, "lab-mutation");
    block.append(node("h4", "F13 变异结果"));
    const before = record.result.before;
    if (!before) {
      block.append(node("p", "缺少通过的原版基线，当前无变异得分。"));
      return block;
    }
    const score = node("dl", undefined, "lab-score");
    for (const [key, value] of Object.entries({
      "变异总数": before.total, "杀死": before.killed, "存活": before.survived,
      "执行错误": before.execution_error, "全量得分": before.score_pct === null ? "—" : `${before.score_pct}%`,
      "有效得分": record.effective.score_pct === null ? "—" : `${record.effective.score_pct}%`,
    })) metric(score, key, value);
    block.append(score, node("p", `全量分母 ${before.total}，有效分母 ${record.effective.denominator}（全量减执行错误）。超时 ${before.timeout}，未运行 ${before.unrun}，取消 ${before.cancelled}，等价候选 ${before.equivalent_candidates}。`));
    const table = node("table", undefined, "lab-table");
    const head = node("tr");
    for (const title of ["算子类型", "杀死 / 总数", "其它观测"]) head.append(node("th", title));
    const tableHead = node("thead");
    tableHead.append(head);
    const body = node("tbody");
    for (const [family, values] of Object.entries(record.by_family)) {
      const row = node("tr");
      const other = Object.entries(values).filter(([key]) => !["killed", "total"].includes(key))
        .map(([key, count]) => `${display(key)} ${count}`).join(" · ");
      row.append(node("td", families[family] || family), node("td", `${values.killed ?? 0} / ${values.total}`),
        node("td", other || "—"));
      body.append(row);
    }
    table.append(tableHead, body);
    block.append(table);
    if (record.survivors.length) {
      block.append(detail("定位存活变异", record.survivors.map((site) =>
        `L${site.line}:${site.column} ${site.operator}\n${site.before} → ${site.after}\n${site.reason}`).join("\n\n")));
    }
    block.append(actionLink("查看 F13 原始会话", `${root}/runs/${labRun.id}/mutation`));
    return block;
  }

  function renderRun() {
    const run = state.run;
    controls();
    renderStages(run);
    const pane = $("result");
    if (!run) {
      pane.replaceChildren(node("p", "运行演示后可查看 Pytest 输出与报告。", "lab-inline-note"));
      return;
    }
    const actions = node("div", undefined, "lab-report-actions");
    if (run.status !== "running") {
      const link = actionLink("下载完整 JSON", `${root}/runs/${run.id}/export`);
      link.download = "";
      actions.append(link);
    }
    actions.append(node("span", `${display(run.status)} · 累计 ${run.duration_ms ?? 0} ms`));
    pane.replaceChildren(actions);
    if (run.message) pane.append(node("p", run.message));
    const pair = node("div", undefined, "lab-result-pair");
    if (run.execution) pair.append(executionCard("原版", run.execution, run.original, run, "execution"));
    if (run.regression) pair.append(executionCard("修复版", run.regression, run.corrected, run, "regression"));
    if (!pair.children.length) pane.append(node("p", "尚未取得 Pytest 运行记录。", "lab-inline-note"));
    else pane.append(pair);
    const extra = node("section", undefined, "lab-observation");
    if (run.bug) extra.append(node("h4", `缺陷 #${run.bug.id} · ${display(run.bug.status)}`),
      node("p", run.bug.nodeid));
    if (run.finding?.source_location) {
      const loc = run.finding.source_location;
      extra.append(node("p", `${loc.function} · 原版 L${loc.line}${loc.precision ? "（函数入口）" : ""}`));
    }
    if (run.execution?.failures.length) extra.append(detail("失败断言与回溯",
      run.execution.failures.map((failure) => [failure.nodeid, failure.exception_type, failure.message,
        ...failure.frames.map((frame) => `  ${frame.path}:${frame.line} ${frame.source}`)].join("\n")).join("\n\n"), true));
    for (const [name, execution] of [["原版", run.execution], ["修复版", run.regression]]) {
      if (execution) extra.append(detail(`${name} Pytest 原始输出`, execution.log || "执行器没有返回文本输出"));
    }
    if (run.suite) extra.append(detail("实际执行的测试源码", run.suite.source));
    if (run.analysis) extra.append(detail("分析与 AI 状态", JSON.stringify(run.analysis, null, 2)));
    if (run.mutation) pane.append(mutations(run.mutation, run));
    if (extra.childElementCount) pane.insertBefore(extra, pane.querySelector(".lab-mutation"));
  }

  async function loadRun(id, token, focusResult) {
    const selection = ++state.runSelection;
    const run = await request(`/runs/${id}`);
    if (token !== state.selection || selection !== state.runSelection || run.sample !== state.item?.name) return;
    state.run = run;
    renderRun();
    updateUrl();
    if (focusResult) tab("result");
  }

  async function poll() {
    if (!state.active) return;
    try {
      const run = await request(`/runs/${state.active}`);
      const selected = state.item?.name === run.sample && state.run?.id === run.id;
      if (selected && state.run.updated_at !== run.updated_at) {
        state.run = run;
        renderRun();
      }
      if (run.status !== "running") {
        state.active = null;
        await loadIndex();
        if (selected) await renderHistory(state.item, state.selection);
        if (!$("report-center").hidden) await reportCenter(true);
        $("message").textContent = "";
      }
    } catch (error) {
      $("message").textContent = `读取执行状态失败，将自动重试。 ${error.message}`;
    } finally {
      if (state.active) state.timer = setTimeout(poll, 850);
      controls();
    }
  }

  async function start() {
    if (state.active || state.submitting) return;
    const item = state.item;
    state.submitting = true;
    controls();
    $("message").textContent = "";
    try {
      const run = await request(`/samples/${item.name}/runs`,
        {mode: $("mode").value, mutation: $("mutation").checked});
      state.active = run.id;
      if (state.item.name === item.name) {
        state.runSelection++;
        state.run = run;
        renderRun();
        updateUrl();
        tab("result");
      }
      clearTimeout(state.timer);
      state.timer = setTimeout(poll, 350);
    } catch (error) {
      $("message").textContent = error.message;
      await loadIndex();
      if (state.active) state.timer = setTimeout(poll, 350);
    } finally {
      state.submitting = false;
      controls();
    }
  }

  const showError = (error) => { $("message").textContent = error.message; };
  for (const id of ["search", "tier", "domain"]) $(id).addEventListener("input", filter);
  $("mode").addEventListener("change", controls);
  $("run").addEventListener("click", () => start().catch(showError));
  $("samples").addEventListener("click", (event) => {
    const button = event.target.closest("[data-sample]");
    if (button) selectSample(button.dataset.sample).catch(showError);
  });
  $("history").addEventListener("click", (event) => {
    const button = event.target.closest("[data-run]");
    if (button) loadRun(button.dataset.run, state.selection, true).catch(showError);
  });
  $("reports-open").addEventListener("click", () => reportCenter(true).catch((error) => {
    $("reports-list").replaceChildren(node("p", error.message));
  }));
  $("reports-close").addEventListener("click", () => {
    reportCenter(false);
    $("reports-open").focus();
  });
  $("reports-list").addEventListener("click", (event) => {
    const button = event.target.closest("[data-report-sample]");
    if (button) {
      reportCenter(false);
      selectSample(button.dataset.reportSample, button.dataset.run).catch(showError);
    }
  });
  for (const button of tabs) button.addEventListener("click", () => tab(button.dataset.tab));

  loadIndex(true).then(() => {
    const selected = state.rows.some((row) => row.name === params.get("sample")) ? params.get("sample") : "unit_scaling";
    if (state.active) state.timer = setTimeout(poll, 650);
    if (params.get("view") === "reports") {
      return Promise.all([reportCenter(true), selectSample(selected, params.get("run"))]);
    }
    return selectSample(selected, params.get("run"));
  }).catch(showError);
})();
