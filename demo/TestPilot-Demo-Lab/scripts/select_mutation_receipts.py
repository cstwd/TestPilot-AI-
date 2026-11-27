
"""Select only receipts matching the final module SHA and target from actual runs."""
import argparse
from collections import Counter
import json
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def review(report):
    before = report.get("before")
    if report["status"] != "completed" or not before:
        raise ValueError(f"Campaign is not scored: {report['id']}")
    events = [event for event in report["events"] if event["kind"] == "observation" and event["phase"] == "before"]
    baselines = [event for event in report["events"] if event["kind"] == "baseline" and event["phase"] == "before"]
    if len(baselines) != 1 or baselines[0]["payload"]["status"] != "passed":
        raise ValueError(f"Campaign has no successful baseline: {report['id']}")
    mutants = {mutant["id"] for mutant in report["manifest"]}
    if len(events) != len(mutants) or {event["mutant_id"] for event in events} != mutants:
        raise ValueError(f"Unobserved or duplicate mutation: {report['id']}")
    counted = Counter(event["status"] for event in events)
    if before["total"] != len(mutants) or any(before[key] != count for key, count in counted.items()):
        raise ValueError(f"Campaign score counts differ from evidence: {report['id']}")
    if before["score_pct"] != round(100 * before["killed"] / before["total"], 2):
        raise ValueError(f"Campaign score differs from evidence: {report['id']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipts", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, default=LAB / "reports/product_mutation.json")
    args = parser.parse_args()
    inventory = {row["name"]: row for row in load(LAB / "scenarios/modules.json")}
    selection = load(LAB / "scenarios/mutation_demo.json")
    candidates = {}
    for path in args.receipts:
        receipt = load(path)
        for sample in receipt["samples"]:
            report = sample.get("report")
            if report:
                key = (sample["module"], sample["target"], report["source_sha256"])
                candidates[key] = (sample, path.name, receipt["date"])
    result = {"stage": "mutation", "samples": []}
    for selected in selection:
        name, target = selected["module"], selected["target"]
        key = (name, target, inventory[name]["sha256"])
        row, filename, date = candidates[key]
        review(row["report"])
        result["samples"].append({**row, "receipt": filename, "recorded_at": date})
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
