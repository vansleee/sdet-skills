#!/usr/bin/env python3
"""檢查中文文件是否符合 de-ai-tone 風格規範。

規範全文在使用者的 ~/.claude/skills/de-ai-tone,這裡只自動化「能機器判、
且判得準」的那幾條。稻草人測試、朗讀測試、有沒有立場這類需要判斷力的
規則不在這裡,靠 review。

檢查範圍:版控中的 *.md / *.yaml / *.yml。程式碼(scripts/、*.json)不在
規範管轄內。每個檢查都跳過 code fence 與行內 `code`,YAML 語法行只看註解
部分,避免把 `env:VAR`、`[a, b]` 這種語法當成中文標點。
"""
import re
import subprocess
import sys

CJK = "㐀-鿿"
CJK_RE = re.compile(f"[{CJK}]")

# 半形標點貼著中文。英文脈絡內部的標點(Playwright (TypeScript)、env:VAR)
# 兩側都不是中文,不會被抓到。
HALFWIDTH = re.compile(f"[{CJK}][,;:()]|[,;:()][{CJK}]")

YAML_SYNTAX_LINE = re.compile(r"^\s*(-\s+)?[A-Za-z_][\w.-]*:\s")

# 第 13 條對照表與互聯網黑話。一詞多義的不放進來,誤判成本高於漏抓:
# 質量=mass、水平=horizontal、通過=pass、項目=item、登錄=記錄、程序=程序、
# 運行=運行、保存=保存、設置=設置、代碼=錯誤代碼,這些義項在臺灣都通行。
MAINLAND = re.compile(
    "視頻|音頻|軟件|硬件|網絡|信息|服務器|內存|硬盤|屏幕|鼠標|默認|缺省"
    "|智能|用戶|界面|兼容|調試|文檔|文件夾|菜單|窗口|加載|粘貼|鏈接|打印"
    "|插件|博客|二維碼|渠道|課題|立馬|矢量|標量|概率|仿真|激光"
    "|復盤|沉澱|閉環|抓手|顆粒度|賽道|打通"
)
# 「數據」「優化」「對齊」在特定義項下合法,但這個 repo 已經統一改掉,
# 所以一律擋,要用再個案討論。
MAINLAND_STRICT = re.compile("數據|優化|對齊")

FILLER = re.compile(
    "值得注意的是|需要注意的是|值得一提的是|有趣的是|更重要的是|更關鍵的是"
    "|事實上|毫無疑問|不得不說|從某種意義上|簡單來說|總的來說|綜上所述"
)
BUZZWORD = re.compile("賦能|深入探討|揭示了|至關重要|不可或缺|旨在")
EMOJI = re.compile("[\U0001f300-\U0001faff]")

# 第 2 條:每千字至多一組。
EMDASH_PER_1000 = 1.0


def prose_lines(path):
    """吐出 (行號, 原始行, 可掃描的內容)。fence、行內 code、YAML 語法都剝掉。"""
    in_fence = False
    is_yaml = path.endswith((".yaml", ".yml"))
    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            if raw.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            body = re.sub(r"`[^`]*`", "", raw)
            if is_yaml and YAML_SYNTAX_LINE.match(raw):
                # 只留註解,值與 key 屬於 YAML 語法
                body = re.sub(r"^[^#]*", "", body)
            yield lineno, raw.rstrip("\n"), body


def main():
    files = [
        f
        for f in subprocess.check_output(["git", "ls-files"], text=True).split()
        if f.endswith((".md", ".yaml", ".yml"))
    ]
    problems = []
    emdash_hits = []
    total_cjk = 0

    checks = [
        (HALFWIDTH, "中文旁的半形標點,改全形(第 16 條)"),
        (MAINLAND, "中國用語(第 13 條)"),
        (MAINLAND_STRICT, "中國用語,本 repo 一律不用(第 13 條)"),
        (FILLER, "空轉話語標記,刪掉語意不損(第 4 條)"),
        (BUZZWORD, "貼標語彙(第 5 條)"),
        (EMOJI, "裝飾性 emoji(第 6 條)"),
    ]

    for path in files:
        for lineno, raw, body in prose_lines(path):
            total_cjk += len(CJK_RE.findall(body))
            for pattern, label in checks:
                for m in pattern.finditer(body):
                    problems.append((path, lineno, label, m.group(0), raw))
            for _ in range(body.count("——")):
                emdash_hits.append((path, lineno, raw))

    status = 0
    if problems:
        status = 1
        print(f"{len(problems)} 處違反 de-ai-tone:", file=sys.stderr)
        for path, lineno, label, hit, raw in problems:
            print(f"  {path}:{lineno}  [{label}] 「{hit}」", file=sys.stderr)
            print(f"      {raw.strip()[:110]}", file=sys.stderr)

    budget = int(total_cjk / 1000 * EMDASH_PER_1000)
    if len(emdash_hits) > budget:
        status = 1
        print(
            f"\n破折號 {len(emdash_hits)} 組,超過配額 {budget} 組"
            f"(每千字 {EMDASH_PER_1000:g} 組,全庫中文 {total_cjk} 字)。",
            file=sys.stderr,
        )
        print(
            "正當用途只有插入補充語與語意突轉;當連接詞用的改成逗號、句號或冒號(第 2 條)。",
            file=sys.stderr,
        )
        for path, lineno, raw in emdash_hits:
            print(f"  {path}:{lineno}  {raw.strip()[:110]}", file=sys.stderr)

    if status:
        return 1

    print(
        f"de-ai-tone 通過:{len(files)} 個檔案、中文 {total_cjk} 字、"
        f"破折號 {len(emdash_hits)}/{budget} 組"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
