---
name: test-author
description: 把一條驗收條件或一次成功探索固化成一支可維護的 Playwright 測試：一支只驗一件事、穩定定位器、web-first 斷言、資料不硬編。
disable-model-invocation: true
---

# Test Author

輸入一條使用者故事／驗收條件（或一次成功的探索路徑），輸出**一支**可重跑、可維護的 Playwright 測試。設計理念見 `docs/maintain/test-author.md`，設計原則見 `references/test-design.md`。

> user-invoked：多一支測試就是多一份要養一輩子的資產，該不該加是人的決定，不讓模型在背景自行新增。

## 前置（缺了就停手回報，不要自己編）
- `config/product-context.md`：base URL、登入方式、Playwright config / testDir、**測試專屬屬性名稱**（`testIdAttribute`）。
- 帳密／token 一律走環境變數（變數名由 product-context 指定），**不得寫進測試檔**。
- `config/<project>/test-style.md`：這個專案的測試碼風格。**動筆前先讀**；沒有這個檔就沿用 `references/test-design.md` 的預設，不要自己另立一套。

## 五條紀律
1. **一支只驗一件事。** 一條 AC 一支測試；要驗兩件就開兩支，不要串成長流程。
2. **名稱寫「使用者看到什麼」，不是「你點了什麼」。**（○「套用折扣碼後顯示折後金額」／×「點擊 apply 按鈕」）
3. **定位器優先序**：測試專屬屬性（名稱讀 config）＞ 角色／可見文字 ＞ 其他。**絕不用**結構性 CSS（`div:nth-child(1)`）、深層 XPath、或會變動的自動產生 ID。
4. **等待用 web-first assertion**（會自動重試），**禁止**用 `waitForTimeout` 當等待手段。
5. **不硬編會變動的資料**（商品名、價格、ID）：從畫面或 API 讀出來再拿去比對；需要固定測資時交 `test-data`。

## 斷言要帶意圖
每個斷言附一句「應該是什麼」的訊息，讓**失敗訊息本身**就說明預期，而不是只丟一個 selector 逾時。

## 交付前自問（過不了就重寫）
- 這支壞掉時，讀失敗訊息的人**不看程式碼**能不能懂哪裡壞了？
- 它自備自清嗎（測資交 `test-data`）？跟別支有順序相依嗎？
- 跟現有測試重複嗎？重複就別新增（減法交 `test-prune`）。
- 寫完驗一次：把預期值故意改錯要**紅**，改回來要**綠**。只會綠的測試等於沒在測。

## 輸出（格式，非某次執行結果）
```yaml
spec: tests/<area>.spec.ts
test_name: "<使用者看到的結果>"
covers: "<story / AC 識別碼>"
locator_strategy: [test-attribute, role]
data: fixture            # 由 test-data 提供
verified: "改錯必紅、改回必綠"
```

## 上下游
上游：人（發動）、`test-planning` 的 plan（`how: test-author` 的待辦）、`explore` 的一次成功路徑、`traceability` 的 gap。下游：`test-data`（測資）、`ci-pipeline`（進 CI 跑）、`traceability`（宣告覆蓋哪些 `req_id`）、`test-prune`（將來的減法評估）。
