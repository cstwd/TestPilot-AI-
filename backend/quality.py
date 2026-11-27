"""Render and export exactly the same quality evidence for a selected run."""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from .bugs import bug_record
from .runs import run_record
from .store import connect, many, one

router = APIRouter(prefix="/api")


def metrics(run):
    counts = {name: run[name] for name in ("passed", "failed", "errors", "skipped")}
    measured = sum(counts.values()) - counts["skipped"]
    observations = {
        "passed": "本次已执行的测试通过。请结合跳过项与未覆盖行判断剩余风险。",
        "failed": "存在断言失败。请查看失败节点和输入预期，再决定是否登记缺陷。",
        "error": "执行或收集出现错误。请先检查日志和环境，再解释通过率。",
        "timeout": "运行超时，未取得完整的测试结果。",
        "skipped": "所有用例被跳过，本次没有可用于判定是否通过的用例。",
    }
    return {**counts, "total": sum(counts.values()),
            "pass_rate_pct": round(100 * counts["passed"] / measured, 2) if measured else None,
            "covered_lines": run["covered_lines"], "total_lines": run["total_lines"],
            "coverage_pct": run["coverage_pct"], "assessment": observations[run["status"]]}


def build_report(path, key):
    with connect(path) as db:
        # Keep run, bug state and regression history in a single SQLite read snapshot.
        db.execute("BEGIN")
        run = run_record(db, key)
        project = one(db, "SELECT id,name FROM projects WHERE id=?", (run["project_id"],))
        source = one(db, "SELECT id,filename,revision,sha256 FROM files WHERE id=?", (run["file_id"],))
        suite = one(db, "SELECT id,target,mode,sha256,file_id FROM suites WHERE id=?", (run["suite_id"],))
        related = many(db, "SELECT id FROM bugs WHERE run_id=? UNION SELECT bug_id FROM regressions "
                       "WHERE run_id=? ORDER BY 1", (key, key))
        return {"schema": "testpilot.quality.v1", "project": project,
                "run": {k: run[k] for k in ("id", "status", "created_at", "duration_ms", "exit_code")},
                "source": source, "suite": suite, "quality": metrics(run),
                "metric_notes": "通过率 = 通过 / (通过 + 失败 + 错误)，跳过单列；"
                                "行覆盖率按被测单文件实际覆盖行 / 可执行行计。无可用分母时为 null。"
                                "缺陷状态取本次查看或导出时的记录，原运行的计数和日志保留。",
                "environment": run.get("environment"), "cases": run["cases"], "log": run["log"],
                "bugs": [bug_record(db, b["id"]) for b in related]}


@router.get("/runs/{run_id}/report")
def report(run_id: int, request: Request):
    return build_report(request.app.state.db_path, run_id)


@router.get("/runs/{run_id}/report/export")
def export(run_id: int, request: Request):
    return JSONResponse(report(run_id, request), headers={
        "Content-Disposition": f'attachment; filename="testpilot-run-{run_id}.json"'
    })
