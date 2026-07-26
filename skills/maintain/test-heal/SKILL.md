---
name: test-heal
description: 修好一支「測試自己壞掉」的測試——只改測試、不改產品，且嚴禁把測試改爛來騙綠燈。當 failure-analysis 判為 test-defect（locator/wait/測資/fixture，或經 oracle 確認的測試過時）需要修復時使用。關鍵詞：修測試、self-heal、locator 壞掉、更新測試、綠色作弊。
---

# Test Heal

輸入一筆被 `failure-analysis` 判為 **test-defect** 的失敗，輸出修好的測試 patch。設計理念見 `docs/maintain/test-heal.md`。

> 只吃 test-defect。`product-regression`（走 bug 流程）、`environment`（重試/查 infra）、`flaky`（`flaky-manager`）一律**拒絕修**——硬修只會把真問題蓋掉。

## 只准這樣改（allowed）
| classification | 允許的修法 |
|---|---|
| `locator` | 更新為穩定選擇器（role / `data-test` 優先，見 `references/test-design.md`）|
| `wait-timing` | 改成 web-first assertion / 正確等待條件 |
| `fixture-isolation` | 修 fixture 與清理，讓測試自備、自收拾 |
| `test-data` | 改用獨立測資（交 `test-data`）|
| `assertion-mismatch` | **僅當** `test-oracle` 已確認「產品合法變更」→ 更新斷言對到新規格 |

## 死都不准（forbidden＝綠色作弊）
- 刪測試、加 `.skip` / `.fixme`、註解掉斷言
- 放寬/刪弱斷言來讓它過（`toBe` 改 `toBeTruthy`、拿掉關鍵欄位…）
- 加 `retry` / `waitForTimeout` 蓋掉時序問題
- 動到**產品程式碼**（本 skill 只改 `tests/`）

> 讓測試變綠最快的方法是把測試改爛。這裡的存在意義,就是擋掉這件事。

## 驗收（硬性）
**修完的測試,要能在「舊/壞行為」下重現紅、在「新/對行為」下轉綠。**
- 只綠不紅代表可能改爛了(斷言失效)——退回重修。
- 具體:對舊行為(或 mock 舊回應)跑一次必須紅;對現況跑一次必須綠。
- 綠燈的最終確認交 `re-run-gate`。

## 規則
- 只動測試碼,不動產品。
- 每次修復輸出 patch/diff + 一句「改了什麼、為什麼(對應 classification)」+ 舊行為重現紅的證據。
- **批次修復需人審**(見 `config/governance.yaml`);單支可自主但仍要過上面的驗收。
