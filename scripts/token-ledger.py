#!/usr/bin/env python3
"""Token ledger — 把每一次 skill 呼叫消耗的 token 與成本記下來。

由 Claude Code hook 觸發（Stop / SessionEnd），從 stdin 讀 hook JSON，
解析 transcript JSONL，把 usage 歸戶到「當下作用中的 skill」。

歸戶規則：transcript 依檔案順序掃，遇到邊界就切 segment，之後所有 assistant
訊息的 usage 都算在那一段頭上。邊界有兩種，mark 優先：

1. **mark**（權威）—— 編排者自己打的 `--mark --run <slug> --stage <name>`。
   它同時決定 run 歸屬與階段名，所以能正確處理「回到編排者」：sub-skill 跑完
   回來寫記帳與摘要那段，打一個 `--stage wrapup` 就不會被算進最後一個 sub-skill。
2. **Skill 呼叫** —— 沒有 mark 時的退路，段名就是 skill 名。

subagent（sidechain）的訊息夾在同一檔案裡，依順序落進當下 segment —— 這是對的，
subagent 本來就是那一段叫出來的。

輸出（全部重算、可重複執行）：
  output/token-ledger/<session_id>.yaml   單一 session：逐段明細 + 依 run/skill/action 彙總
  output/token-ledger/rollup.yaml         跨 session 累積：依 skill / action 彙總

用法（除了 hook 之外，也可以手動補跑）：
  python3 scripts/token-ledger.py --transcript <path.jsonl> [--session-id <id>]
  python3 scripts/token-ledger.py --rollup-only
  python3 scripts/token-ledger.py --mark --run <slug> --stage <name>   # 編排者在階段交界打點
  python3 scripts/token-ledger.py --report <run-slug>                  # 印一次 run 的逐階段花費與總額
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import OrderedDict
from pathlib import Path

try:
    import yaml
except ImportError:  # 沒有 pyyaml 就退回 JSON，不讓 hook 掛掉
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_DIR = REPO_ROOT / "output" / "token-ledger"

# 每百萬 token 美金定價。改價錢改這裡就好。
# 快取：寫入 5m = 1.25x input、寫入 1h = 2x input、讀取 = 0.1x input。
PRICING = {
    "claude-opus-5": (5.00, 25.00),
    "claude-opus-4-8": (5.00, 25.00),
    "claude-opus-4-7": (5.00, 25.00),
    "claude-opus-4-6": (5.00, 25.00),
    "claude-fable-5": (10.00, 50.00),
    "claude-sonnet-5": (3.00, 15.00),
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
}
DEFAULT_PRICE = (5.00, 25.00)

CACHE_WRITE_5M = 1.25
CACHE_WRITE_1H = 2.00
CACHE_READ = 0.10

# skill → 動作。要看「獵/驗/重跑/開/修」各花多少，就是靠這張表。
ACTION_OF_SKILL = {
    "bug-hunter": "hunt",
    "explore": "hunt",
    "exploration-charter": "hunt",
    "bug-verifier": "verify",
    "test-oracle": "verify",
    "issue-quality-gate": "verify",
    "classify-anomaly": "verify",
    "quality-gate": "verify",
    "re-run-gate": "rerun",
    "flaky-detect": "rerun",
    "triage": "file",
    "bug-fixer": "fix",
    "test-heal": "fix",
    "test-author": "author",
    "api-test-author": "author",
    "test-data": "author",
    "failure-analysis": "analyze",
    "pipeline-read": "analyze",
    "pipeline-triage": "analyze",
    "pipeline-observability": "analyze",
    "evidence-package": "evidence",
    "api-evidence": "evidence",
    "structured-result": "evidence",
    "ci-pipeline": "infra",
    "test-env": "infra",
    "test-parallelize": "infra",
    "flaky-manager": "infra",
    "test-planning": "plan",
    "route-by-risk": "plan",
    "traceability": "plan",
    "release-signoff": "plan",
    "status-report": "plan",
    "test-prune": "plan",
    "duty-oncall": "meta",
    "setup-sdet": "meta",
    "sdet-economics": "meta",
    "ask-sdet": "meta",
}

NO_SKILL = "_no_skill"


def new_bucket() -> dict:
    return {
        "calls": 0,
        "input": 0,
        "output": 0,
        "cache_write_5m": 0,
        "cache_write_1h": 0,
        "cache_read": 0,
        "cost_usd": 0.0,
    }


def add(dst: dict, src: dict) -> None:
    for k in ("input", "output", "cache_write_5m", "cache_write_1h", "cache_read"):
        dst[k] += src[k]
    dst["cost_usd"] = round(dst["cost_usd"] + src["cost_usd"], 6)


def cost_of(usage: dict, model: str) -> float:
    price_in, price_out = PRICING.get(model, DEFAULT_PRICE)
    per_token_in = price_in / 1_000_000
    return round(
        usage["input"] * per_token_in
        + usage["output"] * price_out / 1_000_000
        + usage["cache_write_5m"] * per_token_in * CACHE_WRITE_5M
        + usage["cache_write_1h"] * per_token_in * CACHE_WRITE_1H
        + usage["cache_read"] * per_token_in * CACHE_READ,
        6,
    )


def read_usage(u: dict) -> dict:
    """把一次 API 呼叫的 usage 攤平成我們要的欄位。"""
    creation = u.get("cache_creation") or {}
    w5 = creation.get("ephemeral_5m_input_tokens")
    w1 = creation.get("ephemeral_1h_input_tokens")
    if w5 is None and w1 is None:
        # 舊格式只有 cache_creation_input_tokens，當成 5m
        w5, w1 = u.get("cache_creation_input_tokens", 0) or 0, 0
    return {
        "input": u.get("input_tokens", 0) or 0,
        "output": u.get("output_tokens", 0) or 0,
        "cache_write_5m": w5 or 0,
        "cache_write_1h": w1 or 0,
        "cache_read": u.get("cache_read_input_tokens", 0) or 0,
    }


MARK_RE = re.compile(r"token-ledger\.py\s+.*?--mark\b")
MARK_RUN_RE = re.compile(r"--run[= ]+([^\s'\"]+)")
MARK_STAGE_RE = re.compile(r"--stage[= ]+([^\s'\"]+)")

UNASSIGNED_RUN = "_unassigned"


def parse_mark(command: str):
    """從 Bash 指令字串認出 mark，回傳 (run, stage)；不是 mark 就回 None。"""
    if not isinstance(command, str) or not MARK_RE.search(command):
        return None
    run = MARK_RUN_RE.search(command)
    stage = MARK_STAGE_RE.search(command)
    return (run.group(1) if run else None, stage.group(1) if stage else "unnamed")


def parse_transcript(path: Path) -> dict:
    """掃一份 transcript，回傳逐段明細與彙總。"""
    calls: list[dict] = []
    current = None  # 當下作用中的 segment
    current_run = UNASSIGNED_RUN

    def open_call(skill: str, args, ts, stage=None, run=None) -> dict:
        entry = {
            "run": run or current_run,
            "stage": stage or skill.split(":")[-1],  # 段名去掉 plugin 前綴，報表才排得整齊
            "skill": skill,
            "action": ACTION_OF_SKILL.get(skill.split(":")[-1], "other"),
            "args": (args or "")[:120] if isinstance(args, str) else "",
            "started_at": ts,
            "ended_at": ts,
            "models": OrderedDict(),
            "api_calls": 0,
            "input": 0,
            "output": 0,
            "cache_write_5m": 0,
            "cache_write_1h": 0,
            "cache_read": 0,
            "cost_usd": 0.0,
        }
        calls.append(entry)
        return entry

    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg = obj.get("message")
            if not isinstance(msg, dict):
                continue
            ts = obj.get("timestamp")

            # 1. 先記 usage（這則訊息屬於「切換前」的 segment）
            usage = msg.get("usage")
            if isinstance(usage, dict) and usage.get("output_tokens") is not None:
                if current is None:
                    current = open_call(NO_SKILL, "", ts)
                model = msg.get("model") or "unknown"
                u = read_usage(usage)
                c = cost_of(u, model)
                for k, v in u.items():
                    current[k] += v
                current["cost_usd"] = round(current["cost_usd"] + c, 6)
                current["api_calls"] += 1
                current["models"][model] = current["models"].get(model, 0) + 1
                if ts:
                    current["ended_at"] = ts

            # 2. 再看有沒有邊界（mark 優先於 Skill 呼叫），有的話開新 segment
            content = msg.get("content")
            if isinstance(content, list):
                for block in content:
                    if not (isinstance(block, dict) and block.get("type") == "tool_use"):
                        continue
                    inp = block.get("input") or {}
                    name = block.get("name")

                    if name == "Bash":
                        mark = parse_mark(inp.get("command"))
                        if mark:
                            run, stage = mark
                            if run:
                                current_run = run
                            # mark 的 skill 沿用前一段的，讓 by_skill 仍看得出是誰在跑
                            prev_skill = current["skill"] if current else NO_SKILL
                            current = open_call(prev_skill, "", ts, stage=stage)
                    elif name == "Skill":
                        current = open_call(
                            inp.get("skill") or "unknown", inp.get("args"), ts
                        )

    by_skill: dict[str, dict] = {}
    by_action: dict[str, dict] = {}
    by_run: dict[str, dict] = {}
    total = new_bucket()
    for entry in calls:
        if entry["api_calls"] == 0:
            continue
        entry["models"] = dict(entry["models"])
        for bucket_map, key in ((by_skill, entry["skill"]), (by_action, entry["action"])):
            bucket = bucket_map.setdefault(key, new_bucket())
            bucket["calls"] += 1
            add(bucket, entry)

        run = by_run.setdefault(
            entry["run"],
            {"started_at": entry["started_at"], "ended_at": entry["ended_at"],
             "stages": OrderedDict(), "total": new_bucket()},
        )
        run["ended_at"] = entry["ended_at"]
        stage = run["stages"].setdefault(entry["stage"], new_bucket())
        stage["calls"] += 1
        add(stage, entry)
        run["total"]["calls"] += 1
        add(run["total"], entry)

        total["calls"] += 1
        add(total, entry)

    for run in by_run.values():
        run["stages"] = dict(run["stages"])

    return {
        "calls": [e for e in calls if e["api_calls"] > 0],
        "by_run": by_run,
        "by_skill": by_skill,
        "by_action": by_action,
        "total": total,
    }


def dump(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if yaml is not None:
        text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    else:
        text = json.dumps(data, ensure_ascii=False, indent=2)
    path.write_text(text, encoding="utf-8")


def rebuild_rollup() -> None:
    by_skill: dict[str, dict] = {}
    by_action: dict[str, dict] = {}
    total = new_bucket()
    sessions = 0
    for f in sorted(LEDGER_DIR.glob("*.yaml")):
        if f.name == "rollup.yaml":
            continue
        try:
            raw = f.read_text(encoding="utf-8")
            data = yaml.safe_load(raw) if yaml is not None else json.loads(raw)
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        sessions += 1
        for src_key, dst in (("by_skill", by_skill), ("by_action", by_action)):
            for name, bucket in (data.get(src_key) or {}).items():
                acc = dst.setdefault(name, new_bucket())
                acc["calls"] += bucket.get("calls", 0)
                add(acc, {**new_bucket(), **bucket})
        t = data.get("total") or {}
        total["calls"] += t.get("calls", 0)
        add(total, {**new_bucket(), **t})

    dump(
        LEDGER_DIR / "rollup.yaml",
        {
            "sessions": sessions,
            "total": total,
            "by_action": dict(sorted(by_action.items(), key=lambda kv: -kv[1]["cost_usd"])),
            "by_skill": dict(sorted(by_skill.items(), key=lambda kv: -kv[1]["cost_usd"])),
        },
    )


def report_run(slug: str) -> int:
    """印出某一次 run 的逐階段花費與總額。跨 session 也找得到。"""
    found = []
    for f in sorted(LEDGER_DIR.glob("*.yaml")):
        if f.name == "rollup.yaml":
            continue
        try:
            raw = f.read_text(encoding="utf-8")
            data = yaml.safe_load(raw) if yaml is not None else json.loads(raw)
        except Exception:
            continue
        if isinstance(data, dict) and slug in (data.get("by_run") or {}):
            found.append((data.get("session_id", f.stem), data["by_run"][slug]))

    if not found:
        print(f"找不到 run: {slug}")
        print(f"（有記到的 run 見 {LEDGER_DIR}/*.yaml 的 by_run）")
        return 1

    stages: dict[str, dict] = OrderedDict()
    total = new_bucket()
    for _, run in found:
        for name, bucket in run["stages"].items():
            acc = stages.setdefault(name, new_bucket())
            acc["calls"] += bucket.get("calls", 0)
            add(acc, {**new_bucket(), **bucket})
        t = run["total"]
        total["calls"] += t.get("calls", 0)
        add(total, {**new_bucket(), **t})

    print(f"run: {slug}   （session: {', '.join(s for s, _ in found)}）")
    print(f"{'stage':<20}{'segs':>5}{'in':>10}{'out':>10}{'cache_w':>12}{'cache_r':>12}{'USD':>10}")
    for name, b in stages.items():
        print(f"{name:<20}{b['calls']:>5}{b['input']:>10,}{b['output']:>10,}"
              f"{b['cache_write_5m'] + b['cache_write_1h']:>12,}{b['cache_read']:>12,}"
              f"{b['cost_usd']:>10.2f}")
    print(f"{'TOTAL':<20}{total['calls']:>5}{total['input']:>10,}{total['output']:>10,}"
          f"{total['cache_write_5m'] + total['cache_write_1h']:>12,}{total['cache_read']:>12,}"
          f"{total['cost_usd']:>10.2f}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript")
    ap.add_argument("--session-id")
    ap.add_argument("--rollup-only", action="store_true")
    ap.add_argument("--mark", action="store_true", help="在階段交界打點（供編排者呼叫）")
    ap.add_argument("--run", help="run 代號，通常用 <date>_<slug>")
    ap.add_argument("--stage", help="階段名，例如 hunt / verify / gate / dispatch / wrapup")
    ap.add_argument("--report", metavar="RUN", help="印出某次 run 的逐階段花費與總額")
    args = ap.parse_args()

    if args.mark:
        # 這支不做事，它存在的意義就是在 transcript 留一個權威邊界。
        print(f"[token-ledger] mark run={args.run or '-'} stage={args.stage or 'unnamed'}")
        return 0

    if args.report:
        return report_run(args.report)

    if args.rollup_only:
        rebuild_rollup()
        return 0

    transcript = args.transcript
    session_id = args.session_id
    if not transcript:
        try:
            payload = json.load(sys.stdin)
        except Exception:
            return 0  # 不是 hook 呼叫也不要吵
        transcript = payload.get("transcript_path")
        session_id = payload.get("session_id")
        cwd = payload.get("cwd") or ""
        # 只記這個 repo 的工作
        if cwd and not str(Path(cwd).resolve()).startswith(str(REPO_ROOT)):
            return 0

    if not transcript:
        return 0
    tpath = Path(os.path.expanduser(transcript))
    if not tpath.is_file():
        return 0

    result = parse_transcript(tpath)
    if not result["calls"]:
        return 0

    session_id = session_id or tpath.stem
    result = {
        "session_id": session_id,
        "transcript": str(tpath),
        **result,
    }
    dump(LEDGER_DIR / f"{session_id}.yaml", result)
    rebuild_rollup()
    return 0


if __name__ == "__main__":
    sys.exit(main())
