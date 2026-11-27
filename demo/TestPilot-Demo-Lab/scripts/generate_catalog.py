
"""Render the public catalog and generate or verify the whole release checksum."""
import argparse
import hashlib
import json
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
MANIFEST = LAB / "SHA256SUMS.txt"
DOMAINS = {"math": "数学计算", "people": "用户与人员业务", "commerce": "电商与订单",
           "data": "数据处理", "algorithms": "算法与数据结构", "time": "日期与物流规则"}


def catalog():
    rows = json.loads((LAB / "scenarios/modules.json").read_text(encoding="utf-8"))
    lines = ["# TestPilot Demo Lab 数据集目录", "",
             "以下文件可独立上传至 F01。用例数来自公开索引，标准答案保存在独立参考区。",
             "", "| 领域 | 类型 | 模块 | 顶层同步函数 | 合同用例 |", "| --- | --- | --- | --- | ---: |"]
    for domain in DOMAINS:
        for row in rows:
            if row["domain"] == domain:
                targets = ", ".join(row["targets"])
                lines.append(f"| {DOMAINS[domain]} | {row['tier'].upper()} | "
                             f"[{row['name']}]({row['path']}) | {targets} | {row['cases']} |")
    return "\n".join(lines) + "\n"


def checksum():
    files = sorted(path for path in LAB.rglob("*") if path.is_file() and path != MANIFEST
                   and not {"__pycache__", ".pytest_cache", ".hypothesis"}.intersection(path.parts))
    return "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(LAB).as_posix()}\n"
                   for path in files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    flags = parser.add_mutually_exclusive_group()
    flags.add_argument("--freeze", action="store_true", help="Write checksums after all reports are final")
    flags.add_argument("--check", action="store_true", help="Verify catalog and every released byte")
    args = parser.parse_args()
    destination = LAB / "DATASET_CATALOG.md"
    if args.check:
        for path, expected in ((destination, catalog()), (MANIFEST, checksum())):
            if path.read_bytes() != expected.encode("utf-8"):
                parser.exit(1, f"Verification failed: {path.name}\n")
        print(f"{len(MANIFEST.read_text(encoding='utf-8').splitlines())} files verified")
    else:
        destination.write_text(catalog(), encoding="utf-8", newline="\n")
        if args.freeze:
            MANIFEST.write_text(checksum(), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
