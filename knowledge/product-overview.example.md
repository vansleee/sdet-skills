# 受測產品總覽（範本 — 複製成 product-overview.md 後填寫；真檔已 gitignore）

## 一句話
<這個產品是做什麼的、給誰用>

## 核心模組 / 領域
| 模組 | 做什麼 | 關鍵頁面 / API | 詳細知識 |
|---|---|---|---|
| <例：結帳> | <一句話> | <路徑> | `domains/checkout.md` |
| <例：會員> | <一句話> | <路徑> | `domains/account.md` |

## 業務規則（會變成 oracle 的判準）
> `test-oracle` 判「對不對」時會讀這裡。寫「應該怎樣」，不是「怎麼操作」。
- <例：折扣券不可與會員價疊加>
- <例：數量必須為 1–99 的整數>
- <例：未付款訂單保留 30 分鐘後釋放庫存>

## API 事實
> 「怎麼連上 API」（base URL、憑證變數名、契約檔位置）屬於設定，寫在 `config/product-context.md`。
> 這裡只寫**事實**：這個 API 承諾什麼、錯誤怎麼表達、誰能看什麼。`test-oracle` 的 API oracle 讀它。

- 錯誤回應的統一結構：<例：`{ error: { code, message, fields } }`；HTTP 狀態碼與 `code` 的對應表>
- 常用狀態碼慣例：<例：驗證失敗回 422 不是 400；找不到資源回 404 不是 200 空陣列>
- 授權模型：<誰能讀誰的資料、哪些端點需要哪個角色>
- 冪等承諾：<哪些端點宣稱冪等、用什麼鍵去重>
- 分頁慣例：<例：`page` 從 1 起算，`meta.total` 是全體筆數不是本頁>
- 已知不對稱：<例：UI 的欄位名與 API 不同名的那幾個>

## 名詞表（glossary）
- <術語> = <意思>

## 環境 / 帳號
- 測試帳號來源：env:`<VAR_NAME>`（值不寫在這裡）
- base URL:staging=`<...>` / prod=`<...>`
- 已知 flaky / 已知 issue 連結：<...>

## 活文件連結（single source of truth）
- PRD / 規格：<url>
- 設計稿：<url>
- API 文件：<url>
