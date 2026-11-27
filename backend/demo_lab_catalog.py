
"""Read only the audience-facing Demo Lab files and public classroom contracts."""
import ast
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import re

from fastapi import HTTPException

from .generation import TemplateAdapter, checked

ROOT = Path(__file__).resolve().parents[1] / "demo" / "TestPilot-Demo-Lab"
ASSETS = Path(__file__).resolve().parent
DOMAINS = {"math": "数学计算", "people": "用户与人员", "commerce": "电商与订单",
           "data": "数据处理", "algorithms": "算法与结构", "time": "日期与物流"}
TIERS = {"good", "buggy", "challenge"}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def catalog():
    rows = read_json(ROOT / "scenarios" / "modules.json")
    repairs = read_json(ASSETS / "demo_lab_repairs.json")
    contracts = public_contracts()
    result = {}
    for row in rows:
        name, tier, domain = (row[key] for key in ("name", "tier", "domain"))
        if (name in result or not re.fullmatch(r"[a-z][a-z0-9_]*", name)
                or tier not in TIERS or domain not in DOMAINS
                or row["path"] != f"source/{tier}/{name}.py"
                or (name in repairs) != (tier != "good")):
            raise ValueError(f"无效的 Demo Lab 索引条目 {name}")
        curated = contracts.get(name)
        target = curated["target"] if curated else row["targets"][0]
        if target not in row["targets"]:
            raise ValueError(f"无效的 Demo Lab 目标 {name}")
        result[name] = {"name": name, "tier": tier, "domain": domain, "domain_label": DOMAINS[domain],
                        "targets": row["targets"], "target": target, "sha256": row["sha256"],
                        "repair_sha256": repairs.get(name), "classroom": bool(curated), "contract_count": row["cases"]}
    if set(contracts) - result.keys() or set(repairs) - result.keys():
        raise ValueError("Demo Lab 样本与课堂配置不对应")
    return result


def sample(name):
    item = catalog().get(name)
    if item is None:
        raise HTTPException(404, "Demo Lab 样本不存在")
    return item


def frozen_source(item, *, corrected=False):
    name, tier = item["name"], item["tier"]
    folder = ROOT / "reference" / "corrected" if corrected else ROOT / "source" / tier
    expected = item["repair_sha256"] if corrected else item["sha256"]
    path = folder / f"{name}.py"
    try:
        if not expected or path.resolve() != ROOT.resolve() / path.relative_to(ROOT):
            raise ValueError("样本路径与发布索引不对应")
        data = path.read_bytes()
        if not 0 < len(data) <= 131072 or sha256(data).hexdigest() != expected:
            raise ValueError("样本摘要与发布索引不对应")
        return data.decode("utf-8")
    except (OSError, ValueError) as exc:
        raise HTTPException(503, f"无法验证 Demo Lab 样本版本 {name}") from exc


@lru_cache(maxsize=1)
def public_contracts():
    return read_json(ASSETS / "demo_lab_contracts.json")


def contract_suite(item, source):
    target = item["target"]
    curated = public_contracts().get(item["name"])
    if curated:
        declarations = [f"from subject import {target} as target"]
        for number, case in enumerate(curated["cases"], 1):
            arguments = ", ".join(repr(value) for value in case["args"])
            declarations.append(f"def test_classroom_{number}():\n    assert target({arguments}) == {case['expected']!r}")
        return "classroom", checked("\n\n".join(declarations))
    return "template", checked(TemplateAdapter().generate(source, target)[0])


def browse_sample(item):
    source = frozen_source(item)
    fn = next(node for node in ast.parse(source).body
              if isinstance(node, ast.FunctionDef) and node.name == item["target"])
    provenance, code = contract_suite(item, source)
    return {**item, "source": source, "docstring": ast.get_docstring(fn),
            "contract": {"provenance": provenance, "code": code,
                         "cases": public_contracts().get(item["name"], {}).get("cases", [])},
            "corrected": frozen_source(item, corrected=True) if item["repair_sha256"] else None}
