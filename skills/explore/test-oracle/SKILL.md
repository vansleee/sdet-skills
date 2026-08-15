---
name: test-oracle
description: 判斷一個 anomaly 到底是不是 bug：拿產品行為比對 oracle（內部一致性 / API↔UI / 無 console error / 規格 / 使用者期待 / 對照品；API 情境另加狀態碼語意 / error envelope / 冪等 / 授權邊界 / 契約 schema）。要判「是不是真的錯」「違反了哪一條」時使用。關鍵詞：oracle、是不是 bug、判定、一致性、規格、契約、schema、verdict。
---

# Test Oracle

輸入一個 anomaly / fail 候選（來自 `explore` / `classify-anomaly`，需附證據），輸出 verdict：命中哪條 oracle → `bug`；找不到 oracle → `needs-spec` / `inconclusive`。**沒有 oracle 就沒有 bug，只能說「怪」，不能說「錯」。** 設計理念見 `docs/explore/test-oracle.md`。

## Oracle 來源（由強到弱、依可得性挑用）
| oracle | 判準 | 需要外部資訊？ |
|---|---|---|
| 內部一致性 | 產品自相矛盾（同一數字兩個值、狀態前後不一）| 否（最強，優先用）|
| API ↔ UI 一致 | 畫面結果與 API 狀態碼不符 | 否 |
| 無 console error | 正常操作不該噴 error | 否 |
| 規格 / 需求 | 與文件、驗收條件不符 | 是（讀 `knowledge/` 的業務規則，路徑同 `references/config-resolution.md` 的 slug 規則）|
| 使用者期待 / 領域常識 | 違反常理（金額為負、數量非整數）| 弱（易主觀，需標明）|
| 對照品 / 歷史行為 | 與同類產品或過去版本不同 | 是 |

## API 專屬 oracle（被測物是端點本身時加用這幾條）
判的是 response 而不是畫面，證據來自 `api-evidence` 的 `requests.jsonl`。契約來源讀 `product-context.md` 的「API」段（哪一份由 `references/config-resolution.md` 決定）。

| oracle | 判準 | 需要外部資訊？ |
|---|---|---|
| 狀態碼語意 | 狀態碼與 body 的意思不符（`200` 包著錯誤訊息、失敗卻回 `200`、找不到資源回 `500` 而非 `404`）| 否（最強的 API oracle）|
| error envelope 一致 | 同一個 API 的錯誤回應結構在不同端點長得不一樣 | 否 |
| 冪等 / 重放 | 該冪等的動作（`GET`／`PUT`／`DELETE`）重打結果不同，或重送同一筆建立請求產生兩筆 | 否 |
| 分頁 / 排序一致 | 逐頁取回的總數或內容與單次全取不符、有重複或漏項 | 否 |
| 授權邊界 | 換一個帳號的 token 或換一個 id 就取得不屬於它的資料（IDOR）；未帶憑證仍回 `2xx` | 否 |
| 契約 / schema 符合 | response 與 OpenAPI／GraphQL schema 不符（缺必填欄位、型別錯、多回不該回的欄位）| 是（要有契約來源）|
| header 與 content-type | 宣告的 `Content-Type` 與實際 body 不符、該有的快取或安全 header 缺漏 | 弱 |

## 步驟
1. 讀該 anomaly 的證據（screenshot / network / console，或 `api-evidence` 的 `requests.jsonl`）。
2. 由強到弱試 oracle：先找「不需外部資訊」的（內部一致性、API↔UI、console；API 情境再加狀態碼語意、error envelope、冪等、授權邊界）。
3. 命中 → `verdict: bug`，寫下 `oracle_used` + `basis`（違反了什麼、指向證據）。
4. 免費 oracle 全不命中 → 讀 `knowledge/` 的業務規則再判一次；命中就寫 `oracle_used: 規格`，`basis` 要引到是哪一條（檔名＋規則原文）。
5. 連 `knowledge/` 也判不動 → `verdict: needs-spec`（寫「缺哪份規格 / 該問誰」，並建議補進 `knowledge/`）。
6. 證據不足以套任何 oracle → `verdict: inconclusive`（寫還缺什麼證據）。

## 規則
- **沒有 oracle 命中，不得判 bug。** 只能 `needs-spec` / `inconclusive`。
- 「不需外部規格」的 oracle（內部一致性、API↔UI、console）優先。它們最不會吵、最站得住。
- 使用者期待類 oracle 主觀；用了要明講「這是常識判斷、非規格」。
- **契約來源填「無」時，契約 oracle 直接不可用**，不准拿「我覺得這個欄位應該要有」當 schema 判準；降級去用狀態碼語意與一致性，判不動就 `needs-spec`。
- **規格 oracle 只認 `knowledge/` 寫著的句子。** `knowledge/` 不存在或沒有相關規則，這條 oracle 不可用，不准拿「我覺得應該要」補位；判不動就 `needs-spec` 並建議補 `knowledge/`。
- **`4xx` 本身不是 bug。** 打錯參數換來 `400`、沒帶 token 換來 `401`，那是產品做對了。要判 bug 的是「該擋沒擋」與「該過卻擋」。
- **`429` 先當環境訊號，不當產品 bug**：對照 `product-context.md` 記的速率限制，超過就是自己打太快，交 `classify-anomaly` 標 `environment`。
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
- id: R-11
  status: anomaly
  verdict: bug
  oracle_used: 規格
  basis: "數量填 150 被接受並寫回(PUT 回 200,quantity=150);
          knowledge/product-overview.md「業務規則」:數量為 1–99 的整數,超出範圍應擋下。屬該擋沒擋"
- id: A-03
  status: anomaly
  verdict: bug
  oracle_used: 授權邊界
  basis: "GET /users/2 帶 user1 的 token 回 200 並含 user2 email;requests.jsonl#7,同一端點不帶 token 回 401,故非公開資源"
```
