
"""List public sample paths without opening the answer key."""
import argparse
import json
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tier", choices=("good", "buggy", "challenge"))
    parser.add_argument("--domain", choices=("math", "people", "commerce", "data", "algorithms", "time"))
    args = parser.parse_args()
    modules = json.loads((LAB / "scenarios/modules.json").read_text(encoding="utf-8"))
    for row in modules:
        if (not args.tier or row["tier"] == args.tier) and (not args.domain or row["domain"] == args.domain):
            print(f"{row['domain']:12} {row['tier']:9} {row['path']}  {', '.join(row['targets'])}")


if __name__ == "__main__":
    main()
