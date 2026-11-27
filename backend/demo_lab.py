
"""Durable orchestration of existing TestPilot capabilities for frozen Demo Lab samples."""
from contextlib import ExitStack, contextmanager
import json
import logging
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace
from typing import Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from . import analysis, bugs, demo_lab_catalog as dataset, generation, mutation_store, projects, quality, runs
from .engine_flow import run_saved_suite_task
from .engine_history import stamp
from .model_provider import ModelError
from .model_understanding import understand
from .mutation_flow import run_session
from .mutation_results import test_assertion
from .store import connect, exclusive_file, many, one

router = APIRouter(prefix="/api/demo-lab")
LOG = logging.getLogger(__name__)
STAGES = ("import", "analysis", "generation", "execution", "repair", "regression", "mutation", "report")
SCHEMA = (
    """CREATE TABLE IF NOT EXISTS demo_lab_runs (
        id TEXT PRIMARY KEY, sample TEXT NOT NULL, mode TEXT NOT NULL, status TEXT NOT NULL,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL, evidence TEXT NOT NULL)""",
    "CREATE UNIQUE INDEX IF NOT EXISTS demo_lab_single_active ON demo_lab_runs(status) WHERE status='running'",
    "CREATE INDEX IF NOT EXISTS demo_lab_history ON demo_lab_runs(sample,created_at DESC)",
)
SUMMARY = ("id,sample,mode,status,created_at,updated_at,"
           "json_extract(evidence,'$.bug.status') AS defect_status")


class RunOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mode: Literal["template", "ai"] = "template"
    mutation: bool = True


def interrupt_active(db):
    """An interrupted service leaves its last saved stage readable."""
    for row in many(db, "SELECT id,evidence FROM demo_lab_runs WHERE status='running'"):
        evidence = json.loads(row["evidence"])
        for stage in evidence["stages"].values():
            if stage["status"] == "running":
                stage.update(status="interrupted", message="服务在执行期间停止")
        evidence["message"] = "服务已重启，可新建一次独立演示"
        save(db, row["id"], "interrupted", evidence)


def lock_path(path):
    return Path(str(path) + ".demo-lab.lock")


def workspace_path(main_database):
    return main_database.with_name(main_database.stem + ".demo-lab.sqlite3")


def lab_path(request):
    if not request.app.state.demo_lab_available:
        raise HTTPException(503, "Demo Lab 独立数据库无法使用。请检查运行日志和数据目录。")
    return request.app.state.demo_lab_db_path


def service_context(request):
    # Existing workbench routes use only these two state values to operate on a workspace.
    state = SimpleNamespace(db_path=lab_path(request), generators=request.app.state.generators)
    return SimpleNamespace(app=SimpleNamespace(state=state))


def recover(path):
    try:
        with exclusive_file(lock_path(path), "Demo Lab 已有工作进程"), connect(path, write=True) as db:
            interrupt_active(db)
    except HTTPException as exc:
        if exc.status_code != 409:
            raise


def save(db, key, status, evidence):
    result = db.execute("UPDATE demo_lab_runs SET status=?,updated_at=?,evidence=? WHERE id=? AND status='running'",
                        (status, stamp(), json.dumps(evidence, ensure_ascii=True, allow_nan=False), key))
    if result.rowcount != 1:
        raise RuntimeError("Demo Lab 已失去本次演示的写入所有权")


def run_record(path, key):
    with connect(path) as db:
        row = one(db, "SELECT * FROM demo_lab_runs WHERE id=?", (key,))
    evidence = json.loads(row.pop("evidence"))
    return {"schema": "testpilot.demo-lab.v1", **row, **evidence}


def mutation_summary(result):
    primary = result["before"]
    observed = {event["mutant_id"]: event for event in result["events"]
                if event["phase"] == "before" and event["kind"] == "observation"}
    groups, survivors = {}, []
    for site in result["manifest"]:
        event = observed.get(site["id"])
        status = event["status"] if event else "unrun"
        group = groups.setdefault(site["family"], {"total": 0})
        group["total"] += 1
        group[status] = group.get(status, 0) + 1
        if status == "survived":
            survivors.append({**site, "reason": event["reason"]})
    denominator = primary["total"] - primary["execution_error"] if primary else 0
    return {"by_family": groups, "survivors": survivors,
            "all_score_pct": primary["score_pct"] if primary else None,
            "effective": {"killed": primary["killed"] if primary else 0, "denominator": denominator,
                          "score_pct": round(primary["killed"] * 100 / denominator, 2) if denominator else None}}


class Demonstration:
    def __init__(self, key, item, options, request, evidence):
        self.key, self.item, self.options = key, item, options
        self.request = service_context(request)
        self.path = self.request.app.state.db_path
        self.evidence = evidence
        self.started = perf_counter()

    def checkpoint(self, status="running"):
        self.evidence["duration_ms"] = round((perf_counter() - self.started) * 1000)
        with connect(self.path, write=True) as db:
            save(db, self.key, status, self.evidence)

    @contextmanager
    def stage(self, name):
        step = self.evidence["stages"][name]
        step.update(status="running", started_at=stamp())
        self.checkpoint()
        started = perf_counter()
        try:
            yield step
        except (HTTPException, ModelError) as exc:
            step.update(status="failed", message=str(exc.detail if isinstance(exc, HTTPException) else exc))
            raise
        except Exception:
            step.update(status="failed", message="无法完成此步骤，详见服务日志")
            raise
        else:
            if step["status"] == "running":
                step["status"] = "completed"
        finally:
            step.update(duration_ms=round((perf_counter() - started) * 1000))
            self.checkpoint()

    def skip(self, name, reason):
        self.evidence["stages"][name].update(status="skipped", message=reason)

    def import_original(self):
        with self.stage("import"):
            source = dataset.frozen_source(self.item)
            project = projects.create_project(projects.ProjectInput(
                name=f"Demo Lab · {self.item['name']} · {self.key}"), self.request)
            self.evidence["project"] = project
            filename = self.item["name"] + ".py"
            revision = projects.import_file(project["id"], projects.FileInput(filename=filename, source=source),
                                            self.request)
            self.evidence["original"] = revision
        return revision

    def analyze_source(self, revision):
        with self.stage("analysis"):
            ast_result = analysis.analysis(revision["id"], self.request)
            self.evidence["analysis"] = {"static": ast_result, "ai": {"status": "not_requested"}}
            if not ast_result["valid"] or ast_result["sha256"] != revision["sha256"]:
                raise HTTPException(422, "静态分析与冻结版本不一致")
            if self.options.mode == "ai":
                try:
                    response = understand({revision["filename"]: revision["source"]}, self.item["target"])
                except ModelError as exc:
                    self.evidence["analysis"]["ai"] = {"status": "unavailable", "kind": exc.kind,
                                                        "run_id": exc.run_id, "reason": str(exc)}
                    raise
                self.evidence["analysis"]["ai"] = {"status": "completed", "run_id": response.run_id,
                                                    "result": response.value.model_dump()}

    def generate_suite(self, revision):
        with self.stage("generation"):
            target = self.item["target"]
            if self.options.mode == "ai":
                suite = generation.generate(revision["id"], generation.GenerateInput(target=target, mode="ai"),
                                            self.request)
                provenance = "ai"
            else:
                provenance, code = dataset.contract_suite(self.item, revision["source"])
                suite = generation.save_suite(self.path, revision["id"], target, "template", code,
                                              ["Demo Lab 公开课堂合同" if provenance == "classroom" else "产品本地模板"])
            self.evidence["suite"] = {**suite, "provenance": provenance}
        return suite

    def compare(self, revision, suite, first):
        if not self.item["repair_sha256"]:
            self.skip("repair", "该样本使用原版")
            self.skip("regression", "该样本使用原版")
            return revision, first
        if not first["result_complete"] or first["status"] not in {"passed", "failed"}:
            self.skip("repair", "首次运行缺少有效结果")
            self.skip("regression", "首次运行缺少有效结果")
            return revision, first
        candidates = [failure for failure in first["failures"] if test_assertion(failure, suite["source"])]
        with self.stage("repair"):
            fixed = dataset.frozen_source(self.item, corrected=True)
            repaired = projects.import_file(revision["project_id"],
                                            projects.FileInput(filename=revision["filename"], source=fixed),
                                            self.request)
            self.evidence["corrected"] = repaired
            if candidates:
                candidate = candidates[0]
                self.evidence["finding"] = {
                    **candidate, "verdict": "candidate",
                    "source_location": next((frame for frame in reversed(candidate["frames"])
                                             if frame["path"] == "subject.py"), None),
                }
                if self.evidence["finding"]["source_location"] is None:
                    symbol = next(symbol for symbol in self.evidence["analysis"]["static"]["symbols"]
                                  if symbol["name"] == self.item["target"])
                    self.evidence["finding"]["source_location"] = {
                        "path": "subject.py", "line": symbol["line"], "function": symbol["name"],
                        "precision": "entry",
                    }
                defect = bugs.open_bug(first["id"], bugs.BugInput(
                    nodeid=candidate["nodeid"], title=f"Demo Lab · {self.item['target']} 的测试断言"),
                    self.request)
                self.evidence["bug"] = defect
        with self.stage("regression") as step:
            if candidates:
                defect = bugs.regress_run(self.path, defect["id"], repaired["id"], detailed=True)
                self.evidence["bug"] = defect
                after = runs.read_run(defect["regressions"][0]["run_id"], self.request)
                self.evidence["finding"]["verdict"] = "verified" if defect["status"] == "resolved" else "unconfirmed"
            else:
                after = runs.run_suite(self.path, suite["id"], repaired["id"], detailed=True)
                step["message"] = "同套件对照运行，原版没有可登记的测试断言"
            self.evidence["regression"] = after
        return repaired, after

    def mutate(self, revision, suite, execution):
        if not self.options.mutation or execution["status"] != "passed":
            self.skip("mutation", "本次未启用变异" if not self.options.mutation else "当前版本缺少通过基线")
            return
        with self.stage("mutation") as step:
            task = run_saved_suite_task(self.path, revision["id"], suite["id"])
            self.evidence["engine_task"] = task
            if task["status"] != "completed":
                raise HTTPException(409, "变异准备任务未完成，详见引擎执行记录")
            session = mutation_store.create(self.path, task["id"], feedback_enabled=False)
            self.evidence["mutation_session_id"] = session
            self.checkpoint()
            run_session(self.path, session)
            result = mutation_store.read(self.path, session, full=True)
            self.evidence["mutation"] = {"result": result, **mutation_summary(result)}
            if result["status"] != "completed":
                step.update(status="failed", message=result.get("reason") or "变异会话未完成")

    def conclude(self):
        original, repaired = self.evidence.get("execution"), self.evidence.get("regression")
        bug = self.evidence.get("bug")
        report_status = "completed"
        if original and (original["status"] != "passed" and (not bug or bug["status"] != "resolved")
                         or repaired and repaired["status"] != "passed"):
            report_status = "needs_review"
        if not original or any(step["status"] == "failed" for step in self.evidence["stages"].values()):
            report_status = "failed"
        return report_status

    def run(self):
        try:
            revision = self.import_original()
            self.analyze_source(revision)
            suite = self.generate_suite(revision)
            with self.stage("execution") as step:
                first = runs.run_suite(self.path, suite["id"], revision["id"], detailed=True)
                self.evidence["execution"] = first
                if not first["result_complete"] or first["status"] in {"error", "timeout"}:
                    step.update(status="failed", message=first["diagnostic"] or "执行未产出完整可用结果")
            final_revision, final_execution = self.compare(revision, suite, first)
            self.mutate(final_revision, suite, final_execution)
        except (HTTPException, ModelError) as exc:
            self.evidence["message"] = str(exc.detail if isinstance(exc, HTTPException) else exc)
        except Exception:
            LOG.exception("Demo Lab run %s failed", self.key)
            self.evidence["message"] = "流程中断，详见服务日志"
        for name in STAGES[:-1]:
            if self.evidence["stages"][name]["status"] == "pending":
                self.skip(name, "上一步未完成")
        try:
            with self.stage("report"):
                self.evidence["quality"] = {key: quality.build_report(self.path, self.evidence[key]["id"])
                                            for key in ("execution", "regression") if key in self.evidence}
        except Exception:
            LOG.exception("Demo Lab report %s failed", self.key)
        self.checkpoint(self.conclude())


@router.get("/samples")
def samples(request: Request):
    with connect(lab_path(request)) as db:
        rows = many(db, f"SELECT {SUMMARY} FROM demo_lab_runs ORDER BY created_at DESC")
    latest = {}
    for row in rows:
        latest.setdefault(row["sample"], row)
    return {"samples": [{**item, "latest": latest.get(item["name"])} for item in dataset.catalog().values()],
            "active": next((row for row in rows if row["status"] == "running"), None)}


@router.get("/samples/{name}")
def sample(name: str):
    return dataset.browse_sample(dataset.sample(name))


@router.get("/samples/{name}/runs")
def run_history(name: str, request: Request):
    dataset.sample(name)
    with connect(lab_path(request)) as db:
        return many(db, f"SELECT {SUMMARY} FROM demo_lab_runs WHERE sample=? ORDER BY created_at DESC", (name,))


@router.get("/runs")
def report_index(request: Request):
    with connect(lab_path(request)) as db:
        return many(db, f"SELECT {SUMMARY} FROM demo_lab_runs ORDER BY created_at DESC")


def run_under_lock(workflow, claim):
    with claim:
        workflow.run()


@router.post("/samples/{name}/runs", status_code=202)
def start(name: str, options: RunOptions, request: Request, background: BackgroundTasks):
    item = dataset.sample(name)
    key, now = str(uuid4()), stamp()
    evidence = {"sample_info": item, "options": options.model_dump(),
                "stages": {stage: {"status": "pending"} for stage in STAGES}}
    path = lab_path(request)
    with ExitStack() as claim:
        try:
            claim.enter_context(exclusive_file(lock_path(path), "已有 Demo Lab 演示正在运行"))
        except HTTPException as exc:
            with connect(path) as db:
                active = db.execute("SELECT id FROM demo_lab_runs WHERE status='running'").fetchone()
            raise HTTPException(409, {"message": exc.detail, "id": active["id"] if active else None}) from exc
        with connect(path, write=True) as db:
            interrupt_active(db)
            db.execute("INSERT INTO demo_lab_runs VALUES (?,?,?,?,?,?,?)",
                       (key, name, options.mode, "running", now, now, json.dumps(evidence)))
        record = run_record(path, key)
        background.add_task(run_under_lock, Demonstration(key, item, options, request, evidence), claim.pop_all())
    return record


@router.get("/runs/{run_id}")
def progress(run_id: UUID, request: Request):
    return run_record(lab_path(request), str(run_id))


@router.get("/runs/{run_id}/export")
def export(run_id: UUID, request: Request):
    report = progress(run_id, request)
    if report["status"] == "running":
        raise HTTPException(409, "演示完成后可导出报告")
    return JSONResponse(report, headers={"Content-Disposition": f'attachment; filename="demo-lab-{run_id}.json"'})


@router.get("/runs/{run_id}/quality/{side}")
def saved_quality(run_id: UUID, side: Literal["execution", "regression"], request: Request):
    item = progress(run_id, request).get("quality", {}).get(side)
    if item is None:
        raise HTTPException(404, "该演示尚无对应的 F06 快照")
    return item


@router.get("/runs/{run_id}/mutation")
def saved_mutation(run_id: UUID, request: Request):
    item = progress(run_id, request).get("mutation")
    if item is None:
        raise HTTPException(404, "该演示尚无对应的 F13 快照")
    return item["result"]
