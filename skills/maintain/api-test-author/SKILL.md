---
name: api-test-author
description: 把一條驗收條件或一次成功的端點探索固化成一支可維護的 API 測試：一支只驗一件事、狀態碼與 body 都驗、斷言綁契約、憑證走環境變數。
disable-model-invocation: true
---

# API Test Author

輸入一條驗收條件（或一次成功的端點探索路徑），輸出**一支**可重跑、可維護的 API 測試。`test-author` 的姊妹 skill，共用 `references/test-design.md` 的原則，差異在第 3、4 條（見該文件第 9 節）。設計理念見 `docs/maintain/api-test-author.md`。

> user-invoked：跟 `test-author` 同一個理由，多一支測試就是多一份要養一輩子的資產。

## 前置（缺了就停手回報，不要自己編）
- `config/product-context.md` 的「API」段：API base URL、認證方式與取憑證端點、契約來源、API testDir、版本策略。
- 憑證一律走環境變數（變數名由 product-context 指定），**不得寫進測試檔**。
- 契約來源填「無」時照樣可以寫，但 schema 斷言降級成逐欄位明寫，並在測試裡註明「無契約可比」。

## 先確認層級對不對
動手前對照 `references/test-design.md` 第 0 節。這條 AC 講的是畫面呈現 → 退回 `test-author`；講的是商業規則、驗證或權限 → 留在這裡。**已經有一支 UI 測試在驗同一條規則**，就不是新增，是把它降到 API 層再交 `test-prune` 評估上面那支。

## 五條紀律
1. **一支只驗一件事。** 一條 AC 一支測試。同一個端點的不同分支（成功、缺欄位、越權、邊界）各自一支，不要塞成一支跑一輪。
2. **名稱寫「規則是什麼」，不是「打了哪個端點」。**（○「過期折扣碼回 422 且不建立訂單」／×「POST /orders 測試」）
3. **狀態碼與 body 都要驗。** 只驗狀態碼會漏掉「`200` 包著錯誤訊息」；只驗 body 會漏掉語意錯的狀態碼。
4. **斷言綁契約，不比整包快照。** 有契約來源就用 schema 驗，沒有就逐欄位寫明「該有什麼、型別是什麼」。**禁止**把整份回應序列化成黃金檔比對，也禁止斷言欄位順序。
5. **不硬編會變動的資料**（id、時間戳、自動產生的編號）：從前置請求的回應讀出來再拿去比對；需要固定測資時交 `test-data`。

## 另外三條 API 特有的
- **前置資料不要用被測的那個端點建。** 用它建，它一壞就變成「前置失敗」，看不出真正壞的是誰。
- **非同步要等到終態。** 送出後背景處理、佇列、webhook 一律輪詢到成功、失敗或逾時三者之一，禁止固定 sleep。
- **驗權限的測試要驗兩邊。** 「本人拿得到」與「別人拿不到」是兩支，只寫其中一支等於沒驗到邊界。

## 斷言要帶意圖
每個斷言附一句「應該是什麼」，讓**失敗訊息本身**就說明預期，而不是丟一個 `expected 200, got 500`。

## 交付前自問（過不了就重寫）
- 這支壞掉時，讀失敗訊息的人**不看程式碼**能不能懂是哪條規則被違反？
- 它自備自清嗎（測資交 `test-data`）？跟別支有順序相依嗎？重跑第二次還會綠嗎？
- 這條規則是不是已經有 UI 測試在驗？重複就別新增（減法交 `test-prune`）。
- 寫完驗一次：把預期值故意改錯要**紅**，改回來要**綠**。只會綠的測試等於沒在測。

## 輸出（格式，非某次執行結果）
```yaml
spec: tests/api/<area>.spec.ts
test_name: "<被驗的規則>"
covers: "<story / AC 識別碼>"
endpoint: "POST /orders"
asserts: [status, body-schema, side-effect]
contract_source: "openapi.yaml#/paths/~1orders/post"   # 無契約時寫 none
auth: "env:API_TOKEN_USER1"
data: fixture            # 由 test-data 提供
verified: "改錯必紅、改回必綠"
```

## 上下游
上游：人（發動）、`test-planning` 的 plan、`explore` 端點側的一次成功路徑、`traceability` 的 gap。下游：`test-data`（測資）、`ci-pipeline`（掛進不裝瀏覽器的 API job）、`traceability`（宣告覆蓋哪些 `req_id`，`level: api`）、`test-prune`（將來的減法評估）。
