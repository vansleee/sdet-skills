#!/usr/bin/env python3
"""把 Ulysses 匯出的 reference link 轉回 inline，順便清掉它留下的髒東西。

用法：
    python3 scripts/fix-ulysses-export.py book/day-03-workspace-setup.md ...
    python3 scripts/fix-ulysses-export.py book/*.md          # 沒被弄壞的會自己跳過
    python3 scripts/fix-ulysses-export.py --check book/*.md  # 只檢查，不寫入

為什麼要這支：book/ 的稿子在 Ulysses 進出之後，連結會變成
`[標題][1]` 加文末 `[1]:\thttps://…` 的 reference 形式，圖片變成 `![alt][image-1]`，
檔尾的換行也會不見，偶爾還夾帶 U+00A0。全書其餘篇章一律 inline，
每次手工改一遍太蠢，而且容易漏掉圖片定義造成圖斷掉。

退出碼：--check 之下有檔案需要修就回 1，其餘回 0。
"""

import re
import sys
from pathlib import Path

# 文末的定義行，Ulysses 用 tab 分隔，但也接受空白
DEFINITION = re.compile(r"^\[([^\]]+)\]:[ \t]+(\S+)[ \t]*$", re.M)


def fix(text: str) -> tuple[str, list[str]]:
    """回傳（修好的內容, 做了哪些事）。"""
    notes = []

    if "\xa0" in text:
        notes.append(f"清掉 {text.count(chr(0xa0))} 個不換行空格")
        text = text.replace("\xa0", " ")

    targets = {label: url for label, url in DEFINITION.findall(text)}
    if targets:
        text = DEFINITION.sub("", text)
        used, missing = 0, []
        for label, url in targets.items():
            marker = f"][{label}]"
            hits = text.count(marker)
            if hits:
                text = text.replace(marker, f"]({url})")
                used += hits
            else:
                missing.append(label)
        notes.append(f"{len(targets)} 個定義轉成 inline，替換 {used} 處")
        if missing:
            notes.append(f"**沒有被引用的定義**：{'、'.join(missing)}")

    # 定義行拿掉之後留下的連續空行，收成一個
    collapsed = re.sub(r"\n{3,}\Z", "\n", text)
    if collapsed != text:
        notes.append("收掉檔尾多出來的空行")
        text = collapsed

    if not text.endswith("\n"):
        notes.append("補回檔尾換行")
        text += "\n"

    leftover = re.findall(r"\]\[[^\]]+\]", text)
    if leftover:
        notes.append(f"**還有對不到定義的參照**：{'、'.join(sorted(set(leftover)))}")

    # 跳脫過頭：Ulysses 會把表格裡的 `#` 寫成 `\\#`。只回報，不自動改 ——
    # 反斜線在程式碼與正規表達式裡是合法的，機器分不出來，人看一眼比較快。
    for i, line in enumerate(escaped_punctuation(text), 1):
        notes.append(f"**第 {i} 處疑似跳脫過頭**：{line.strip()[:60]}")

    return text, notes


def escaped_punctuation(text: str):
    """挑出程式碼區塊以外、帶著連續反斜線跳脫的行。"""
    in_fence = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and re.search(r"\\\\[#*_|\[\]]", line):
            yield line


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    paths = [Path(a) for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 0

    dirty = 0
    for p in paths:
        original = p.read_text()
        fixed, notes = fix(original)
        if not notes:
            continue
        print(f"{p}：{'；'.join(notes)}")
        if fixed != original:
            dirty += 1
            if not check_only:
                p.write_text(fixed)

    if not dirty:
        print("沒有需要改寫的檔案。")
    elif check_only:
        print(f"\n{dirty} 個檔案需要修，跑一次不帶 --check 就會改。")
    return 1 if (dirty and check_only) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
