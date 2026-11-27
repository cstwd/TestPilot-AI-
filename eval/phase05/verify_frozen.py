"""Verify the archived Phase 05 model evaluation without loading a model."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import traceback

from .aggregate import ARMS, cases, summarize
from .audit import LAB, RAW, REPORT
from .corpus import SEEDS, SPEC, freeze


def read_json(path):
    return json.loads(path.read_bytes())


def verify():
    if not __debug__:
        raise ValueError("Run without Python optimization so archive assertions remain enabled")

    frozen = LAB / "frozen.json"
    reference = REPORT / "summary.json"
    if json.loads(json.dumps(freeze())) != read_json(frozen):
        raise ValueError("Frozen sources, rubric, seeds or mutation manifest differ")

    expected = read_json(reference)["groups"]
    groups = {}
    for arm in ARMS:
        observed = summarize(cases(arm, require_complete=True))
        if observed["run_count"] != len(SPEC) * len(SEEDS):
            raise ValueError(f"Arm {arm} has an incomplete campaign count")
        differences = sorted(key for key in observed.keys() | expected[arm].keys()
                             if observed.get(key) != expected[arm].get(key))
        if differences:
            raise ValueError(f"Arm {arm} differs from the archived summary: {', '.join(differences)}")
        groups[arm] = {"label": ARMS[arm], **observed}

    large = read_json(RAW / "audit.json")
    small = read_json(RAW / "small-identity.json")
    return {
        "outcome": "passed",
        "method": "offline replay of archived model and WASI receipts",
        "source_commit": "8923f2c37ce46afb79ef2c844e939d749d4c34be",
        "inputs": {p.name: hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest()
                   for p in (frozen, reference)},
        "models": {
            "A": {"name": small["name"], "ollama_digest": small["digest"]},
            "B": {"name": "Versioned template"},
            "C/D": {"name": "Qwen3.8-27B UD-IQ3_XXS", "weight_sha256": large["sha256"],
                    "revision": large["pin"]},
        },
        "seeds": SEEDS,
        "project_count": len(SPEC),
        "groups": groups,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="Also save the JSON result to this path")
    args = parser.parse_args()
    try:
        report = verify()
    except (OSError, ValueError, KeyError, AssertionError, StopIteration):
        traceback.print_exc(file=sys.stderr)
        report = {"outcome": "failed", "error": traceback.format_exc().splitlines()[-1]}
    output = json.dumps(report, ensure_ascii=True, indent=2) + "\n"
    print(output, end="")
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        # A run report must never replace a frozen input or an earlier receipt.
        with args.report.open("x", encoding="utf-8") as stream:
            stream.write(output)
    return 0 if report["outcome"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
