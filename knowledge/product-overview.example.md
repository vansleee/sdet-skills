# 受測產品總覽（範本 — 複製成 product-overview.md 後填寫；真檔已 gitignore）

## 一句話
<這個產品是做什麼的、給誰用>

## 核心模組 / 領域
| 模組 | 做什麼 | 關鍵頁面 / API | 詳細知識 |
|---|---|---|---|
| <例:結帳> | <一句話> | <路徑> | `domains/checkout.md` |
| <例:會員> | <一句話> | <路徑> | `domains/account.md` |

## 業務規則（會變成 oracle 的判準）
> `test-oracle` 判「對不對」時會讀這裡。寫「應該怎樣」，不是「怎麼操作」。
- <例:折扣券不可與會員價疊加>
- <例:數量必須為 1–99 的整數>
- <例:未付款訂單保留 30 分鐘後釋放庫存>

## 名詞表（glossary）
- <術語> = <意思>

## 環境 / 帳號
- 測試帳號來源:env:`<VAR_NAME>`（值不寫在這裡）
- base URL:staging=`<...>` / prod=`<...>`
- 已知 flaky / 已知 issue 連結:<...>

## 活文件連結（single source of truth）
- PRD / 規格:<url>
- 設計稿:<url>
- API 文件:<url>
