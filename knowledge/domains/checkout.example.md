# 領域知識範本：結帳（範本 — 複製成 checkout.md 後填寫）

> 中大型產品時，每個模組一份，skill 只載入相關那份（progressive disclosure），不整包塞進 context。

## 範圍
<這個模組涵蓋哪些頁面 / 流程 / API>

## 關鍵業務規則（oracle 判準）
> 這些是 `test-oracle` 的「規格 oracle」來源——有了它，很多 anomaly 才能被判成 bug 或 needs-spec。
- <例:金額不可為負>
- <例:單列小計變動時，頁尾總計必須同步重算>   # 有這條，「qty=0 頁尾未重算」就從 anomaly 升為明確的規格違反
- <例:結帳前必須先登入，或明確允許 guest 結帳>

## 狀態機 / 合法轉移
- <例:cart → address → payment → invoice；不可跳過 address 直接付款>

## 已知邊界 / 陷阱
- <例:cart id 存在瀏覽器本地，過期會 404——預期行為應該是靜默重建，還是提示使用者?>
