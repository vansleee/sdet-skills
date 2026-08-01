# 受測產品（範本 — 複製成 product-context.md 後填寫；真檔已 gitignore）

- 產品：<一句話說明>
- base URL:staging=<...> / prod=<...>
- 登入：storageState=<路徑>；帳密來源=env:<VAR_NAME>（值不寫在這裡）
- Playwright:config=<path> / testDir=<path> / reporter=<...>

## API（沒有可測的 API 就寫「無」，不要留空）

- API base URL:staging=<...> / prod=<...>（與網頁不同網域時務必分開寫）
- 認證方式：<bearer / cookie session / api key / oauth>；取得憑證的端點=<POST /auth/login>；憑證來源=env:<VAR_NAME>（值不寫在這裡）
- 契約來源：<OpenAPI 檔路徑或 URL / GraphQL schema / 無>（`test-oracle` 的 contract oracle 與 `api-test-author` 的 schema 斷言都讀它；填「無」代表這兩者降級成「只能驗狀態碼語意與一致性」）
- API 測試位置：testDir=<path>（與 UI 測試分開，CI 才跑得動不裝瀏覽器的快 lane）
- 版本策略：<路徑版號 /v1 / header / 無>
- 速率限制：<每分鐘幾次 / 無>（探索前要知道，否則會把 429 誤判成產品 bug）
- 不得碰的端點：<刪除、扣款、寄信、對外通知等有副作用的端點>（`explore` 與 charter 的 out-of-bounds 讀它）
