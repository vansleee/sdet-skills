---
name: flaky-manager
description: 跨 run 的 flaky 治理：維護 flaky 名單、決定隔離（quarantine）與解除、追蹤到期未修者並升級。要看 flaky 健康度、要隔離某支測試時使用；`pipeline-triage` 分流出 flaky 群、`pipeline-observability` 的 flaky_rate 超標時路由到它。
---

# Flaky Manager（一批）

輸入跨 run 的失敗歷史，輸出 flaky 名單 + 隔離決策 + 到期升級。設計理念見 `docs/infra/flaky-manager.md`。

> 一筆 vs 一批：`flaky-detect` 對**一支**測試重跑 N 次定性；本 skill 管**一批**的名單、政策與退場。
> 狀態檔：`flaky-registry.yaml`（範本 `state-templates/flaky-registry.example.yaml`，見 `docs/state-files.md`）。

## 輸入 / 輸出
- **輸入**：`pipeline-triage` 判為 flaky 的群、`flaky-detect` 的定性結果、跨 run 歷史（`pipeline-read` 拉近 N 個 run，N 讀 `config/sdet-config.yaml` 的 `flaky.lookback_runs`，預設 20）、現有 `flaky-registry.yaml`。
- **輸出**：更新後的 registry ＋ 本次的 quarantine / de-quarantine / escalate 決策清單 ＋ 給 `pipeline-observability` 的 flaky rate。

## 步驟
1. **收歷史**：對近 `lookback_runs` 個 run 取每支測試的紅綠序列（同 sha 上有紅有綠 = flaky 訊號）。
2. **算 flake_rate**：`失敗次數 / 執行次數`，逐支算。沒有數字的 flaky 回報不算數。
3. **比對 registry**：已在名單的更新 `last_seen`、`flake_rate`；新出現的加入。
4. **套政策**（下表），產決策。
5. **檢到期**：quarantine 超過 `flaky.max_quarantine_days`（預設 14）仍未修 → **escalate**：交 `test-heal` 修，或 `test-prune` 評估刪除，並回報給人。
6. **確認再寫**：quarantine / de-quarantine 會改測試標記，屬副作用——**先把清單列給使用者確認**，得同意才動，並受 `config/governance.yaml` 管制。
7. **輸出**：更新 registry、回報決策表、把 flaky rate 交 `pipeline-observability`、把名單交 `quality-gate`。

## 政策

| 狀態轉換 | 條件 | 動作 |
|---|---|---|
| → `quarantined` | `flake_rate` ≥ `flaky.quarantine_threshold`（預設 0.2）且連續出現 ≥ 2 個 run | 標記隔離、開/更新追蹤 issue、指派 owner |
| → `watch` | 0 < `flake_rate` < 門檻 | 留在名單觀察，不隔離 |
| → `active`（解除隔離）| 修完後交 `re-run-gate` **連續綠 N 次**（讀 `config` 的 `rerun.required_green`）| 解除標記、registry 標 `resolved` |
| → `escalated` | 隔離超過 `max_quarantine_days` 未修 | 轉 `test-heal`（修）或 `test-prune`（評估刪）+ 回報人 |

隔離的**實作方式**讀 `config/sdet-config.yaml` 的 `flaky.quarantine_mechanism`（如 Playwright 的 `test.fixme` / `@flaky` tag + grep 排除），**不寫死在本 skill**——不同專案的測試框架與 CI 設定不同。

## 鐵則
- **quarantine 一定要有到期日。** 沒有退場機制的隔離＝安靜地刪掉覆蓋率：測試還在 repo 裡、看起來有測，實際永遠不跑。到期就必須 escalate，不准無限展延。
- **隔離不是修好。** registry 裡 `quarantined` 是「欠債中」，不是結案；只有 `resolved` 才算完。
- **不自己修測試、不自己判單筆根因。** 定性交 `flaky-detect`、修交 `test-heal`、驗穩交 `re-run-gate`。
- **禁止用「加 retry」當治理手段**——那是把 flake_rate 藏起來，不是降下來。
- 隔離中的測試紅了**不擋 `quality-gate`**（否則隔離沒意義），但**必須在放行報告裡列出來**，讓人知道這版有多少覆蓋是關掉的。

## 輸出（格式，非某次執行結果）
```yaml
# flaky-registry.yaml（節錄）
- nodeid: "checkout.spec.ts > applies coupon"
  status: quarantined          # watch | quarantined | escalated | resolved
  flake_rate: 0.35             # 近 20 run:7/20
  first_seen: 2026-07-10
  last_seen: 2026-07-28
  suspected_root_cause: wait-condition   # 沿用 flaky-detect 的分類
  quarantined_at: 2026-07-18
  expires_at: 2026-08-01       # quarantined_at + max_quarantine_days
  owner: "<github handle>"
  issue: "<issue url>"
decisions:
  - nodeid: "cart.spec.ts > removes item"
    action: quarantine
    reason: "flake_rate 0.25 ≥ 0.2,連續 3 run 出現"
  - nodeid: "login.spec.ts > sso"
    action: escalate
    reason: "隔離 21 天 > max_quarantine_days 14,仍未修 → 轉 test-heal"
summary: { total_flaky: 9, quarantined: 3, escalated: 1, flake_rate_overall: 0.04 }
```

## 上下游
上游：`pipeline-triage`（分流 flaky 群）、`flaky-detect`（單支定性）、`pipeline-read`（跨 run 歷史）。下游：`test-heal` / `test-prune`（escalate 去向）、`re-run-gate`（解除隔離的驗證）、`quality-gate`（讀名單）、`pipeline-observability`（flaky rate 指標）。
