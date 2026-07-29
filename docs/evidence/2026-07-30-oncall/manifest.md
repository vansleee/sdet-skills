# Evidence Manifest — 20260730 toolshop oncall（Bug Hunting build）

- 受測站台：https://with-bugs.practicesoftwaretesting.com/#/（由 practicesoftwaretesting.com 的「🐛 Bug Hunting」按鈕開啟）
- Charter：charters/toolshop-login-cart.yaml
- 帳號：customer@practicesoftwaretesting.com（demo 公開帳號）
- 工具：playwright MCP，單一 Chromium session
- 邊界：未做註冊、未進 checkout 的 payment 步驟、未做 production 寫入

| 檔案 | 內容 |
|---|---|
| exploration-log.yaml | 13 步探索路徑與每步理由、停手原因 |
| results.yaml | 12 筆結構化結果（pass / fail / anomaly / inconclusive） |
| candidates.yaml | hunter 輸出：6 個候選 + 2 筆未達門檻留人判 |
| packages/ | 每個候選的可攜 Evidence Package（給盲驗用） |
| console.log | 整段 console（含 broken.png 404、/users/me 401） |
| network.log | 整段 API 請求（含 /users/login 200、/products/search 200） |
| 01-bughunting-enabled.png | Bug Hunting 模式啟動後的畫面 |
| 02-product-1-detail.png | 商品頁全頁（含 Reltded products 拼錯、按鈕重疊） |
| 03-qty-plus-noop.png | 商品頁按 ＋ 兩次後數量仍為 1 |
| 04-product2-qty-leak.png | 切到 product/2 後數量欄仍是前一個商品的 3 |
| 05-cart-totals.png | 購物車：列 Total $00.00、頁尾 $78.48 |
| 06-cart-line-total-zero.png | 改量 3→5 後頁尾 $106.78、列 Total 仍 $00.00 |
| 07-home-link-goes-contact.png | 點 Home 後停在 Contact 表單 |
| 08-search-no-results.png | 搜尋 0 筆結果正常；同畫面可見 Sorth / Serch 拼錯與破圖 |
| 09-qty-leak-and-plus-noop-repro2.png | 第二次跨商品數量外洩 + ＋ 無效 |
| snap-01-home.yml / snap-02-product1.yml | a11y snapshot（含 Home href=#/contact 佐證） |
