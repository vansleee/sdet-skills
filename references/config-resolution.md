# Config 解析規則（多專案）

可以同時支援多個待測試的產品，而這份定義主要是用來判斷要讀取哪一組 config。所有需要讀取的 config 的 skill 都需要 follow 這條規則，不能各自撰寫另外一套路徑的邏輯。相關設定怎麼產生可以參考 setup-sdet。

## 解析

1. 取 `project` slug，來源依序：呼叫端明講的 `project` → charter 的 `charter.project` 欄位 → 無。
2. 有 slug → 路徑是 `config/<project>/<檔名>`。
3. 沒有 slug → 路徑是 `config/<檔名>`，也就是扁平佈局的預設專案。

適用檔名：`product-context.md`、`sdet-config.yaml`、`ci-backend-github-actions.md`、`issue-tracker-github.md`、`issue-tracker-local-md.md`。

**例外：`config/governance.yaml` 永遠在 `config/` 根目錄**，不跟著 project 走。它是跨專案共用的授權分級表。

## 鐵則

- 當某個解析失敗的話，就終止目前的動作，不能去讀取別組 config。charter 寫了 `project: shopnow` 但 `config/shopnow/product-context.md` 不存在時，回報「專案 shopnow 的設定不存在，請先跑 `setup-sdet`」，**不得改讀扁平的 `config/product-context.md`**。回退的後果是拿 A 產品的 base URL 與帳號去打 B 產品，證據全錯而且看起來很正常。
- **第一次讀就覆誦。** 讀到某個專案的 `product-context.md` 後，在輸出裡覆誦一次讀回的 base URL 與 slug。覆誦不出來代表讀錯專案或路徑寫錯，當場攔下。
- **slug 兩邊一致。** `config/<project>/` 與 `knowledge/<project>/` 用同一個 slug，不另外維護對照表。`knowledge/` 由人工維護。
- **往下傳，不重解析。** 一條鏈上（`explore` → `evidence-package` / `api-evidence` / `test-oracle`）由最上游解析一次，把 slug 傳給下游；下游拿到就用，拿不到才自己照上面第 1 步解析。
- **一次性探索不必有 project。** charter 不填 `project`、自己帶 `target` URL 的練習站探索，照舊直接跑，不查 `config/`。

## 目前接線範圍

已接：`exploration-charter`、`explore`、`api-evidence`、`test-oracle`、`bug-hunter`。

尚未接：`maintain/`、`infra/`、`workflow/` 各 skill 仍寫死扁平路徑，等它們真的要跑多專案時再照這份接。單一專案的扁平佈局不受影響。
