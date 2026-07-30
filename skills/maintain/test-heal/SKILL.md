---
name: test-heal
description: 修好一支「測試自己壞掉」的測試：只改測試、不改產品，且不把測試改爛來騙綠燈。`failure-analysis` 判為 test-defect、或 `flaky-detect` 帶著 classification 轉過來時使用。
---

# Test Heal

輸入一筆被 `failure-analysis` 判為 **test-defect** 的失敗，輸出修好的測試 patch。設計理念見 `docs/maintain/test-heal.md`。

> 只吃 test-defect。`product-regression`（走 bug 流程）、`environment`（重試/查 infra）、`flaky`（`flaky-manager`）一律**拒絕修**。硬修只會把真問題蓋掉。

## 只准這樣改（allowed）

表的 key 是 `failure-analysis` 的 `classification`。`flaky-detect` 轉過來的用它輸出的 `classification` 欄查表，**別拿 `suspected_root_cause` 對**（那是另一套詞彙）。

| classification | 允許的修法 |
|---|---|
| `locator` | 更新為穩定選擇器（role / `data-test` 優先，見 `references/test-design.md`）|
| `wait-timing` | 改成 web-first assertion / 正確等待條件 |
| `fixture-isolation` | 修 fixture 與清理，讓測試自備、自收拾 |
| `test-data` | 改用獨立測資（交 `test-data`）|
| `assertion-mismatch` | **僅當** `test-oracle` 已確認「產品合法變更」→ 更新斷言對到新規格 |

## 死都不准（forbidden＝綠色作弊）

禁項清單與唯一例外見 `references/green-cheating.md`。**這支 skill 存在的意義就是擋掉那張表**。
本 skill 另有一條自己的界線：**只改 `tests/`，不動產品程式碼**。

## 驗收（硬性）
**修完的測試，要能在「舊/壞行為」下重現紅、在「新/對行為」下轉綠。**
- 具體：對舊行為（或 mock 舊回應）跑一次必須紅；對現況跑一次必須綠。
- 只綠不紅代表斷言可能已經失效，退回重修。
- 綠燈的最終確認交 `re-run-gate`。

## 規則
- 只動測試碼，不動產品。
- **批次修復需人審**（見 `config/governance.yaml`）；單支可自主但仍要過上面的驗收。

## 輸出（格式，非某次執行結果）
```yaml
nodeid: "<file> > <test name>"
classification: locator          # 對應 failure-analysis 的分類,決定允許哪種修法
patch: "tests/<area>.spec.ts 的 diff"
what_changed: "<改了什麼、為什麼>"
red_proof: "<對舊行為重現紅的證據:指令 + 失敗訊息>"
green_proof: "<對現況轉綠的證據>"
next_step: "交 re-run-gate 驗穩"
```

## 上下游
上游：`failure-analysis`（判 test-defect）、`flaky-detect`（帶 `classification` 欄轉過來）、`pipeline-triage`（一批裡的 test-defect 群）、`flaky-manager`（隔離到期 escalate）。下游：`re-run-gate`（驗穩定綠）。
