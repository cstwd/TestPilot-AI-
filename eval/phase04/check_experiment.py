"""Independently verify a downloaded F13 report against its archived initial engine task."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from uuid import UUID


def digest(text):
    return sha256(text.encode("utf-8")).hexdigest()


def verify(task, report, source):
    assert task["id"] == report["task_id"]
    assert len({event["id"] for event in report["events"]}) == len(report["events"])
    suite = next(r["payload"] for r in task["records"] if r["id"] == report["suite_id"])
    assert digest(source) == report["source_sha256"]
    assert digest(suite["code"]) == suite["sha256"] == report["test_sha256"]
    manifest = {m["id"]: m for m in report["manifest"]}
    assert len(manifest) == len(report["manifest"]) and all(UUID(k) for k in manifest)
    for site in manifest.values():
        edit = site["edit"]
        assert source[edit["start"]:edit["end"]] == edit["old"]
        changed = source[:edit["start"]] + edit["new"] + source[edit["end"]:]
        assert digest(changed) == site["mutated_sha256"] != digest(source)
    print("Session", report["id"], report["status"], "task", task["id"], "initial", suite["mode"])
    feedback = next((e["payload"] for e in report["events"] if e["kind"] == "feedback"), {})
    selection = next((e["payload"] for e in report["events"] if e["kind"] == "selection"), {})
    if feedback:
        print("Feedback", feedback.get("status"), feedback.get("model"), feedback.get("model_digest"))
        print("Accepted by original baseline:", selection.get("accepted_names"), "rejected:", selection.get("rejected_names"))
    for phase in ("before", "after"):
        events = [e for e in report["events"] if e["phase"] == phase]
        scores = report[phase]
        if scores is None:
            assert not any(e["kind"] == "observation" for e in events)
            print(phase, "no valid original baseline")
            continue
        assert scores["total"] == len(manifest)
        baseline, = [e["payload"] for e in events if e["kind"] == "baseline" and e["status"] == "passed"]
        assert baseline["result_complete"] and baseline["exit_code"] == 0 and baseline["passed"] > 0
        code = suite["code"] if phase == "before" else (selection.get("code") or feedback["code"])
        assert code.startswith(suite["code"]) and digest(code) == baseline["test_sha256"]
        assert baseline["source_sha256"] == digest(source)
        observations = [e for e in events if e["kind"] == "observation"]
        assert len({e["mutant_id"] for e in observations}) == len(observations)
        counts = dict.fromkeys(("killed", "survived", "execution_error", "cancelled", "timeout"), 0)
        print(phase, "baseline passed:", baseline["passed"])
        for event in observations:
            site = manifest[event["mutant_id"]]
            measured = event["payload"]["execution"]
            assert measured["source_sha256"] == site["mutated_sha256"]
            assert measured["test_sha256"] == digest(code)
            verdict = event["status"]
            counts[verdict] += 1
            nodes = event["payload"]["nodeids"]
            if verdict == "killed":
                assert measured["result_complete"] and measured["failed"] and not measured["errors"] and nodes
                assert measured["exit_code"] == 1 and set(nodes) == {f["nodeid"] for f in measured["failures"]}
            elif verdict == "survived":
                assert measured["result_complete"] and measured["exit_code"] == 0
            print(f"  L{site['line']}:{site['column']} {site['before']} -> {site['after']}: {verdict}", ", ".join(nodes))
        for status, count in counts.items():
            assert scores[status] == count
        assert scores["unrun"] == len(manifest) - len(observations)
        assert scores["equivalent_candidates"] == sum(int(m["equivalent_candidate"]) for m in manifest.values())
        expected = round(100 * counts["killed"] / len(manifest), 2) if manifest else None
        assert scores["score_pct"] == expected
        print("  full denominator", len(manifest), "score", expected, "verified")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("task", "report", "source"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    verify(json.loads(args.task.read_bytes()), json.loads(args.report.read_bytes()), args.source.read_text(encoding="utf8"))
