---
name: sdet-economics
description: 成本紀律 reference：省 token、重用 context、模型分級、預算與停止條件、ROI、績效。
---

# SDET Economics（reference，被 bug-hunter / explore / duty-oncall 讀）

成本紀律 reference。**token 是稀缺資源**，燒在低風險探索上等於燒真錢；本文件定規則，不自己跑東西。設計理念見 `docs/economics/sdet-economics.md`。

## 省 token / 重用 context
- 同一 session 內已經看過的畫面/證據不要重新截圖重新讀；`exploration-log.yaml` 記過的路徑不要重走（見 `explore`）。
- 能交給便宜模型做的重複性工作（大量掃描、格式化、分類）不要用強模型；強模型留給需要判斷力的步驟。
- 一次探索的 context 能被下一步直接用（如已讀的 snapshot、已抓的 network log）就不要重新呼叫工具重抓。

## 模型分級（讀 `config/sdet-config.yaml` 的 `models.cheap` / `models.strong`）

| 用途 | 模型 | 為什麼 |
|---|---|---|
| 大量探索、掃描、初篩、格式化 | `models.cheap` | 量大、單次判斷輕，貴模型的邊際價值低 |
| 最終判定（`test-oracle` 判 bug、`bug-verifier` 蓋章、開 issue 前的品質閘） | `models.strong` | 判錯的代價（開假單、漏真 bug）遠高於模型差價 |

沒設定時兩者都退回預設 session 模型；不准為了省錢把判定步驟也降級。

## 預算與停止條件（讀 `config/sdet-config.yaml` 的 `budget`）
- `budget.max_tokens_per_run`：單次執行（一次 hunt / 一次 duty-oncall 值班）的 token 上限。
- `budget.max_actions_per_explore`：`explore` 單次探索的最大步數（呼應 `explore` 自己的 `max_steps` 停止條件，兩者取小）。
- **超過就停手回報，不硬撐。** 停在哪一步、為什麼停、還剩什麼沒探完，要寫進交回的紀錄。這是 `explore` 停止條件的成本版本，不是另一套邏輯。
- 沒有 `sdet-config.yaml` 或欄位缺漏時，用保守預設（寧可提早停、事後被問「怎麼停這麼快」，不要燒穿預算才發現）。

## ROI：一個確認 bug 花多少成本
**token 與成本讀 `output/token-ledger/`（hook 自動記，見 `docs/state-files.md`），不要拿模型自己報的數字。** `rollup.yaml` 有依 skill 與依動作（hunt / verify / rerun / file / fix）的 `cost_usd` 與 token；`<session_id>.yaml` 有逐次呼叫的明細。`findings` / `confirmed` / `duration` 仍從各輪的 `output/sessions/**/runs/*.yaml`（`duty-oncall` 寫）取，算：

```
cost_per_confirmed_bug = Σ tokens(該輪所有 run) ÷ Σ confirmed(該輪所有 run)
```

`confirmed` 只算 `bug-verifier` 蓋章或人複核為真的，候選 findings 不算。分母膨脹會讓 ROI 好看但失真。

## 績效：`output/calibration.yaml` 算得準不準
先讀 `references/confidence.md` 的校準規則，只用識別完整、裁定來源明確的列；按 project 與報告期間篩選，分開計算：
- `precision_high = high 且 human_verdict=confirmed 的筆數 ÷ high 且已有明確人工裁定的筆數`。
- `reproduction_rate_high = high 且 verifier_verdict=confirmed 的筆數 ÷ high 且 verifier_verdict 為 confirmed 或 not-reproduced 的筆數`。
- null／inconclusive 與來源不明的舊資料不算成否定；回報兩個分母與排除筆數，分母為零時指標填 null。verifier confirmed 只證明現象重現，不能代替人工裁定。
- precision 持續偏低 → confidence 因子配分過鬆，或門檻設太低，兩者都會拉低 ROI（花力氣送驗證/開單的東西大半是假警報）。

**沒有 calibration，ROI 只是沒人驗證過的自我感覺。**

## 輸出（格式，非某次執行結果）
```yaml
period: "2026-07-21..2026-07-28"
tokens_total: 1_240_000
runs: 6
confirmed_bugs: 9
cost_per_confirmed_bug: 137_778
precision_high: 0.78          # output/calibration.yaml 算出
human_reviewed_high: 9
reproduction_rate_high: 0.90
verifier_decided_high: 10
excluded: { human: 3, verifier: 2 }
stop_events:
  - run: "20260726-checkout"
    reason: "hit max_tokens_per_run，停在 checkout 第 3 步"
recommendation: "checkout 區域 precision 偏低，檢討 confidence 因子配分"
```

## 上下游
上游資料：`output/sessions/**/runs/*.yaml`（`duty-oncall`）、`output/calibration.yaml`（hunter 寫 predicted；呼叫端／gate 回填 verifier；明確人判另填 human）。與 `economics/route-by-risk` 分工：`route-by-risk` 決定「要不要測」，本文件決定「用什麼成本測、測完值不值得」。
