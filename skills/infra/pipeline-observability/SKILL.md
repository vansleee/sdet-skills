---
name: pipeline-observability
description: 算測試健康指標（MTTR、flaky rate、首次通過率、派工延遲、suite duration），比對趨勢，把超標的路由到該處理它的 skill。要看測試健康度、判斷 CI 是不是在變差、做週期性回顧時使用。
---

# Pipeline Observability

輸入一段期間的 run 歷史，輸出指標 + 趨勢 + **行動建議**。infra 迴圈的收尾與回饋。設計理念見 `docs/infra/pipeline-observability.md`。

> **指標要導向行動，不是儀表板自嗨。** 每個超標指標都必須指名「接下來交給哪支 skill」，否則這份報告只是好看的數字。

## 輸入 / 輸出
- **輸入**：期間（預設近 30 天，讀 `config/sdet-config.yaml` 的 `observability.window_days`）＋ `pipeline-read` 的 run 歷史 ＋ `runs/<date>.yaml`（值班計量）＋ `runs/reruns-<date>.yaml`（重跑紀錄）＋ `flaky-registry.yaml` ＋ `pipeline-gate.yaml` ＋ `triage-reports/` ＋ `issues-index.yaml`。
- **輸出**：指標報告（本期值、上期值、趨勢、是否超標、行動建議），存 `reports/health-<date>.md`。

## 指標（算式與資料來源見 `references/test-health-metrics.md`）

| 指標 | 一句話定義 | 主要來源 | 超標時路由到 |
|---|---|---|---|
| `mttr` | 主線由紅轉綠的中位時間 | run 歷史（同 branch 連續 run 的 conclusion）| `pipeline-triage`（派工太慢）/ `test-heal` |
| `flaky_rate` | flaky 失敗數 ÷ 總失敗數 | `flaky-registry.yaml` | `flaky-manager` |
| `first_pass_rate` | 不靠 retry 就綠的 run 比例 | run 歷史 + retry 記錄 | `pipeline-triage`（驟降＝有新問題進來）|
| `suite_duration_p50/p95` | 套件耗時 | run 歷史 | `test-parallelize` |
| `assignment_latency` | 紅燈到 issue 被 assign 的中位時間 | `triage-reports/` + `issues-index.yaml` | `pipeline-triage` / 人（人力問題）|
| `quarantine_count` | 隔離中的測試數（含逾期幾支）| `flaky-registry.yaml` | `flaky-manager`（逾期）/ `test-prune` |
| `gate_pass_rate` / `override_count` | 放行通過率、硬推次數 | `pipeline-gate.yaml` | 人（override 變多＝閘門與現實脫節）|

閾值全部讀 `config/sdet-config.yaml` 的 `observability.thresholds`，**不寫死**。

## 步驟
1. **定期間**：本期 vs 上一期（同長度）。
2. **收資料**：從上表來源讀；**不重跑任何測試、不重算下游已算過的值**（flaky rate 直接引 registry，不自己重算重現率）。
3. **算指標**：照 `references/test-health-metrics.md`。資料不足以算的，標 `no-data` 並寫缺什麼——**不用 0 或猜測值填補**。
4. **比趨勢**：與上期比，標 `improving` / `stable` / `degrading`。
5. **對閾值**：超標的標 `alert`。
6. **產行動**：每個 `alert` 依上表指名下一步 skill + 一句理由。沒有 alert 就明說「本期無需行動」。
7. **存檔**：寫 `reports/health-<date>.md`。

## 鐵則
- **每個 alert 必須綁一個行動。** 只報數字不指路，等於把判斷成本丟回給人。
- **不重算、只引用。** 數字的單一真相在各自的狀態檔；這裡重算一次，就會出現兩個版本的 flaky rate。
- **`no-data` 不是 0。** 沒量到不等於健康——這和 `route-by-risk`「資料源缺不等於低風險」是同一條紀律。
- **趨勢比絕對值重要。** flaky rate 5% 不一定有問題，但從 1% 變 5% 一定有事。報告一律附上期對照。
- **純讀無副作用——它是儀表，不是方向盤。** 指出該去哪，方向盤交給被路由到的那支。

## 輸出（格式，非某次執行結果）
```yaml
window: { from: 2026-06-29, to: 2026-07-29, runs: 214 }
metrics:
  mttr:               { value: "4h20m", prev: "2h05m", trend: degrading, threshold: "4h",  alert: true }
  flaky_rate:         { value: 0.31,    prev: 0.12,    trend: degrading, threshold: 0.15,  alert: true }
  first_pass_rate:    { value: 0.86,    prev: 0.88,    trend: stable,    threshold: 0.80,  alert: false }
  suite_duration_p95: { value: "38m",   prev: "31m",   trend: degrading, threshold: "20m", alert: true }
  assignment_latency: { value: "1h10m", prev: "1h30m", trend: improving, threshold: "4h",  alert: false }
  quarantine_count:   { value: 9, expired: 2, prev: 5,  trend: degrading, threshold: 5,    alert: true }
  gate_pass_rate:     { value: 0.71, override_count: 4, prev: 0.83, trend: degrading, alert: true }
  coverage_gap:       { value: no-data, reason: "traceability.yaml 不存在,本期未跑 traceability" }
actions:
  - metric: flaky_rate
    route: flaky-manager
    why: "0.12 → 0.31,且隔離中 9 支有 2 支逾期未處置"
  - metric: suite_duration_p95
    route: test-parallelize
    why: "p95 38m 超過目標 20m,先驗獨立性再加 shard"
  - metric: gate_pass_rate
    route: 人
    why: "override 4 次(上期 1 次),閘門準則可能與現實脫節,需人檢視 config/sdet-config.yaml 的 gate"
```

## 上下游
上游：`pipeline-read`（run 歷史）、`flaky-manager` / `quality-gate` / `pipeline-triage`（各自的狀態檔）。下游：依 alert 路由回 `flaky-manager` / `test-parallelize` / `pipeline-triage` / `test-prune`——**這就是 infra 迴圈的回饋邊**；`status-report` 直接引用本報告的數字，不自己重算。
