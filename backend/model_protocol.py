"""Frozen wire schemas for the production model."""
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Protocol(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Probe(Protocol):
    ok: Literal[True]


class GeneratedCode(Protocol):
    code: str = Field(min_length=1, max_length=131072)


class Understanding(Protocol):
    functions: list[str]
    parameters: list[tuple[str, str | None, str | None]]
    return_value: Any
    branch_lines: list[int]
    boundary_value: Any
    exception: str | None
    defect_line: int | None


class MutationCase(Protocol):
    disposition: Literal["test", "no_distinguishing_case"]
    call: str | None
    expected: Any
    reason: str = Field(min_length=1, max_length=160)
