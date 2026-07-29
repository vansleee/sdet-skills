---
name: flaky-detect
description: 判定一支測試是真的 flaky 還是穩定壞掉：同碼同環境重跑 N 次，量化重現率、歸類疑似根因。某支時紅時綠時使用；`failure-analysis` 判 flaky、`re-run-gate` 裁決 flaky 需要定性時也用。
---

# Flaky Detect（一筆）

輸入一支可疑測試，輸出「是不是 flaky＋重現率＋疑似根因＋下一步」。設計理念見 `docs/maintain/flaky-detect.md`。

> 一筆 vs 一批：這支只定性**一支**測試。跨 run 的 flaky 趨勢、隔離名單與治理交 `flaky-manager`。

## 判準（同一份程式碼、同一個環境，重複執行 N 次）
- 結果**不一致**（有紅有綠）→ **flaky**。
- **N 次全紅** → 不是 flaky，是壞了 → 交 `failure-analysis`。
- **N 次全綠** → `not-reproduced`：記錄後結案，不要一直重跑到它紅為止。

N（`reruns`）與 `flake_rate` 門檻讀 `config/sdet-config.yaml`，**不寫死**。

## 硬性要求：量化重現率
**沒有重現率的 flaky 回報不算數。** 必記「幾次紅／總共幾次」，並保留每次的失敗訊息——不同次紅的原因不同，通常代表有多個問題疊在一起，要拆開報。

## 疑似根因分類

交下游時**一定要帶 `classification` 那欄**——`test-heal` 的「只准這樣改」表是用 `failure-analysis` 的詞彙當 key，只給 `suspected_root_cause` 它查無此列。

| suspected_root_cause | 訊號 | 交下游用的 `classification` | 後續 |
|---|---|---|---|
| `wait-condition` | 等待條件不正確（元素存在但還不可用）| `wait-timing` | `test-heal` |
| `data-pollution` | 測試間資料殘留／互相污染 | `fixture-isolation` | `test-data` |
| `parallel-race` | 平行執行搶同一筆資料或同一個帳號 | `test-data` | `test-data` / `test-parallelize` |
| `external-dependency` | 依賴外部服務、時間、時區、亂數 | `wait-timing` | 隔離或 mock，交 `test-heal` |
| `render-timing` | 動畫、非同步渲染、重繪造成的時序 | `wait-timing` | `test-heal` |

## 鐵則
- **結論要指向根因，不是「加 retry / 加 sleep」**——那兩個是綠色作弊（`references/green-cheating.md`），把 flake_rate 藏起來而非降下來。
- 本 skill 只定性、不動手：修法交 `test-heal`，驗穩交 `re-run-gate`。
- 重跑有上限（config），到了就停。寫下「未達成定性」也比亂猜一個根因好。

## 輸出（格式，非某次執行結果）
```yaml
nodeid: "<file> > <test name>"
runs: <N>
failures: <n>
flake_rate: <n/N>
suspected_root_cause: wait-condition
classification: wait-timing     # test-heal 認得的詞彙,缺這欄它修不了
confidence: medium
next_step: "交 test-heal 改成 web-first assertion"
```

## 上下游
上游：`failure-analysis`（判 flaky）、`re-run-gate`（裁決 flaky 要定性）、`flaky-manager`（名單上要重新定性的）。下游：`test-heal`（依 `classification` 修）、`test-data`（資料污染／搶資源）、`flaky-manager`（納入名單與隔離決策）。
