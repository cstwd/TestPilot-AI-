import {colorLine, splitSource, tokenize} from "./studio-source.js";

const MATRIX_LIMIT = 1_500_000;
const PAGE_LINES = 72;

function documentLines(source) {
  const {lines, offsets} = splitSource(source);
  const raw = lines.map((_, i) => source.slice(offsets[i], offsets[i + 1]));
  return {lines, raw, tokens: tokenize(lines)};
}

// Align unchanged lines exactly, comparing their original endings as well as their text.
// Large dissimilar middles are shown unpaired rather than given speculative change markers.
export function alignLines(before, after) {
  let prefix = 0;
  while (prefix < before.length && prefix < after.length && before[prefix] === after[prefix]) prefix++;
  let a = before.length, b = after.length;
  while (a > prefix && b > prefix && before[a - 1] === after[b - 1]) { a--; b--; }

  const rows = [];
  const context = (left, right) => rows.push({left, right, equal: true});
  for (let i = 0; i < prefix; i++) context(i, i);
  const m = a - prefix, n = b - prefix;
  const bounded = m > 0 && n > 0 && (m + 1) * (n + 1) > MATRIX_LIMIT;
  let added = 0, removed = 0;
  if (bounded) {
    for (let k = 0; k < Math.max(m, n); k++) rows.push({
      left: k < m ? prefix + k : null, right: k < n ? prefix + k : null, unpaired: true,
    });
  } else {
    const width = n + 1;
    const score = m && n ? new Uint16Array((m + 1) * width) : null;
    if (score) {
      for (let i = m - 1; i >= 0; i--) {
        for (let j = n - 1; j >= 0; j--) {
          score[i * width + j] = before[i + prefix] === after[j + prefix] ? 1 + score[(i + 1) * width + j + 1] :
            Math.max(score[(i + 1) * width + j], score[i * width + j + 1]);
        }
      }
    }
    let i = 0, j = 0, deletes = [], inserts = [];
    function flush() {
      removed += deletes.length;
      added += inserts.length;
      for (let k = 0; k < Math.max(deletes.length, inserts.length); k++) {
        rows.push({left: deletes[k] ?? null, right: inserts[k] ?? null});
      }
      deletes = [];
      inserts = [];
    }
    while (i < m || j < n) {
      if (i < m && j < n && before[prefix + i] === after[prefix + j]) {
        flush();
        context(prefix + i++, prefix + j++);
      } else if (j < n && (i === m || score[i * width + j + 1] > score[(i + 1) * width + j])) {
        inserts.push(prefix + j++);
      } else {
        deletes.push(prefix + i++);
      }
    }
    flush();
  }
  for (let k = 0; k < before.length - a; k++) context(a + k, b + k);
  return {rows, added, removed, bounded};
}

function lineEnding(text, raw) {
  return {"\n": "LF", "\r\n": "CRLF", "\r": "CR"}[raw.slice(text.length)] || "无行尾";
}

function cell(documentData, index, side, kind, otherLine) {
  const node = document.createElement("div");
  node.className = "bug-diff-cell";
  node.dataset.side = side;
  if (index == null) {
    node.dataset.kind = "absent";
    node.setAttribute("aria-hidden", "true");
    return node;
  }
  node.dataset.kind = kind;
  const no = document.createElement("span");
  no.className = "bug-line-no";
  no.textContent = index + 1;
  no.title = lineEnding(documentData.lines[index], documentData.raw[index]);
  const other = document.createElement("span");
  other.className = "bug-line-no bug-unified-no";
  other.textContent = otherLine == null ? " " : otherLine + 1;
  const marker = document.createElement("span");
  marker.className = "bug-diff-marker";
  marker.textContent = {removed: "−", added: "+", unpaired: "·"}[kind] || " ";
  node.append(no, other, marker, colorLine(documentData.lines[index], documentData.tokens[index]));
  return node;
}

export function renderDiff($, before, after) {
  const oldDoc = documentLines(before.source), newDoc = documentLines(after.source);
  const comparison = alignLines(oldDoc.raw, newDoc.raw);
  const {rows, added, removed, bounded} = comparison;
  const controls = $("diff-pager");
  const box = $("diff-lines");
  const previous = controls.querySelector('[data-step="-1"]');
  const next = controls.querySelector('[data-step="1"]');
  const firstChange = rows.findIndex(row => !row.equal);
  let page = Math.floor(Math.max(0, firstChange - 3) / PAGE_LINES);
  function render() {
    const first = page * PAGE_LINES;
    const end = Math.min(rows.length, first + PAGE_LINES);
    const fragment = document.createDocumentFragment();
    for (const row of rows.slice(first, end)) {
      const line = document.createElement("div");
      line.className = "bug-diff-row";
      if (row.equal) line.dataset.equal = "";
      const kind = row.equal ? "context" : row.unpaired ? "unpaired" : null;
      line.append(cell(oldDoc, row.left, "old", kind || "removed", row.equal ? row.right : null),
        cell(newDoc, row.right, "new", kind || "added"));
      fragment.append(line);
    }
    if (!rows.length) fragment.append(document.createTextNode("两侧均为空文件。"));
    box.replaceChildren(fragment);
    box.scrollTop = 0;
    controls.hidden = rows.length <= PAGE_LINES;
    controls.querySelector("span").textContent = (first + 1) + "–" + end + " / " + rows.length;
    previous.disabled = first === 0;
    next.disabled = end === rows.length;
  }
  const summary = $("diff-summary");
  summary.textContent = bounded ? "改动区较大 · 并列显示原文" :
    added || removed ? "+" + added + " / −" + removed : "源码内容相同";
  summary.hidden = false;
  previous.onclick = () => { page--; render(); };
  next.onclick = () => { page++; render(); };
  render();
}

// Ordinary F04 results store the traceback in raw stdout. Only excerpt a uniquely
// attributable block from the real Pytest failure section and terminal case summary.
export function assertionEvidence(run, item) {
  const structured = run.failures?.filter(value => value.nodeid === item.nodeid && value.assertion_diff);
  if (structured?.length) return {text: structured.map(value => value.assertion_diff).join("\n\n"), structured: true};
  if (item.outcome !== "failed" || typeof run.log !== "string") return null;
  const name = item.nodeid.split("::").at(-1);
  if (run.cases.filter(entry => entry.nodeid.split("::").at(-1) === name).length !== 1) return null;
  const lines = run.log.split(/\r\n?|\n/);
  const summary = lines.findLastIndex(line => /^=+\s+short test summary info\s+=+$/u.test(line.trim()));
  if (summary < 0 || !lines.slice(summary + 1).some(line =>
    line === "FAILED " + item.nodeid || line.startsWith("FAILED " + item.nodeid + " - "))) return null;
  const failures = lines.slice(0, summary).findLastIndex(line => /^=+\s+FAILURES\s+=+$/u.test(line.trim()));
  if (failures < 0) return null;
  let end = lines.findIndex((line, index) => index > failures && /^=+\s+\S.*\s+=+$/u.test(line.trim()));
  if (end < 0 || end > summary) end = summary;
  const block = lines.slice(failures + 1, end);
  const headings = block.map(line => /^_{3,}\s+(.+?)\s+_{3,}$/u.exec(line.trim())?.[1]);
  if (headings.filter(value => value === name).length !== 1) return null;
  const start = headings.indexOf(name);
  const stop = headings.findIndex((value, index) => index > start && value !== undefined);
  const snippet = block.slice(start + 1, stop < 0 ? block.length : stop).join("\n").trimEnd();
  if (!/^\s*(?:>\s*)?assert\b/mu.test(snippet) || !/^\s*E\s+AssertionError\b/mu.test(snippet)) return null;
  return {text: snippet, structured: false};
}
