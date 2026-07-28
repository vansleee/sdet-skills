---
name: test-parallelize
description: 用分片與平行讓一大包測試在時限內跑完：先驗測試獨立性，再算 shard 數、產 Actions matrix、合併報告、驗數。當套件太慢、PR 等太久、要開平行或加 shard 時使用。關鍵詞：太慢、平行、分片、shard、workers、時限、matrix。
---

# Test Parallelize（一批）

輸入套件規模與時限目標，輸出分片策略 + Actions matrix + 報告合併步驟。設計理念見 `docs/infra/test-parallelize.md`。

> **平行不是加速鍵，是放大鏡。** 測試若彼此不獨立，開平行只會把「偶爾紅」放大成「天天紅」。所以前置檢查不過就先擋下，不給分片。

## 輸入 / 輸出
- **輸入**：測試總數、baseline duration（單機序列跑完要多久）、時限目標（讀 `config/sdet-config.yaml` 的 `ci.target_duration_minutes`，PR 預設 10 分鐘）。
- **輸出**：`shards` / `workers` 建議值 ＋ matrix 片段 ＋ merge-reports job ＋ 成本估算，交 `ci-pipeline` 掛上去。

## 步驟

### 1. 前置檢查：獨立性（不過就停在這裡）
逐條驗，**任一條不過就先擋下**、把它轉給對應 skill 修好再回來：

| 檢查 | 不過的訊號 | 轉給誰 |
|---|---|---|
| 測資唯一 | 測試用寫死的帳號 / email / 商品名 | `test-data` |
| 無共用狀態 | 依賴前一支留下的登入態或資料 | `test-heal`（修 fixture）|
| 無順序依賴 | 換順序就紅（`--shuffle` 驗） | `test-heal` |
| 環境可隔離 | 共享環境沒有 namespace 慣例 | `test-env` |

快速驗法：本機用 `--workers=4 --shuffle` 跑一輪，新紅的那些就是不獨立的。

### 2. 算 shard 數
`shards = ceil(baseline_duration / target_duration)`，再加 1 當緩衝。上限讀 config 的 `ci.max_shards`。
每個 shard 內部再開 `workers`（Playwright 預設 CPU/2）——**先加 workers（同一台機器、免錢）再加 shard（多開 runner、要錢）**。

### 3. 產 matrix + 分片指令
Playwright：`npx playwright test --shard=${{ matrix.shard }}/${{ strategy.job-total }}`，reporter 設 `blob`。

### 4. 合併報告
分片後每片各有一份報告，**不合併等於下游全瞎**。加一個 `if: always()` 的 merge job：下載所有 `blob-report-*` → `npx playwright merge-reports --reporter=html,json` → 上傳成 `playwright-report` / `test-results-json`（名字照 `ci-pipeline` 的 artifact 契約）。

### 5. 驗數（必做）
合併後的 **total 測試數必須等於分片前的 total**。不相等代表某片整個沒跑或沒回報——這是分片最危險的失效模式：**看起來全綠，其實少跑了 1/4**。不相等就標 WARNING 並擋下，不當成通過。

### 6. 分桶平衡
預設用 Playwright 內建的平均分配。若最慢 shard 比最快多 40% 以上，改用歷史 duration 分桶（讀上幾次 run 的 JSON 報告，把測試依耗時貪婪分配）。**重算時機**：新增大量測試、或最慢/最快落差再次超過 40%。

### 7. 成本估算
`runner 分鐘數 ≈ shards × (target_duration + 啟動 overhead ~2 分鐘)`。列出「序列 vs 分片」的分鐘數對比給人看——**快不等於免費**，多開 4 片省 20 分鐘牆鐘、但帳單乘以 4。建議上限：`ci.max_shards`，或成本超過 `sdet-economics` 認可的門檻就回報而不是硬開。

## 鐵則
- **獨立性沒過不給分片。** 先修再平行，不然只是量產 flaky。
- **驗數不可省。** 全綠但少跑，比紅燈危險得多。
- **先 workers 後 shards。** 同機器的平行是免費的，多 runner 不是。
- 改 workflow / `playwright.config.ts` 是副作用：先列 diff 給人確認。
- 本 skill 不修測試（`test-heal`）、不管環境（`test-env`）、不定 flaky 政策（`flaky-manager`）。

## 輸出（格式，非某次執行結果）
```yaml
baseline_duration_min: 42
target_duration_min: 10
independence_check: pass       # 不 pass 就停,附不過的項目與轉給誰
shards: 5
workers_per_shard: 4
matrix: "shard: [1, 2, 3, 4, 5]"
merge_job: "playwright merge-reports --reporter=html,json"
count_check: "分片前 318 == 合併後 318"   # 不等就 WARNING 並擋下
cost_estimate: "序列 42 runner-min → 分片 5 × 12 = 60 runner-min（+43%,換 32 分鐘牆鐘）"
```

## 上下游
上游：`ci-pipeline`（要掛分片時呼叫）、`pipeline-observability`（duration 超標時建議來這裡）。前置相依：`test-data` / `test-env` / `test-heal`（獨立性沒過時先去修）。下游：分片後的 flaky 若變多，交 `flaky-manager`。
