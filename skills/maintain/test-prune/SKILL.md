---
name: test-prune
description: 判斷一支測試該留、該合併、還是該刪，並寫清楚刪掉之後失去的覆蓋；一律只給建議、交人核准。當套件肥大、有長期 skip／重複覆蓋／驗已下線功能的測試時使用。關鍵詞：刪測試、減法、淘汰、重複覆蓋、skip、維護成本。
---

# Test Prune（一支）

輸入一支測試，輸出 `keep` / `merge` / `remove` 的**建議**與理由。設計理念見 `docs/maintain/test-prune.md`。

> **只給建議。** 刪除不可逆，本 skill 不自行刪檔、不加 `.skip`；輸出一律帶 `needs_human_approval: true`（對齊 `config/governance.yaml` 的 needs_review 精神）。

## 三個提問
1. 它驗的**行為還存在嗎**？（功能已下線／規格已改 → remove 候選）
2. 它**跟別支重複嗎**？（同一條路徑被覆蓋兩次、沒有獨有斷言 → merge 候選）
3. 它壞掉時**你會不會真的去看**？（長期沒人理 → 它不是安全網，是噪音）

## 刪除候選訊號
- 長期 `.skip` / `.fixme`，超過 config 的保留期限仍未修。
- 覆蓋與其他測試重疊，且沒驗到任何獨有的斷言。
- 驗的是已下線或已改規格的功能。
- 維護成本遠高於它擋下的風險（常壞、常修、從沒抓到真 bug）。

## 硬性要求：先寫清楚失去什麼
**沒寫清 `coverage_lost` 就不准建議 remove。** 要具體到「哪個使用者可見行為之後沒有任何測試在守」，並指出是否有別支接手；接不上就降級成 `keep` 或 `merge`。

## 與 test-heal 的分界（重要）
本 skill 是 `test-heal` 的相反面，但**不准用「刪掉它」來解決一個會紅的測試**——那是綠色作弊。會紅的先走 `failure-analysis`：test-defect → `test-heal`；product-regression → 走 bug 流程；flaky → `flaky-detect`。
只有「這個行為已經不需要被測」才輪到本 skill。

## 輸出（格式，非某次執行結果）
```yaml
nodeid: "<file> > <test name>"
verdict: remove              # keep | merge | remove
reason: "<對應上面哪個訊號>"
coverage_lost: "<刪掉後沒人守的行為;無則寫 none>"
merge_into: "<verdict=merge 時填>"
needs_human_approval: true
```
