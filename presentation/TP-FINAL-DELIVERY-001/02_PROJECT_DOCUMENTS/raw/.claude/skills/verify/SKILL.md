---
name: verify
description: Run TestPilot AI syntax, focused module or full regression checks and write an acceptance report.
---

From the repository root run `python hooks/verify.py --scope <scope> --report <report-path>` with the project interpreter. Use `toolchain`, `f01` to `f06`, `f13`, `phase05`, or `full`. Keep the run serial because browser processes and WASI jobs share host resources. The command selects repository-owned tests and writes environment, commands, durations, exit codes and captured outputs. The report path must be inside `reports/`.

For browser tests use installed Edge on Windows. For the Phase 05 offline replay also run the aggregator as directed in `eval/phase05/README.md` on the archived artifacts. Report live model checks separately from fixtures and archived results. Diagnose the first failing command and rerun the affected scope before a full rerun.
