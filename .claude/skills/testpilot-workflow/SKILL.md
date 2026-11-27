---
name: testpilot-workflow
description: Develop and verify a TestPilot AI work package using a reproducible analysis, test, repair and acceptance loop.
---

1. Read `AGENTS.md` and the relevant module acceptance report. Record WP, initial Git revision, current changes and observable completion conditions.
2. Read the affected routes, data and UI boundaries. Choose an ordinary repository fixture and identify the expected result and failure behavior. Add or reuse the smallest meaningful regression. For user code use the application WASI path.
3. Run the targeted verification before editing when reproducing a defect. Record the result. Make a scoped change and rerun. Use the command and diff to diagnose any mismatch before iterating.
4. Run adjacent checks and issue an evidence-backed work record with initial goal, changed paths, commands, observed results, Git reference and review status. Keep evidence links in `collab-log/LOG.md`.

Use the `verify` skill for repeatable regression. For a read-only historical replay use archived data and an isolated temporary work directory.
