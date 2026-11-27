"""Compare current JUnit output to the immutable list of Phase 03 tests."""
import argparse
from pathlib import Path
from xml.etree import ElementTree


def outcomes(path):
    result = {}
    for case in ElementTree.parse(path).iter("testcase"):
        name = case.attrib["classname"].replace(".", "/") + ".py::" + case.attrib["name"]
        if name in result:
            raise ValueError(f"duplicate JUnit node {name}")
        result[name] = next((x.tag for x in case if x.tag in {"failure", "error", "skipped"}), "passed")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, nargs="*",
                        help="Print archived node IDs if omitted, otherwise verify each supplied JUnit file.")
    args = parser.parse_args()
    archived = outcomes(Path(__file__).resolve().parents[2] / "reports/phase03/platform-junit.xml")
    assert len(archived) == 89
    if not args.results:
        print("\n".join(archived))
    for path in args.results:
        current = outcomes(path)
        missing = archived.keys() - current.keys()
        problems = {k: v for k, v in current.items() if v != "passed"}
        if missing or problems:
            raise SystemExit(f"{path}: missing={sorted(missing)}, failures/errors/skips={problems}")
        print(f"{path}: all {len(archived)} archived IDs passed; {len(current) - len(archived)} further passed; total {len(current)}")
