import test from "node:test";
import assert from "node:assert/strict";
import {alignLines, assertionEvidence} from "../frontend/static/bug-evidence.js";

test("aligns insertions, removals, replacements, and original line endings", () => {
  const before = ["header\n", "removed\n", "keep\n", "same text\r\n", "end\n"];
  const after = ["header\n", "keep\n", "added\n", "same text\n", "end\n"];
  const diff = alignLines(before, after);
  assert.equal(diff.added, 2);
  assert.equal(diff.removed, 2);
  assert.deepEqual(diff.rows.filter(row => row.equal).map(row => [row.left, row.right]), [[0, 0], [2, 1], [4, 4]]);
  assert.deepEqual(diff.rows.flatMap(row => row.left == null ? [] : [before[row.left]]), before);
  assert.deepEqual(diff.rows.flatMap(row => row.right == null ? [] : [after[row.right]]), after);
  assert.equal(alignLines([], after).added, after.length);
  assert.equal(alignLines(before, []).removed, before.length);
  assert.deepEqual(alignLines([], []).rows, []);
});

test("bounds highly dissimilar comparisons without speculative counts", () => {
  const before = ["start", ...Array.from({length: 2100}, (_, i) => "old " + i), "end"];
  const after = ["start", ...Array.from({length: 1800}, (_, i) => "new " + i), "end"];
  const diff = alignLines(before, after);
  assert.equal(diff.bounded, true);
  assert.equal(diff.added + diff.removed, 0);
  assert.equal(diff.rows.filter(row => row.unpaired).length, 2100);
  assert.equal(diff.rows.filter(row => row.equal).length, 2);
  assert.deepEqual(diff.rows.flatMap(row => row.left == null ? [] : [before[row.left]]), before);
  assert.deepEqual(diff.rows.flatMap(row => row.right == null ? [] : [after[row.right]]), after);
});

const target = {nodeid: "test_generated.py::test_second", outcome: "failed"};
const log = [
  "=== FAILURES ===",
  "___ test_first ___",
  "  assert target(2) == 9",
  "E   AssertionError",
  "___ test_second ___",
  "test_generated.py:8 in test_second",
  "  assert target(-3) == 3",
  "E   AssertionError",
  "=== PASSES ===",
  "=== short test summary info ===",
  "FAILED test_generated.py::test_first - AssertionError",
  "FAILED test_generated.py::test_second - AssertionError",
  "=== 2 failed ===",
].join("\n");

test("uses a uniquely attributable real assertion block or stored structured evidence", () => {
  const run = {log, cases: [target, {nodeid: "test_generated.py::test_first"}]};
  const evidence = assertionEvidence(run, target);
  assert.equal(evidence.structured, false);
  assert.match(evidence.text, /assert target\(-3\) == 3/u);
  assert.doesNotMatch(evidence.text, /target\(2\)/u);
  const structured = assertionEvidence({...run, failures: [{nodeid: target.nodeid, assertion_diff: "saved diff"}]}, target);
  assert.deepEqual(structured, {text: "saved diff", structured: true});
  assert.equal(assertionEvidence({...run, cases: [...run.cases, {nodeid: "another.py::test_second"}]}, target), null);
  assert.equal(assertionEvidence({...run, log: log.replace("FAILED test_generated.py::test_second", "FAILED test_other.py::test_second")}, target), null);
});
