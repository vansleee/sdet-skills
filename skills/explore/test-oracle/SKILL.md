---
name: test-oracle
description: 判斷一個 anomaly 到底是不是 bug——拿產品行為比對 oracle（內部一致性 / API↔UI / 無 console error / 規格 / 使用者期待 / 對照品）。要判「是不是真的錯」「違反了哪一條」時使用。關鍵詞：oracle、是不是 bug、判定、一致性、規格、verdict。
---

# Test Oracle

輸入一個 anomaly / fail 候選（來自 `explore` / `classify-anomaly`，需附證據），輸出 verdict：命中哪條 oracle → `bug`；找不到 oracle → `needs-spec` / `inconclusive`。**沒有 oracle 就沒有 bug——只能說「怪」，不能說「錯」。** 設計理念見 `docs/explore/test-oracle.md`。

## Oracle 來源（由強到弱、依可得性挑用）
| oracle | 判準 | 需要外部資訊？ |
|---|---|---|
| 內部一致性 | 產品自相矛盾（同一數字兩個值、狀態前後不一）| 否（最強，優先用）|
| API ↔ UI 一致 | 畫面結果與 API 狀態碼不符 | 否 |
| 無 console error | 正常操作不該噴 error | 否 |
| 規格 / 需求 | 與文件、驗收條件不符 | 是（要有 spec）|
| 使用者期待 / 領域常識 | 違反常理（金額為負、數量非整數）| 弱（易主觀，需標明）|
| 對照品 / 歷史行為 | 與同類產品或過去版本不同 | 是 |

## 步驟
1. 讀該 anomaly 的證據（screenshot / network / console）。
2. 由強到弱試 oracle：先找「不需外部資訊」的（內部一致性、API↔UI、console）。
3. 命中 → `verdict: bug`，寫下 `oracle_used` + `basis`（違反了什麼、指向證據）。
4. 都不命中、要有規格才判得動 → `verdict: needs-spec`（寫「缺哪份規格 / 該問誰」）。
5. 證據不足以套任何 oracle → `verdict: inconclusive`（寫還缺什麼證據）。

## 規則
- **沒有 oracle 命中，不得判 bug。** 只能 `needs-spec` / `inconclusive`。
- 「不需外部規格」的 oracle（內部一致性、API↔UI、console）優先——它們最不會吵、最站得住。
- 使用者期待類 oracle 主觀；用了要明講「這是常識判斷、非規格」。
- verdict 寫回 finding：`verdict` / `oracle_used` / `basis`。判 bug 者才續走 `bug-verifier` / 開單。

## 輸出（附加到 finding）
```yaml
- id: R-05
  status: anomaly
  verdict: bug
  oracle_used: 內部一致性
  basis: "qty=0 時單列 Total 顯示 $0.00,但頁尾 Total 仍 $14.15,同一畫面自相矛盾"
- id: F2
  status: anomaly
  verdict: needs-spec
  oracle_used: —
  basis: "空車時 navbar 無 cart icon;無內部矛盾、無 API/console 違反,是否刻意設計需產品規格"
```
