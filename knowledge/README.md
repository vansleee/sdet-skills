# knowledge/ — 受測產品的「事實」（product knowledge）

skill 是「能力」（怎麼做，產品無關、可重用）；這個資料夾是「事實」（產品是什麼，產品專屬）。**skill 讀這裡，但不把產品知識寫死進 skill**。這樣同一套 skill 換個產品，只要換掉這個資料夾。

## 為什麼獨立成一塊
- **保持 skill 可重用**：產品知識天生產品專屬，混進 skill 就不能 reuse。
- **餵給「規格 oracle」**：`explore/test-oracle` 判「對不對」時，很多情境只有規格說得準。像購物 demo 可以靠「內部一致性 / API↔UI」這種**不需外部規格**的 oracle；但公司自己的產品，這裡就是**規格 oracle 的判準來源**。
- **single source of truth**：一處維護，所有 skill 共用。

## 依規模分層（不要一步到位）
1. **小產品** → 一份 `product-overview.md`（複製 `product-overview.example.md` 填寫）。
2. **中型** → `domains/` 下每個模組一份（見 `domains/checkout.example.md`），skill 只載入需要的那份（progressive disclosure）。
3. **大型 / 文件會變** → 改用檢索（RAG）或 MCP resource 指向活文件（Confluence / Notion / repo docs），避免知識過期。

## gitignore 政策
真實產品知識可能含內部規格，**不進版控**；只 commit 範本（`*.example.md`）與本說明。規則見 repo 根 `.gitignore`。

## 與 `config/` 的關係
`config/product-context.example.md` 是「開工設定」層級的最小起點（base URL、帳號來源）。當產品知識長大到需要描述業務規則、領域、名詞表，就搬來 `knowledge/`。前者是「怎麼連上產品」，後者是「產品是什麼」。

API 照同一條線切：base URL、認證方式、憑證變數名、契約檔位置在 `config/`；這個 API 承諾什麼（錯誤結構、狀態碼慣例、授權模型、冪等承諾、端點清單與副作用）在 `knowledge/`。前者換環境會變，後者換環境不會。`explore` 的端點側靠 `knowledge/` 的端點清單才有得列，`test-oracle` 的 API oracle 也讀它。
