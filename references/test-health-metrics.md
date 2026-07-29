# 測試健康指標：算式與資料來源

`pipeline-observability` 讀本檔計算指標。**演算法放這裡，資料放狀態檔**——對齊 `docs/state-files.md` 的慣例。
閾值不在這裡，在 `config/sdet-config.yaml` 的 `observability.thresholds`（專案可調）。

## 通則
- **能引用就不重算。** 下游狀態檔已有的值（flaky rate、gate 裁決）直接引用；重算會產生第二個版本的真相。
- **資料不足標 `no-data`，不用 0 補。** 沒量到 ≠ 健康。
- **一律附上期對照。** 趨勢比絕對值有意義。
- **中位數優於平均。** 時間類指標（MTTR、latency）用中位數，避免一次 3 天的離群值把整期拉爛。

---

## mttr — 平均修復時間
**定義**：主線（預設 `main`）由紅轉綠所需時間的**中位數**。

```
對 branch 的 run 依時間排序，找出每一段「紅 → 綠」：
  紅段起點 = 第一個 conclusion == failure 的 run 的 createdAt
  紅段終點 = 該段之後第一個 conclusion == success 的 run 的 createdAt
mttr = median(終點 - 起點)
```
- 來源：`gh run list --branch main --limit N --json conclusion,createdAt`（經 `pipeline-read`）。
- 排除：仍在紅、尚未轉綠的段（未完成，不列入；但要在報告註明「進行中 n 段」）。
- 排除：`environment` 類的紅（若 `output/triage-reports/` 有標）——那是 infra 問題不是測試修復時間，計入會失真。

## flaky_rate — flaky 佔失敗比
**定義**：被判定為 flaky 的失敗數 ÷ 該期總失敗數。

```
flaky_rate = flaky 失敗筆數 / 總失敗筆數
```
- 來源：**直接引用** `output/flaky-registry.yaml`（`flaky-manager` 維護），不自行重跑或重算重現率。
- 另報 `flaky_rate_overall`（flaky 執行次數 ÷ 總執行次數）供跨專案比較。
- 註：分母是「失敗數」不是「測試數」——這個指標回答的是「紅燈裡有多少是雜訊」。

## first_pass_rate — 首次通過率
**定義**：不依靠 retry 就綠的 run 比例。

```
first_pass_rate = (第一次嘗試即 success 的 run 數) / 總 run 數
```
- 來源：run 歷史的 `run_attempt`（`gh run view --json` 有）；`run_attempt > 1` 才綠的不算。
- 驟降是最靈敏的早期警訊：通常代表有新的不穩定性或真 bug 剛進來 → 路由 `pipeline-triage`。

## suite_duration_p50 / p95 — 套件耗時
**定義**：整個測試 job 從開始到結束的耗時分位數。

```
duration = job.completed_at - job.started_at   （取測試 job，非整個 workflow）
p50 = 中位數, p95 = 95 分位
```
- 來源：`gh run view --json jobs`。
- 分片時取**最慢那片**（牆鐘時間由它決定），並另記 `runner_minutes = Σ 各片耗時`（成本）。
- p95 比 p50 重要：偶爾很慢的那幾次才是讓人不敢跑 CI 的原因。

## assignment_latency — 派工延遲
**定義**：run 轉紅到對應 issue 被 assign 的時間中位數。

```
latency = issue.assigned_at - run.created_at
```
- 來源：`output/triage-reports/<date>_<run>.md`（`pipeline-triage` 產）＋ `output/issues-index.yaml` ＋ `gh issue view --json assignees,createdAt`。
- 沒開單的紅（自動判為 flaky / environment）不列入。
- 這是唯一一個**主要衡量人與流程、而非測試品質**的指標；超標通常是人力或分派規則問題，路由給人。

## quarantine_count — 隔離中的測試數
**定義**：`output/flaky-registry.yaml` 中 `status: quarantined` 的筆數；另記 `expired`（`status: escalated` 或 `expires_at` 已過）。

- 來源：直接數 registry。
- **`expired > 0` 一律 alert**，不管總數多少——逾期未處置的隔離就是安靜消失的覆蓋率。

## gate_pass_rate / override_count — 放行健康度
**定義**：`output/pipeline-gate.yaml` 中 `verdict == PASS` 的比例；`override_count` 為 `verdict == OVERRIDE` 的筆數。

- 來源：直接數 `output/pipeline-gate.yaml`。
- **override 變多的解讀**：不是「人在作弊」，而是「閘門準則與現實脫節」的訊號——例如把不穩定的套件列進 `required_suites`。路由給人檢視 config，而不是路由去收緊閘門。

## coverage_gap（可選）
**定義**：`output/traceability.yaml` 中未被任何測試或 finding 覆蓋的需求數。

- 來源：`traceability`（workflow bucket）產出；沒跑過就標 `no-data`，不要當成 0。
