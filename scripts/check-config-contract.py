#!/usr/bin/env python3
"""檢查維護 skill 的既有平面設定契約，避免產品與風格跨專案混用。"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent


def check_skill(name, content):
    problems = []
    if "`config/test-style.md`" not in content:
        problems.append(f"{name}: 缺少預設專案的 config/test-style.md")
    if re.search(r"config/[^/\s`]+/(?:product-context|test-style)\.md", content):
        problems.append(f"{name}: maintain 尚未接多專案，不得混入具名專案設定")
    if name in {"test-author", "api-test-author"} and "`config/product-context.md`" not in content:
        problems.append(f"{name}: 缺少預設專案的 config/product-context.md")
    return problems


def main():
    problems = []
    for name in ("test-author", "api-test-author", "test-heal"):
        content = (ROOT / "skills/maintain" / name / "SKILL.md").read_text()
        problems.extend(check_skill(name, content))
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print("維護設定契約通過：3 支 skill 使用同一個平面預設專案")
    return 0


if __name__ == "__main__":
    sys.exit(main())
