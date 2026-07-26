---
name: re-run-gate
description: 測試修好後重跑，確認是「穩定的綠」而不是「剛好過一次」；達標才放行，超過重試上限仍紅就 escalate。當 test-heal 修完要驗證、或要判斷一支測試是否真的穩定時使用。關鍵詞：重跑、re-run、重試、穩定綠、放行、escalate、max retries。
---

# Re-run Gate

輸入一支剛被 `test-heal` 修好的測試（或要驗穩的測試），重跑後給裁決：pass / flaky / escalate。設計理念見 `docs/maintain/re-run-gate.md`。

## 什麼才算過（green criteria）
「綠」的定義來自 `config/sdet-config.yaml`（預設：連續 N 次全綠，N=3）。**過一次不算過。**

## 重跑與裁決
1. 重跑該測試，最多 `max_retries` 次（config，預設 3）。
2. 依結果裁決：
   - **穩定綠**（達 green criteria）→ `pass`：修復成立，關閉該筆、寫回修復完成。
   - **間歇綠**（過但不穩，例如 3 次過 1）→ `flaky`：**不放行**，交 `flaky-detect` / `flaky-manager`，別假裝修好了。
   - **max_retries 仍紅** → `escalate`：留 issue 開著、標 `escalated: max retries reached`、交人（依 `config/governance.yaml`）。

## 鐵則
- **1/N 不是 pass。** 嚴禁「一直重跑到剛好過一次」當通過——那是拿 re-run 蓋 flaky，綠色作弊的變形。
- **一定要有停止條件。** 到 `max_retries` 就停，不無限重試。
- **每次都記錄**到 `runs/<date>.yaml`（重跑次數、逐次結果、最終裁決），供 ROI 與 flaky 趨勢用。
- 只裁決、不修：要再修回 `test-heal`，穩定性問題交 `flaky-manager`。

## 輸出
```yaml
nodeid: "checkout.spec.ts > applies coupon"
reruns: 3
results: [green, green, green]
verdict: pass          # pass | flaky | escalate
note: "連續 3 綠,達 green criteria"
```
