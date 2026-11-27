"""Verify member logs and their repository evidence (no writes or network calls)."""

from collections import Counter
from datetime import datetime
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
MEMBER_DIR = ROOT / "collab-log/members"
MEMBERS = ("陈帅廷", "陈万策", "赵君豪", "马雪朋", "王选中")
INDICES = (
    "collab-log/LOG.md",
    "collab-log/COURSE_HISTORY.md",
    "collab-log/member_contributions.md",
    "docs/COURSE_TEAM_CONTRIBUTIONS.md",
    "docs/COURSE_EVIDENCE_INDEX.md",
)
SECTIONS = (
    "基本信息", "1. 工作背景", "2. 工作目标", "3. 使用工具", "4. 原始任务指令",
    "5. 具体操作过程", "6. 关键技术成果", "7. 测试与验证", "8. Git与交付记录",
    "9. 工作总结", "10. 经验总结", "执行记录说明",
)
RECORD = re.compile(r"^### 操作记录 (\d+)：(.+)\n", re.M)
LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)")
COMMIT = re.compile(r"`([0-9a-f]{7,40})`")


def git(*arguments):
    return subprocess.check_output(["git", *arguments], cwd=ROOT, encoding="utf-8")


def read(file):
    return file.read_text(encoding="utf-8")


def check_links(file, source, errors):
    """Resolve local paths, headings, explicit anchors and GitHub line fragments."""
    targets = set()
    count = 0
    for hit in LINK.finditer(source):
        link = hit[1].removeprefix("<").removesuffix(">")
        if re.match(r"[a-z]+://", link):
            continue
        count += 1
        path, _, fragment = link.partition("#")
        target = (file.parent / unquote(path)).resolve() if path else file
        if not target.is_relative_to(ROOT) or not target.exists():
            errors.append(f"{file.relative_to(ROOT)} 无有效链接目标 {link}")
            continue
        fragment = unquote(fragment)
        if fragment:
            contents = read(target) if target.is_file() else ""
            line_ref = re.fullmatch(r"L(\d+)(?:-L(\d+))?", fragment)
            if line_ref:
                begin = int(line_ref[1])
                valid = 1 <= begin <= int(line_ref[2] or begin) <= len(contents.splitlines())
            else:
                valid = fragment in re.findall(r'<a id="([^"]+)"></a>', contents)
            if not valid:
                errors.append(f"{file.relative_to(ROOT)} 无有效定位 {link}")
                continue
        targets.add(target.relative_to(ROOT).as_posix())
    return targets, count


def verify_record(file, record, number, name, wp, errors, stats):
    match, body = record
    fields = re.split(r"^\*\*([^*\n]+)\*\*[ \t]*$", body, flags=re.M)
    headings = fields[1::2]
    sections = {heading: value.strip() for heading, value in zip(headings, fields[2::2])}
    label = f"{wp} 操作记录 {number}"
    if int(match[1]) != number or headings != list(SECTIONS):
        errors.append(f"{label} 编号、章节或顺序不符")
    if any(not sections.get(heading) for heading in SECTIONS):
        errors.append(f"{label} 存在空白章节")

    info = sections.get("基本信息", "")
    attributes = dict(re.findall(r"^- ([^：\n]+)：(.+)$", info, re.M))
    required = {"责任成员": name, "工作包": wp, "工作主题": match[2], "贡献度归属": "20%"}
    if any(attributes.get(key) != value for key, value in required.items()):
        errors.append(f"{label} 基本信息不完整或归属有误")
    try:
        timestamp = datetime.fromisoformat(attributes.get("工作日期", "")[:19])
    except ValueError:
        errors.append(f"{label} 缺有效工作日期")
        timestamp = datetime.min
    if not attributes.get("工作阶段") or "Codex" not in sections.get("执行记录说明", ""):
        errors.append(f"{label} 缺工作阶段或实际操作者")
    if len(re.findall(r"^\d+\. ", sections.get("5. 具体操作过程", ""), re.M)) < 2:
        errors.append(f"{label} 缺执行步骤")

    targets, _ = check_links(file, body, errors)
    evidence = {target for target in targets if target not in INDICES
                and not target.startswith("collab-log/members/")}
    if not evidence:
        errors.append(f"{label} 缺工程证据")
    stats["evidence"] += bool(evidence)
    prompt = sections.get("4. 原始任务指令", "")
    if "未在仓库" not in prompt and "无该任务独立 Prompt" not in prompt:
        if any("transcripts/" in path for path in LINK.findall(prompt)):
            stats["prompt"] += 1
        else:
            errors.append(f"{label} 缺原始任务链接或缺失说明")
    verification, _ = check_links(file, sections.get("7. 测试与验证", ""), errors)
    if any({"reports", "tests"} & set(Path(target).parts)
           or target.endswith(("_ACCEPTANCE.md", "COURSE_FINAL_REPORT.md", "DESIGN_AUDIT.md"))
           for target in verification):
        stats["verification"] += 1
    else:
        errors.append(f"{label} 缺测试或验收来源")

    commits = COMMIT.findall(sections.get("8. Git与交付记录", ""))
    if commits:
        stats["git"] += 1
    else:
        errors.append(f"{label} 缺实现、归档或基线提交")
    for commit in commits:
        try:
            git("rev-parse", "--verify", "--quiet", f"{commit}^{{commit}}")
        except subprocess.CalledProcessError:
            errors.append(f"{label} 无法解析 Git 提交 {commit}")
    return timestamp


def main():
    errors = []
    stats = Counter()
    expected = [MEMBER_DIR / f"{name}_WP{index:02}_个人操作日志.md"
                for index, name in enumerate(MEMBERS, 1)]
    if set(MEMBER_DIR.glob("*.md")) != set(expected):
        errors.append("个人日志目录应包含五份预期文件")

    counts = {}
    link_total = 0
    detail_targets = set()
    for index, (name, file) in enumerate(zip(MEMBERS, expected), 1):
        if not file.is_file():
            continue
        wp = f"WP{index:02}"
        source = read(file)
        _, links = check_links(file, source, errors)
        link_total += links
        matches = list(RECORD.finditer(source))
        counts[wp] = len(matches)
        if len(matches) < 5:
            errors.append(f"{wp} 操作记录少于 5 条")
        timestamps = []
        for offset, match in enumerate(matches):
            next_start = matches[offset + 1].start() if offset + 1 < len(matches) else len(source)
            body = source[match.end():next_start]
            timestamps.append(verify_record(file, (match, body), offset + 1, name, wp, errors, stats))
            anchor = f"{wp.lower()}-{offset + 1:02}"
            detail_targets.add(f"{file.name}#{anchor}")
            if source.count(f'<a id="{anchor}"></a>') != 1 or f"](#{anchor})" not in source:
                errors.append(f"{wp} 操作记录 {offset + 1} 无唯一可访问锚点")
        if timestamps != sorted(timestamps):
            errors.append(f"{wp} 操作记录时间未排序")

    member_paths = {file.relative_to(ROOT).as_posix() for file in expected}
    for index in INDICES:
        file = ROOT / index
        if not file.is_file():
            errors.append(f"缺索引 {index}")
            continue
        source = read(file)
        targets, links = check_links(file, source, errors)
        link_total += links
        if not member_paths <= targets:
            errors.append(f"{index} 未覆盖五份日志")
        if index.endswith("COURSE_HISTORY.md"):
            for target in detail_targets:
                if f"](members/{target})" not in source:
                    errors.append(f"{index} 缺明细链接 {target}")
        if index.endswith(("member_contributions.md", "COURSE_TEAM_CONTRIBUTIONS.md")):
            rows = re.findall(r"^\| (.*?) \| (.*?) \|.*\|\s*(\d+)%\s*\|$", source, re.M)
            shares = [(re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", member),
                       re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", package), int(value))
                      for member, package, value in rows]
            expected_shares = [(name, f"WP{index:02}", 20)
                               for index, name in enumerate(MEMBERS, 1)]
            if shares != [*expected_shares, ("合计", "五个工作包", 100)]:
                errors.append(f"{index} 份额应为五名成员各 20%、合计 100%")

    total = sum(counts.values())
    if total < 25:
        errors.append("全组操作记录少于 25 条")
    for wp, count in counts.items():
        print(f"{wp}: {count} records")
    print(f"Total: {total}; evidence: {stats['evidence']}/{total}; "
          f"original prompts: {stats['prompt']}/{total}; Git: {stats['git']}/{total}; "
          f"test/acceptance: {stats['verification']}/{total}; local links: {link_total}")
    for error in dict.fromkeys(errors):
        print(error, file=sys.stderr)
    print("FAIL" if errors else "PASS")
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
