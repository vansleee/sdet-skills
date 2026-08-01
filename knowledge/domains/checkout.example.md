# 領域知識範本：結帳（範本 — 複製成 checkout.md 後填寫）

> 中大型產品時，每個模組一份，skill 只載入相關那份（progressive disclosure），不整包塞進 context。

## 範圍
<這個模組涵蓋哪些頁面 / 流程 / API>

## 關鍵業務規則（oracle 判準）
> 這些是 `test-oracle` 的「規格 oracle」來源。有了它，很多 anomaly 才能被判成 bug 或 needs-spec。
- <例：金額不可為負>
- <例：單列小計變動時，頁尾總計必須同步重算>   # 有這條，「qty=0 頁尾未重算」就從 anomaly 升為明確的規格違反
- <例：結帳前必須先登入，或明確允許 guest 結帳>

## 狀態機 / 合法轉移
- <例：cart → address → payment → invoice；不可跳過 address 直接付款>

## 端點與契約
> 端點清單寫在這裡，`explore` 端點側才有得列（沒有 OpenAPI 時它只能從既有 network 紀錄反推，一定不完整）。

| 端點 | 做什麼 | 誰能打 | 有副作用？ |
|---|---|---|---|
| `POST /carts/{id}/items` | <一句話> | <登入使用者本人> | 是（寫入） |
| `GET /carts/{id}` | <一句話> | <本人> | 否 |

- 這個模組的錯誤碼：<例：`COUPON_EXPIRED` → 422；`STOCK_INSUFFICIENT` → 409>
- 不得自動化碰的端點：<例：`POST /orders/{id}/pay`，會觸發外部金流>

## 已知邊界 / 陷阱
- <例：cart id 存在瀏覽器本地，過期會 404，預期行為應該是靜默重建，還是提示使用者？>
