"""Required JSON fields for the eight engine artifacts; retain module-specific evidence."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Evidence(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)


class SourceAnalysis(Evidence):
    valid: bool
    symbols: list[dict]
    diagnostics: list[dict]
    sha256: str | None


class TestStrategy(Evidence):
    target: str
    source_sha256: str
    cases: list[dict]
    contracts: list[dict]


class GeneratedTest(Evidence):
    code: str
    mode: Literal["ai", "template", "rules"]
    sha256: str
    attempts: list[dict]


class TestExecution(Evidence):
    status: Literal["passed", "failed", "skipped", "timeout", "error"]
    passed: int | None = Field(ge=0)
    failed: int | None = Field(ge=0)
    errors: int | None = Field(ge=0)
    skipped: int | None = Field(ge=0)
    result_complete: bool
    cases: list[dict]
    stdout: str
    stderr: str
    exit_code: int | None


class CoverageResult(Evidence):
    covered_lines: int | None
    total_lines: int | None
    covered_branches: int | None
    total_branches: int | None


class FailureAnalysis(Evidence):
    findings: list[dict]


class RepairAttempt(Evidence):
    number: int = Field(ge=1, le=3)
    previous_sha256: str
    reason: str


class TestReport(Evidence):
    stop_reason: str
    initial_execution_id: str | None
    final_execution_id: str | None


class StageError(Evidence):
    error: str


MODELS = {model.__name__: model for model in (
    SourceAnalysis, TestStrategy, GeneratedTest, TestExecution, CoverageResult,
    FailureAnalysis, RepairAttempt, TestReport,
)}
