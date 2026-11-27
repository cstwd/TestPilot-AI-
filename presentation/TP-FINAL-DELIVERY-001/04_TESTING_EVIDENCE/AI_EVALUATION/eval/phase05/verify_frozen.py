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


ARCHIVE_SHA256 = {
    "frozen.json": "fa35592d0f4d0b6dd0a8f03466a2f664d7ec0b70d32a4faa527c4559db495e86",
    "summary.json": "7528e7614f28937d83ff34e4e684bf5bf6f26fb8b95cdf2aaed63c401aac93ff",
    "audit.json": "a13b1e8b75337039665486b044a5516ab42b86a096a77819a76a2169e76671a3",
    "small-identity.json": "4dab4df1b672279b7130c21dd7216a6f02a6696e2cfd344203e9e93f475ce537",
}


def read_json(path):
    return json.loads(path.read_bytes())


def verify():
    if not __debug__:
        raise ValueError("Run without Python optimization so archive assertions remain enabled")

    frozen = LAB / "frozen.json"
    reference = REPORT / "summary.json"
    large_identity = RAW / "audit.json"
    small_identity = RAW / "small-identity.json"
    paths = (frozen, reference, large_identity, small_identity)
    digests = {p.name: hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest()
               for p in paths}
    for name, digest in digests.items():
        if digest != ARCHIVE_SHA256[name]:
            raise ValueError(f"Frozen archive digest differs: {name}")

    if json.loads(json.dumps(freeze())) != read_json(frozen):
        raise ValueError("Frozen sources, rubric, seeds or mutation manifest differ")

    expected = read_json(reference)["groups"]
    if not isinstance(expected, dict) or expected.keys() != ARMS.keys():
        raise ValueError("Archived summary must contain the four planned arms")
    groups = {}
    for arm in ARMS:
        observed = summarize(cases(arm, require_complete=True))
        if observed["run_count"] != len(SPEC) * len(SEEDS):
            raise ValueError(f"Arm {arm} has an incomplete campaign count")
        archived = expected[arm]
        if not isinstance(archived, dict):
            raise ValueError(f"Archived summary for arm {arm} must be an object")
        if observed != archived:
            missing = observed.keys() ^ archived.keys()
            changed = {key for key in observed.keys() & archived.keys()
                       if observed[key] != archived[key]}
            raise ValueError(f"Arm {arm} differs from the archived summary: {', '.join(sorted(missing | changed))}")
        groups[arm] = {"label": ARMS[arm], **observed}

    large = read_json(large_identity)
    small = read_json(small_identity)
    return {
        "outcome": "passed",
        "method": "offline replay of archived model and WASI receipts",
        "source_commit": "8923f2c37ce46afb79ef2c844e939d749d4c34be",
        "inputs": digests,
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
