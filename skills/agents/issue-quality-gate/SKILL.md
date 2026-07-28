---
name: issue-quality-gate
description: 開單前的硬閘門：六條 AND 全過才放行，輸出 gate.yaml 分流 pass / hold / block。使用者問「這能不能開單」時使用；任何 skill 要把候選變成 issue 或 PR 前，都得先過它。
---

# Issue Quality Gate

輸入一批候選（含 verdict、confidence、evidence），輸出 `gate.yaml`。設計理念見 `docs/agents/issue-quality-gate.md`。

> **好習慣會被跳過，硬閘門不會。** 前面立的規矩——證據、oracle、信心、誤報、去重、獨立重現——在這裡從「最好有」變成「沒有就開不了」。這是一個 **AND**：全過才放行。

## 前置
- 候選已過 `bug-verifier`（有 `verdicts/V-<slug>.yaml`）；沒驗過的不進閘門，先送驗。
- `known-false-positives.yaml`、`issues-index.yaml`、`config/sdet-config.yaml`（`confidence.min_to_file`）可讀。

## 六條檢查（順序固定，逐條記 pass/fail）
| # | 條件 | 判準 | 來源 |
|---|---|---|---|
| 1 | reproducible | verifier `verdict == confirmed` | `bug-verifier` |
| 2 | has_evidence | manifest + 重現步驟 + 佐證檔齊全、可攜 | evidence-package |
| 3 | oracle_passed | `verdict == bug`（非 needs-spec / inconclusive） | `test-oracle` |
| 4 | confidence_ok | `confidence >= confidence.min_to_file` | `references/confidence.md` |
| 5 | not_false_pos | 未命中 `known-false-positives.yaml` | known-FP |
| 6 | not_duplicate | 指紋不在 `issues-index.yaml`（或已併入舊單） | `references/bug-fingerprint.md` |

## 分流
- **pass** — 六條全過 → 交 `triage` 開單；範圍清楚、可修的可再交 `bug-fixer`。
- **hold** — 差 confidence 或「算不算 bug」存疑 → 進人工複核佇列，寫明 `blocked_on`。
- **block** — needs-spec、無法重現、命中 FP → 擋下，寫明**卡在哪一條、下一步找誰**。

## 輸出
```yaml
# gate.yaml
- candidate: "<fingerprint>"
  checks: { reproducible: pass, has_evidence: pass, oracle_passed: pass,
            confidence_ok: pass, not_false_pos: pass, not_duplicate: pass }
  result: pass | hold | block
  blocked_on: "<卡在哪、下一步>"   # hold / block 必填
```
同時回報一行摘要：**幾個放行、幾個待人判、幾個擋下。**

## 鐵則
- **AND，不是加權平均。** 五條滿分救不了一條 fail。
- 不放行 ≠ 丟掉：每筆 hold / block 都要寫 `blocked_on`，讓「要人來判」變成看得到的佇列，不是默默消失。
- 閘門本身**不開單、不修、不改候選內容**；它只做決定、留紀錄。
- override 走 `config/governance.yaml`：`require_reason: true`，硬推要留痕（誰／何時／理由）。
- 擋下的紀錄與後續人判回填 `calibration.yaml`——閘門越透明，越知道該調鬆或調緊。

## 驗收（跑完自己對一次）
- 每個候選**六條都跑完**、逐條有 pass/fail 嗎？
- 被擋的都寫了 `blocked_on` 嗎？
- 有沒有任何候選繞過閘門直接開單？（一個都不該有）
