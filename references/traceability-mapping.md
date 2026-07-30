# 需求 ↔ 測試 ↔ finding 的對應規則

`traceability` 讀本檔建立對應。**規則在這裡，資料在 `output/traceability.yaml`**。狀態檔只存資料，不存演算法（見 `docs/state-files.md`）。

## req_id 命名

```
REQ-<AREA>-<NNN>
例：REQ-CHECKOUT-005、REQ-AUTH-012
```
- `AREA` 用 `knowledge/domains/<area>.md` 的檔名（大寫）；單檔 `knowledge/` 時用小節標題。
- **`req_id` 一旦發出就不再變動。** 需求改寫內容可以，換號不行。換號會讓所有既有對應斷掉，而且斷掉時不會有錯誤訊息。
- 需求被移除：標 `status: retired`，保留 id，不回收再利用。

## 測試怎麼宣告它覆蓋哪條需求

**優先序**（由強到弱，取第一個命中的）：

| # | 方式 | 樣子 | 信心 |
|---|---|---|---|
| 1 | 明示 annotation | `test('...', { annotation: [{ type: 'req', description: 'REQ-CHECKOUT-005' }] }, ...)` | high |
| 2 | tag | `test('rejects expired coupon @REQ-CHECKOUT-005', ...)` | high |
| 3 | 對照檔 | `traceability-map.yaml` 手動維護 `req_id → nodeid[]` | high |
| 4 | 檔名／describe 區塊語意相符 | `checkout-coupon.spec.ts` ↔ `REQ-CHECKOUT-*` | **low → 標 `uncertain`** |

前三種是「測試自己宣告的」，可信；第 4 種是推測，**一律標 `uncertain`，不計入 covered**。專案要提高可信度就往 1–3 遷移，不是靠放寬第 4 條。

## finding 怎麼對到需求
- finding 的 `oracle` 欄若引用了 `knowledge/` 的某條規則 → 直接對到該 `req_id`（high）。
- 只有區域相符（同一個 area）→ `uncertain`。
- 對不到 → **finding 孤兒**，這是正常且有價值的訊號：探索找到了規格沒寫的行為。建議補 `knowledge/`。

## status 判定

| status | 條件 |
|---|---|
| `covered` | 至少一筆 high 信心的測試或 finding 對到 |
| `uncertain` | 只有 low 信心（第 4 種）的對應 |
| `gap` | 完全沒有對應 |
| `retired` | 需求已下線，保留 id 供歷史追溯 |

**`uncertain` 不計入 `covered`。** 把推測算成覆蓋，就是在製造假的安全感。

## 不做的事
- **不算單一覆蓋率百分比。** 一旦有這個數字，它就會變成 KPI，接著有人用廢測試把它衝高。輸出對照表與 gap 清單，讓人看見「哪一條沒守」，而不是「守了幾成」。
- **不自動刪測試。** 測試孤兒只產生 `test-prune` 候選，且 `test-prune` 本身也只給建議。
