---
name: failure-analysis
description: 一支自動化測試紅了，分析根因並分流：選擇器/等待/測資/斷言/環境/產品迴歸/flaky——先歸類，別急著修。測試失敗、要判斷「這支為什麼紅、誰該修」時使用；`pipeline-triage` 對每個根因群呼叫它一次。
---

# Failure Analysis（一筆）

輸入一筆失敗測試（nodeid、error、traceback + evidence：trace/screenshot/console/network），輸出分類 + 依據 + 分流。**紅了先別急著修，先搞清楚是誰的錯。** 設計理念見 `docs/maintain/failure-analysis.md`。

> 一筆 vs 一批：這支處理**一筆**。CI 一次紅一片時，由 `pipeline-triage` 先 fan-in 合併成根因群，再對**每群呼叫本 skill 一次**（不要逐筆）。

## 分類表（classification）

| classification | 訊號 | 分流 fix_target |
|---|---|---|
| `locator` | 找不到元素 / selector 失效或 drift | `test-heal`（更新 locator）|
| `wait-timing` | 元素還沒好就操作、偶發逾時 | `test-heal`（改對等待條件，禁 waitForTimeout）|
| `test-data` | 帳號被鎖/過期、髒資料 | `test-data`（隔離/自備）|
| `fixture-isolation` | 前一測試污染了狀態 | `test-heal`（修 fixture/清理）|
| `assertion-mismatch` | expected ≠ actual | **先問 `test-oracle`**（見下）|
| `environment` | 5xx/timeout/DNS/憑證/基礎設施 | 重試 + 查 infra，**不動測試** |
| `product-regression` | 產品真的變了/壞了 | 走產品 bug 流程（`bug-verifier` → `triage`）|
| `flaky` | 間歇重現 < 100% | `flaky-detect` / `flaky-manager` |
| `cascade` | 前置失敗連鎖導致 | 修根源那一筆，其餘標 cascade |
| `unknown` | 證據不足以歸類 | needs-investigation，補證據 |

## 關鍵分岔：assertion-mismatch 是測試的錯還是產品的錯

expected ≠ actual 時**不要自己猜**，交給 `test-oracle` 判斷「這個新行為符不符合規格/預期」：
- 產品**應該**變成這樣（規格改了）→ **測試過時** → `test-heal` 更新斷言。
- 產品**不該**變成這樣 → **product-regression** → 走產品 bug 流程，**不准**改斷言遷就（那是綠色作弊）。

## 規則
- 依 evidence + traceback 判類，`basis` 要指向具體證據，不憑印象。
- 只有 `product-regression` 走 bug 流程；其餘留在測試側處理。
- **只分類 + 分流，不動手修。** 判準是「誰該修」，動手交 `fix_target` 那一欄指到的 skill。

## 輸出（格式，非某次執行結果；附加到該筆 finding）
```yaml
nodeid: "checkout.spec.ts > applies coupon"
classification: locator
confidence: high
basis: "trace 顯示 .btn-apply 不存在;DOM 已改為 [data-test=apply-coupon]"
fix_target: test-heal
next_step: "更新 locator 為 [data-test=apply-coupon]"
```

## 上下游
上游：`pipeline-read`（單筆失敗）、`pipeline-triage`（每個根因群呼叫一次）、`re-run-gate`（escalate 的）。下游：依 `fix_target` 分流——`test-heal` / `test-data` / `flaky-detect` / `test-oracle`（assertion-mismatch）/ `bug-verifier` → `triage`（product-regression）。
