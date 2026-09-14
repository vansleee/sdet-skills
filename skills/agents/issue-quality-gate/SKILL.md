---
name: issue-quality-gate
description: 開單前檢查六條必要條件，依專案與 UI／API 證據分流 pass / hold / block。使用者問能否開單，或候選要轉 Issue 時使用；重複項擋下並連結舊單。
---

# Issue Quality Gate

輸入一批候選（含 verdict、confidence、evidence），輸出 `output/sessions/<date>_<slug>/gate.yaml`。設計理念見 `docs/agents/issue-quality-gate.md`。

> **好習慣會被跳過，硬閘門不會。** 前面立的規矩——證據、oracle、信心、誤報、去重、獨立重現——在這裡從「最好有」變成「沒有就開不了」。這是 **AND**：全過才放行。

## 前置
- 先讀 `references/agent-handoff.md` 與 `references/config-resolution.md`；候選與 verdict 的 `(project, session, finding_id)` 必須一致，project 須符合 charter。沒有 verdict 時，由呼叫端依盲驗契約送 `bug-verifier`，不得傳完整候選與評分；無法送驗就記 `reproducible: fail`、`result: block` 與待驗原因。
- `output/known-false-positives.yaml`、`output/issues-index.yaml` 與解析後的 `sdet-config.yaml`（`confidence.min_to_file`）可讀。跨輪登錄簿只比對同 project，舊資料歸屬不明先人工核對。

## 六條檢查（順序固定，逐條記 pass/fail）
| # | 條件 | 判準 | 來源 |
|---|---|---|---|
| 1 | reproducible | 同筆 finding 的獨立 verifier `verdict == confirmed` | `bug-verifier` |
| 2 | has_evidence | hunter 與 verifier 各自通過 UI／API 證據表，檔案齊全且可攜 | `references/agent-handoff.md` |
| 3 | oracle_passed | `verdict == bug`（非 needs-spec / inconclusive） | `test-oracle` |
| 4 | confidence_ok | 數值 `score >= confidence.min_to_file`，因子完整且未違反封頂 | `references/confidence.md` |
| 5 | not_false_pos | 未命中 `output/known-false-positives.yaml` | known-FP |
| 6 | not_duplicate | 同 project 的指紋不在 index；已併入舊單仍為 fail | `references/bug-fingerprint.md` |

## 分流
- **pass** — 六條全過 → 交 `triage` 開單；範圍清楚、可修的可再交 `bug-fixer`。
- **hold** — 沒有 block 條件，但差 confidence 或「算不算 bug」存疑，寫明 `blocked_on`。
- **block** — needs-spec、無法重現、證據不全、命中 FP 或重複。重複項填 `existing_issue` 與 `blocked_on`，不交新單流程；舊單補證由 triage 依授權處理。

## 輸出
```yaml
# output/sessions/<date>_<slug>/gate.yaml
- project: null
  session: <date>_<slug>
  finding_id: F-001
  level: ui
  evidence_levels: [ui]
  candidate: "<fingerprint>"
  checks: { reproducible: pass, has_evidence: pass, oracle_passed: pass,
            confidence_ok: pass, not_false_pos: pass, not_duplicate: pass }
  result: pass | hold | block
  blocked_on: "<卡在哪、下一步>"   # hold / block 必填
  existing_issue: null           # 重複時填完整連結或本地路徑
```
同時回報一行摘要：**幾個放行、幾個待人判、幾個擋下。**

## 鐵則
- **AND，不是加權平均。** 五條滿分救不了一條 fail。
- 不放行 ≠ 丟掉：每筆 hold / block 都要寫 `blocked_on`，讓「要人來判」變成看得到的佇列，不是默默消失。
- 閘門本身**不開單、不修、不改候選內容**；它只做決定、留紀錄。
- override 走 `config/governance.yaml` 並留誰／何時／理由；不得藉此把重複項改成新單 pass，也不能取代缺少的獨立驗證與證據。補齊或修正判定後重跑六條檢查，副作用仍另查權限。
- 依 `references/confidence.md` 用完整識別回填驗證結果、`gate_result` 與 gate 路徑；人工結果只在收到實際人判時記入，不把 block 當成 `not-a-bug`。缺 calibration 對應列或識別不唯一就回報，不猜測回填。

## 驗收（跑完自己對一次）
- 每個候選**六條都跑完**、逐條有 pass/fail 嗎？
- 被擋的都寫了 `blocked_on` 嗎？
- 有沒有任何候選繞過閘門直接開單？（一個都不該有）
