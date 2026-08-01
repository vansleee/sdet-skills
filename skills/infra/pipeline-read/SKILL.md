---
name: pipeline-read
description: 從 GitHub Actions run 拉失敗、artifact、annotation（用 gh），輸出結構化失敗清單。只讀不下結論。使用者貼 run 連結或問「CI 為什麼紅」時使用；任何 skill 要 run 證據都先經它，別自己重刻讀法。
---

# Pipeline Read

輸入一個 GitHub Actions run，輸出**結構化失敗清單**。infra 迴圈的感官：只讀不寫，把 raw run 變成下游吃得下的資料。設計理念見 `docs/infra/pipeline-read.md`。

> 只負責「讀出來、整理好」。合併根因是 `pipeline-triage`、分類單筆是 `failure-analysis`、判 flaky 是 `flaky-detect`。**本 skill 不下任何結論。**

## 輸入 / 輸出
- **輸入**：run id / run URL；或「某 branch 最新一次紅的 run」（`gh run list --branch <b> --status failure --limit 1 --json databaseId`）。
- **輸出**：`run` 摘要 ＋ `failures[]`（每筆含 nodeid / file / error signature / job / annotation / artifact 路徑）＋ `warnings[]`。狀態欄位沿用 `structured-result` 的六態。

## 步驟（**由粗到細，能停就停**）
1. **摘要先行**：`gh run view <id> --json databaseId,headBranch,headSha,conclusion,createdAt,jobs`。得到哪些 job 紅、各自幾秒。**這步通常就夠回答「哪裡紅」**。
2. **只拉失敗 log**：`gh run view <id> --log-failed`。**絕不 `--log`**（整包成功 log 動輒數萬行，燒 context 又沒資訊）。
3. **取 annotation**：`gh api repos/{owner}/{repo}/actions/runs/{id}/jobs --jq '.jobs[].steps'`，撈 failure annotation 與 step 層級的錯誤。
4. **需要才下載 artifact**：要逐筆 nodeid、要 trace 時才 `gh run download <id> -n test-results-json`（或 `-n traces`）。API job 的結果在 `api-test-results-json`、證據在 `api-evidence-<slug>`，兩個都要單獨拉。artifact 名照 `references/artifact-contract.md`。
5. **解析成結構**：每筆失敗抽 `nodeid` / `file` / `error_signature`（錯誤訊息正規化：去掉行號、timestamp、UUID、隨機測資，留下可比對的骨架）/ `job` / `shard` / `level`（`api` 或 `ui`，由來源 artifact 決定）。下游要靠 `level` 才分得出「契約漂移」跟「定位器失效」是兩群，別讓它們合併成一個根因。
6. **驗數**：`passed + failed + skipped == total`。不符就寫進 `warnings[]` 標 `count-mismatch`（判準與理由見 `references/artifact-contract.md` 的「靜默失蹤」）。
7. **輸出**：交給呼叫者。失敗數 ≥ config 的 `triage.batch_threshold`（預設 5）就在輸出裡建議轉 `pipeline-triage`；1 筆就建議轉 `failure-analysis`。

## error signature 正規化（下游合併根因靠它）
把易變的部分抽掉，讓「同一個原因」的失敗長得一樣：
```
locator('[data-test=id-8f3a2]') 逾時 30000ms at line 42
→ locator([data-test=id-<UUID>]) timeout at <line>
```
規則：UUID / 數字 id / timestamp / 絕對路徑 / 行號 → 佔位符；保留錯誤類型與 selector 骨架。

## 鐵則
- **只讀不寫：它是感官，不是手。** 觀察到什麼就回報什麼，動作留給下游。
- **由粗到細。** 先 summary、再失敗 log、最後才 artifact。整包 log 進 context 是本 skill 最容易犯、也最貴的錯（見 `sdet-economics`）。
- **不下結論。** 判「這是 flaky 還是壞了」不是本 skill 的事。輸出事實，讓下游判。
- **驗數不可省**（防靜默失蹤，見 `references/artifact-contract.md`）。
- 後端指令讀 `config/ci-backend-github-actions.md`；token 走 `GH_TOKEN` env，不落地。

## 輸出（格式，非某次執行結果）
```yaml
run:
  id: 1234567890
  branch: main
  sha: abc1234
  conclusion: failure
  url: "https://github.com/<owner>/<repo>/actions/runs/1234567890"
totals: { total: 318, passed: 300, failed: 14, skipped: 4 }
failures:
  - nodeid: "checkout.spec.ts > applies coupon"
    file: "tests/checkout.spec.ts:42"
    job: "e2e (shard 3)"
    level: ui
    error_signature: "locator([data-test=apply-coupon]) timeout at <line>"
    annotation: "Test timeout of 30000ms exceeded"
    artifacts: ["traces/checkout-applies-coupon/trace.zip"]
warnings:
  - code: count-mismatch
    detail: "passed+failed+skipped=318 但 report total=400,疑似 shard 4 未回報"
next_step: "14 筆 ≥ batch_threshold → 轉 pipeline-triage 合併根因"
```

## 上下游
上游：`duty-oncall`、使用者貼 run URL、`quality-gate`（要證據時）。下游：`pipeline-triage`（一批）、`failure-analysis`（一筆）、`flaky-manager`（跨 run 歷史）、`pipeline-observability`（指標原料）。
