import {element} from "./run-evidence.js";

export const percent = value => value == null ? null : value + "%";
export const issueLabel = status => ({open: "待修复", resolved: "已解决", verified: "已验证", closed: "已关闭"}[status] || status);

export function metricValues(quality) {
  const measured = quality.passed + quality.failed + quality.errors;
  const rate = percent(quality.pass_rate_pct) ?? "无可计算的用例";
  const coverage = percent(quality.coverage_pct) ?? "未采集";
  const base = quality.covered_lines != null && quality.total_lines != null ?
    quality.covered_lines + " / " + quality.total_lines + " 行" : "覆盖行和可执行行未记录";
  return {measured, rate, coverage, base};
}

const metricDefinitions = [
  ["测试通过率", "读取报告的通过率。通过 ÷（通过 + 失败 + 错误）。跳过独立统计。分母为零时显示“无可计算的用例”。"],
  ["总用例数", "收录用例 = Passed + Failed + Error + Skipped。每种状态来自本次运行的真实用例记录。"],
  ["Passed / Failed / Error / Skipped", "分别显示报告的通过、失败、错误和跳过原始计数。分布图使用全部收录用例作为分母，跳过不进入通过率。"],
  ["行覆盖率", "读取 WASI 实测的覆盖行 ÷ 单文件可执行行。0 / 正数对应 0%。报告无覆盖率时显示“未采集”，已有行数仍保留。"],
  ["关联缺陷", "按本运行的原始失败或回归关系计入。缺陷分布以此报告的关联缺陷数为分母，按报告读取时的状态分组。"],
  ["回归结果", "显示报告保存的回归判定、被测修订与运行 ID。可进入 F04 查看该执行的真实终态。"],
];

function metricCard({key, title, value, detail, meter, kind, missing}) {
  const item = element("div", "quality-metric");
  item.dataset.metric = key;
  const display = element("dd", "", value);
  if (missing) display.dataset.valueKind = "missing";
  item.append(element("dt", "", title), display);
  if (meter != null) {
    const lane = element("div", "quality-meter");
    lane.dataset.kind = kind;
    lane.setAttribute("aria-hidden", "true");
    const fill = element("span");
    fill.style.width = meter + "%";
    lane.append(fill);
    item.append(lane);
  }
  item.append(element("dd", "quality-muted quality-metric-note", detail));
  return item;
}

function chart(bar, legend, groups, total) {
  const fills = document.createDocumentFragment(), labels = document.createDocumentFragment();
  for (const [title, count, kind] of groups) {
    if (total && count) {
      const segment = element("span");
      segment.dataset.kind = kind;
      segment.style.flex = "0 0 " + (100 * count / total) + "%";
      fills.append(segment);
    }
    const item = element("li");
    item.dataset.kind = kind;
    item.append(element("span", "", title), element("strong", "", count + " / " + total));
    labels.append(item);
  }
  bar.hidden = !total;
  bar.replaceChildren(fills);
  legend.replaceChildren(labels);
}

function issueTone(status) {
  return status === "resolved" ? "pass" : status === "open" ? "warn" : "neutral";
}

export function renderMetrics($, data) {
  const q = data.quality;
  const values = metricValues(q);
  $("report-quality").replaceChildren(
    metricCard({key: "pass-rate", title: "测试通过率", value: values.rate,
      detail: q.passed + " / " + values.measured + "（通过 + 失败 + 错误）", meter: q.pass_rate_pct,
      kind: "pass", missing: q.pass_rate_pct == null}),
    metricCard({key: "total", title: "收录用例", value: q.total, detail: "通过、失败、错误、跳过合计"}),
    metricCard({key: "coverage", title: "行覆盖率", value: values.coverage, detail: values.base + "（覆盖 / 可执行）",
      meter: q.coverage_pct, kind: "coverage", missing: q.coverage_pct == null}),
    metricCard({key: "defects", title: "关联缺陷", value: data.bugs.length, detail: "关联本次原始失败或回归运行"}),
  );
  $("case-denominator").textContent = "收录 " + q.total + " 项";
  chart($("quality-case-bar"), $("quality-case-legend"), [
    ["Passed / 通过", q.passed, "pass"], ["Failed / 失败", q.failed, "fail"],
    ["Error / 错误", q.errors, "warn"], ["Skipped / 跳过", q.skipped, "neutral"],
  ], q.total);

  const defects = new Map();
  for (const issue of data.bugs) defects.set(issue.status, (defects.get(issue.status) || 0) + 1);
  $("defect-denominator").textContent = data.bugs.length ? "关联 " + data.bugs.length + " 条" : "无关联缺陷";
  chart($("quality-defect-bar"), $("quality-defect-legend"), [...defects].map(([key, count]) =>
    [issueLabel(key), count, issueTone(key)]), data.bugs.length);

  const definitions = document.createDocumentFragment();
  for (const [label, text] of metricDefinitions) definitions.append(element("dt", "", label), element("dd", "", text));
  $("quality-definitions").replaceChildren(definitions);
  $("metric-notes").textContent = data.metric_notes;
}
