---
name: status-report
description: 把近期活動彙整成 standup / 測試報告 / release-readiness 摘要。只引用既有狀態檔，不重算。要回報進度、給團隊看時使用；`release-signoff` 要素材時也用。
---

# Status Report

輸入一段期間，輸出**對人的摘要**：測了什麼、發現什麼、卡在哪、風險在哪。設計理念見 `docs/workflow/status-report.md`。

> **只彙整，不重算。** 每個數字都引用既有狀態檔並附出處。這裡重算一次 flaky rate，團隊就有兩個版本的真相。

## 輸入 / 輸出
- **輸入**：期間（預設「上次報告以來」；查不到就用近 7 天）＋ 對象（`standup` / `test-report` / `release-readiness`）＋ 資料來源（下表）。
- **輸出**：對應格式的摘要，存 `output/reports/status-<date>.md`。

## 資料來源

| 要講的事 | 引用哪裡 | 誰維護 |
|---|---|---|
| 執行了什麼、花多少 | `output/sessions/**/runs/*.yaml` | `duty-oncall` |
| 修完重跑了幾次 | `output/sessions/**/runs/reruns-*.yaml` | `re-run-gate` |
| 發現了什麼 | `output/sessions/**/findings/F-*.yaml`、`output/sessions/**/verdicts/V-*.yaml` | `explore` / `bug-verifier` |
| 開了哪些單 | `output/issues-index.yaml`、`gh issue list` | `triage` |
| CI 健康度 | `output/reports/health-<date>.md` | `pipeline-observability` |
| 放行狀態 | `output/pipeline-gate.yaml` | `quality-gate` |
| 覆蓋與 gap | `output/traceability.yaml` | `traceability` |
| 一片紅的處理 | `output/triage-reports/` | `pipeline-triage` |
| 隔離中的測試 | `output/flaky-registry.yaml` | `flaky-manager` |

## 步驟
1. **定期間**：找上一份 `output/reports/status-*.md` 的日期當起點；沒有就近 7 天。
2. **收資料**：只讀上表來源。來源不存在 → 該段寫「無資料（未跑 `<skill>`）」，**不現場發明數字**。
3. **分四類**：進度（做了什麼）／發現（找到什麼）／阻塞（卡在誰身上）／風險（可能出事的）。
4. **挑格式**（見下）。
5. **附出處**：每個結論後面掛狀態檔路徑或 URL。
6. **存檔**：寫 `output/reports/status-<date>.md`。
7. **要發到外部才確認**：貼 Slack / 留言到 issue 屬副作用，**先問過再送**。

## 三種格式

| 對象 | 長度 | 內容重點 |
|---|---|---|
| `standup` | 3–5 行 | 做了 / 發現 / 卡住。**只講需要別人知道的**，不列數字表 |
| `test-report` | 一頁 | 範圍、結果分佈（照 `structured-result` 六態）、重點 finding（附證據連結）、風險、隔離中的覆蓋 |
| `release-readiness` | 半頁 | 給 `release-signoff` 當素材：覆蓋現況、未解 blocker、gate 狀態、已知風險。**只陳述，不下 go/no-go** |

## 鐵則
- **缺資料就寫「無資料」。** 用 0 或估計值填補，會讓「沒量」長得像「沒問題」。
- **每個結論附出處。** 沿用 `structured-result` 的證據習慣。沒有出處的結論在追問時站不住。
- **`release-readiness` 只陳述現況。** 它是 `release-signoff` 的輸入，go/no-go 由那支裁決。
- **隔離中的測試一定要提。** 「這期有 3 支測試是關掉的」屬於讀者必須知道的事，不能因為它不好看就省略。

## 輸出（格式，非某次執行結果）
```markdown
## Standup — 2026-07-29
- 跑了 checkout 折扣碼探索（charter: checkout-coupon），14 個檢查點，2 fail 1 blocked。
- 找到 1 個確認 bug：過期折扣碼仍可套用 → 已開 #488（`output/issues-index.yaml`）。
- 卡住：折扣碼與點數能否併用，PRD 未定義，等 PM 回覆（`output/plans/checkout-coupon.md#open_questions`）。
- 風險：CI flaky rate 0.12 → 0.31，隔離中 9 支（2 支逾期）→ `output/reports/health-2026-07-29.md`。
```

```yaml
# release-readiness 的骨架（只陳述，不裁決）
coverage:   { source: output/traceability.yaml, covered: 41, gap: 3, uncertain: 2 }
blockers:   { source: "gh issue list --label blocker", open: 1, ids: ["#471"] }
gate:       { source: output/pipeline-gate.yaml, latest: FAIL, blocked_on: "blocker #471" }
quarantine: { source: output/flaky-registry.yaml, count: 9, expired: 2 }
known_risks:
  - "REQ-CHECKOUT-006（折扣碼 × 點數）無任何覆蓋,risk_score 0.71"
note: "本節僅陳述現況;go/no-go 由 release-signoff 裁決。"
```

## 上下游
上游：所有會寫狀態檔的 skill（見上表）。下游：`release-signoff`（吃 `release-readiness` 當素材）、人（standup / 測試報告）。
