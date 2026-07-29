---
name: quality-gate
description: merge/release 前的 pipeline 放行閘：彙整 run 結果、隔離名單、blocker issue，逐條附證據裁決 PASS / FAIL / OVERRIDE 並留痕。只裁決，不 merge。
disable-model-invocation: true
---

# Quality Gate（pipeline 層）

輸入一個候選（PR / commit / release build），輸出放行裁決 + 逐條證據 + 留痕。設計理念見 `docs/infra/quality-gate.md`。

> **三層閘門分工**：`issue-quality-gate` 管「一張 issue 能不能開」→ **本 skill** 管「這個 build 能不能放行」→ `release-signoff` 管「整個 release 對需求能不能簽出去」。本 skill 的輸出是上層的證據，不重複做上層的判斷。
> 狀態檔：`output/pipeline-gate.yaml`（**注意**：與 `issue-quality-gate` 的 `output/gate.yaml` 是不同檔案，別混用）。

## 輸入 / 輸出
- **輸入**：候選識別（PR 編號 / sha / tag）＋ `pipeline-read` 的 run 結果 ＋ `output/flaky-registry.yaml` 隔離名單 ＋ open blocker issue（`gh issue list --label blocker`）＋ 準則（`config/sdet-config.yaml` 的 `gate`）。
- **輸出**：裁決（`PASS` / `FAIL` / `OVERRIDE`）＋ 逐條評估表（每條附證據出處）＋ 寫入 `output/pipeline-gate.yaml` 的留痕。

## 準則（AND，全過才 PASS；門檻讀 config，不寫死）

| # | 條件 | 判準 | 證據來源 |
|---|---|---|---|
| 1 | `required_suites_green` | config 列的必跑套件全綠 | `pipeline-read` 的 `totals` / `failures` |
| 2 | `no_count_mismatch` | `passed+failed+skipped == total`，無 `count-mismatch` warning | `pipeline-read` 的 `warnings` |
| 3 | `no_open_blocker` | 無 open 的 blocker label issue 指向此範圍 | `gh issue list` + `output/issues-index.yaml` |
| 4 | `quarantine_within_budget` | 隔離中的測試數 ≤ `gate.max_quarantined` | `output/flaky-registry.yaml` |
| 5 | `no_expired_quarantine` | 無逾期未處置的隔離（`status: escalated`） | `output/flaky-registry.yaml` |

**隔離中的測試紅了不算 fail**（否則隔離沒意義），但**一律列進報告**——放行的人必須看到「這版有幾支測試是關掉的」。

## 步驟
1. **收證據**：呼叫 `pipeline-read` 取最新 run；讀 registry、blocker issue、config 準則。
2. **逐條評估**：每條標 `pass` / `fail` / `inconclusive`，並寫 `basis` 指向具體證據（run URL、issue URL、registry 條目）。
3. **缺證據不當 PASS**：拿不到 run、artifact 過期、指令失敗 → 該條標 `inconclusive`，整體裁決 `FAIL`，`blocked_on` 寫「缺什麼證據、去哪拿」。
4. **裁決**：全 `pass` → `PASS`；任一 `fail` / `inconclusive` → `FAIL`。
5. **Override（僅限人主動要求）**：依 `config/governance.yaml` 的 `override.require_reason: true` **強制留痕**——誰、何時、理由、硬推了哪幾條。沒有理由就不寫、不放行。
6. **留痕**：寫 `output/pipeline-gate.yaml`（先給人看再寫）。
7. **報告**：輸出逐條表 + 一行摘要（`PASS/FAIL`、幾條不過、隔離中幾支）。

## 鐵則
- **AND，不是加權平均。** 四條滿分救不了一條 fail。
- **`inconclusive` 不得當 PASS。** 「查不到」和「沒問題」是兩件事，混為一談就是拿假的綠燈換過關。
- **只裁決、不執行。** 本 skill **不 merge、不 tag、不 deploy**——`merge_pr` 在 `config/governance.yaml` 的 `forbidden` 名單。放行動作（貼 label、留言）也要先確認才做。
- **override 必留痕，且不可事後補。** 沒有理由的硬推＝沒有 override。
- 本 skill 不分析失敗（`failure-analysis` / `pipeline-triage`）、不決定 flaky 政策（`flaky-manager`）、不做需求層放行（`release-signoff`）。

## 輸出（格式，非某次執行結果）
```yaml
# output/pipeline-gate.yaml
- candidate: "PR #482 @ abc1234"
  evaluated_at: 2026-07-29T10:12:00Z
  run: "https://github.com/<owner>/<repo>/actions/runs/1234567890"
  checks:
    required_suites_green:    { result: pass, basis: "e2e 318/318 綠(run 1234567890)" }
    no_count_mismatch:        { result: pass, basis: "318 = 314+0+4" }
    no_open_blocker:          { result: fail, basis: "#471 blocker,結帳金額錯誤,open" }
    quarantine_within_budget: { result: pass, basis: "隔離 3 支 ≤ max 5" }
    no_expired_quarantine:    { result: pass, basis: "registry 無 escalated" }
  verdict: FAIL
  blocked_on: "先處理 blocker #471"
  quarantined_note: "本版有 3 支測試被隔離,該區覆蓋為關閉狀態:checkout/coupon, cart/remove, login/sso"
  override: null      # 若硬推:{ by: "<who>", at: "<when>", reason: "<why>", forced: [no_open_blocker] }
```

## 上下游
上游：`pipeline-read`（run 證據）、`flaky-manager`（隔離名單）。**只由人發動**——沒有 skill 呼叫它，放行是人的決定點。下游：`release-signoff`（吃本 skill 的 `output/pipeline-gate.yaml` 當證據）、`pipeline-observability`（gate 通過率、override 次數）、`status-report`（引用裁決）。
