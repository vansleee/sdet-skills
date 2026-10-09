#!/usr/bin/env python3
"""檢查維護 skill 的設定契約：照 config-resolution 解析專案，產品與風格不跨專案混用。"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent


def check_skill(name, content):
    problems = []
    if "`projects/<project>/config/test-style.md`" not in content:
        problems.append(f"{name}: 缺少 projects/<project>/config/test-style.md")
    if "references/config-resolution.md" not in content:
        problems.append(f"{name}: 沒有指向 references/config-resolution.md")
    if re.search(r"projects/(?!<project>/)[^/\s`]+/config/", content):
        problems.append(f"{name}: 不得寫死具名專案的設定路徑")
    if name in {"test-author", "api-test-author"} and "`projects/<project>/config/product-context.md`" not in content:
        problems.append(f"{name}: 缺少 projects/<project>/config/product-context.md")
    return problems


def main():
    problems = []
    for name in ("test-author", "api-test-author", "test-heal"):
        content = (ROOT / "skills/maintain" / name / "SKILL.md").read_text()
        problems.extend(check_skill(name, content))
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print("維護設定契約通過：3 支 skill 照 config-resolution 解析同一個專案")
    return 0


if __name__ == "__main__":
    sys.exit(main())
