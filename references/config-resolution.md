# Config 解析規則（多專案）

可以同時支援多個待測試的產品，而這份定義主要是用來判斷要讀取哪一組 config。所有需要讀取的 config 的 skill 都需要 follow 這條規則，不能各自撰寫另外一套路徑的邏輯。相關設定怎麼產生可以參考 setup-sdet。

## 解析

1. 初次執行取 `project` slug，來源依序：呼叫端明講的 `project` → charter 的 `charter.project` 欄位 → 無。收到既有交接時沿用其 `project`，與 charter 或新指示衝突就停止核對，不在同一 finding 中途切換專案。
2. 有 slug → 路徑是 `config/<project>/<檔名>`。
3. 沒有 slug → 路徑是 `config/<檔名>`，也就是扁平佈局的預設專案。

適用檔名：`product-context.md`、`sdet-config.yaml`、`test-style.md`、`ci-backend-github-actions.md`、`issue-tracker-github.md`、`issue-tracker-local-md.md`。

**例外：`config/governance.yaml` 永遠在 `config/` 根目錄**，不跟著 project 走。它是跨專案共用的授權分級表。

## 鐵則

- 當某個解析失敗的話，就終止目前的動作，不能去讀取別組 config。charter 寫了 `project: shopnow` 但 `config/shopnow/product-context.md` 不存在時，回報「專案 shopnow 的設定不存在，請先跑 `setup-sdet`」，**不得改讀扁平的 `config/product-context.md`**。回退的後果是拿 A 產品的 base URL 與帳號去打 B 產品，證據全錯而且看起來很正常。
- **第一次讀就覆誦。** 讀到某個專案的 `product-context.md` 後，在輸出裡覆誦一次讀回的 base URL 與 slug。覆誦不出來代表讀錯專案或路徑寫錯，當場攔下。
- **slug 兩邊一致。** `config/<project>/` 與 `knowledge/<project>/` 用同一個 slug，不另外維護對照表。`knowledge/` 由人工維護。
- **往下傳，不重解析。** 探索與 agents 全鏈沿用同一 project。候選、盲驗輸入、verdict、gate 與分派都帶 `project`、`session`、`finding_id`，格式見 `references/agent-handoff.md`。設定路徑由 project 推得，不接受資料包另指定其他專案的設定。
- **一次性探索不必有 project。** charter 不填 `project`、自己帶 `target` URL 時，不必讀 product-context 取得網址；agents 的預算、門檻與後端仍讀扁平 `config/`。不得把 target URL 當成 Issue repository。
- **後端只在解析後的目錄選。** 有已設定 repository 的 `issue-tracker-github.md` 就用 GitHub；該檔不存在且有 `issue-tracker-local-md.md` 才用本地。GitHub 設定不完整或未登入時停手，不回退到本地或其他專案。對外指令明確指定設定中的 repository，label 也讀該設定；PR 目標另核對產品 repo。

## 目前接線範圍

已接：`exploration-charter`、`explore`、`api-evidence`、`test-oracle`、`agents/` 全部六支 skill。

尚未接：`maintain/`、`infra/`、`workflow/` 各 skill 仍寫死扁平路徑，等它們真的要跑多專案時再照這份接。單一專案的扁平佈局不受影響。
