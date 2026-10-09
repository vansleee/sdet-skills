# meta/

`skills/meta/` 每支 skill 的設計理由。執行指令在各自的 `SKILL.md`，這裡只寫為什麼。

## ask-sdet

SDET 的共同入口，負責需求辨識、設定銜接與流程路由。

### 為什麼合併入口

新讀者通常先知道自己想做什麼，還不知道應該先設定或呼叫哪支 skill。ask-sdet 先分辨意圖與必要前置條件，缺設定時接入 setup-sdet，完成後回到原任務，使用者不必在兩個入口間重述需求。

setup-sdet 保留直接入口，讓既有文章與熟悉設定流程的使用者繼續使用。兩支 skill 同屬 `meta/`，名稱與 user-invoked 宣告保留；設定清單、寫入確認與讀回驗收只維護在 setup-sdet。

### 執行邊界

| 情境 | 行為 |
| --- | --- |
| 只問有哪些能力或該用哪支 | 回答建議，不啟動設定 |
| 明確要求設定或修改設定 | 讀取 setup-sdet，接入同一份流程 |
| 要執行任務且設定足夠 | 依任務授權與所選 skill 接續 |
| 必要設定缺漏但未要求修改 | 說明缺漏，確認要補設定後再訪談 |
| 具名 project 缺檔或流程尚未支援多專案 | 停手核對，不回退到預設產品 |
| 設定讀回驗收失敗 | 列出阻礙，不接續依賴該設定的工作 |

寫入確認保留在 setup-sdet。ask-sdet 的使用者呼叫只表示進入共同入口，不能當成任意修改 config、開單或改碼的授權。

### 維護

新增、改名或改變入口時同步路由表。變更設定流程時只改 setup-sdet 與其設計文件；ask-sdet 維護接入條件、原任務與返回方式，避免兩套設定邏輯逐漸分歧。

## setup-sdet

一次性設定：訪談受測產品、登入、CI、issue tracker、Playwright、門檻，產出所有其他 skill 讀取的 `config/`。多專案時，每個專案一份，路徑前綴 `config/<project>/`。

### 產出檔案與負責範圍

| 檔案 | 負責範圍 | 誰讀它 |
|---|---|---|
| `product-context.md` | base URL（各環境）、登入方式（storageState / `env:VAR`）、Playwright config/testDir/reporter 路徑、trace 來源、API（base URL、認證方式、契約來源、API testDir、速率限制、不得碰的端點）| `explore`、`evidence-package`、`bug-hunter` 等所有要開瀏覽器的 skill；API 段由 `api-evidence`、`api-test-author`、`test-oracle` 讀 |
| `ci-backend-github-actions.md` | 怎麼用 `gh` 讀 CI run、拿 artifact/annotation | `pipeline-read`、`pipeline-triage` |
| `issue-tracker-github.md` | 有 GitHub issue repo 時：repo、triage label、canonical→實際 label 對應 | `triage`、`issue-quality-gate` |
| `issue-tracker-local-md.md` | 還沒有 GitHub issue repo 時的本地備援：開單改記 `output/reports/issues/*.md` | `triage`、`issue-quality-gate` |
| `sdet-config.yaml` | confidence / dedupe / budget / models（cheap/strong）/ risk 權重等門檻 | `bug-verifier`、`issue-quality-gate`、`route-by-risk` |

`config/governance.yaml` 不在上表——這份是跨專案共用的授權分級表，放 `config/` 根目錄，由需要副作用的 skill（`triage`、`bug-fixer`、`test-heal`…）沿途寫入/參照，不是這支 skill 的訪談輸出。

### 專案（project）是什麼

一個 project 對應一個「常態要走完整 agents 鏈（`explore` → `bug-hunter` → `bug-verifier` → `issue-quality-gate` → `triage` → `bug-fixer`）的受測產品」，slug 用小寫連字號（如 `toolshop`）。一次性探索（練習站、demo 站）不需要建 project，charter 自己帶 target URL 就夠，見 `exploration-charter`。

`knowledge/<project>/` 用同一個 slug，讓「怎麼連上產品」（`config/`）跟「產品是什麼」（`knowledge/`）對得上同一個專案，不必另外維護對照表。`knowledge/` 目前由人工維護，這支 skill 不寫入，只在收尾提醒兩邊 slug 是否一致。

只有一個常態受測產品時，沿用既有扁平佈局（`config/product-context.md` 等，不建子目錄），視為預設專案。第二個常態受測產品出現時才切換成 `config/<project>/`，既有的扁平檔案留著當遺留的預設專案，不強迫搬遷。

多專案要接 charter 時，charter 用 `project: <slug>` 欄位指向要讀哪組 `config/<project>/`、`knowledge/<project>/`。這條約定由本 skill 定義，解析規則寫在 `references/config-resolution.md`，`exploration-charter` 訪談時問、`explore` 開跑前解析，`api-evidence`、`test-oracle`、`bug-hunter` 沿用同一個 slug。`maintain/`、`infra/`、`workflow/` 各 skill 尚未接，仍讀扁平路徑。`test-author`、`api-test-author` 與 `test-heal` 的風格檔也讀 `config/test-style.md`；不能把其他專案的風格檔搭配預設產品設定。這三支收到具名 project 時先停手核對，不會自動回退。

### 範例：怎麼用

新增一個叫 `shopnow` 的第二個專案：

    /setup-sdet
    > 專案 slug：shopnow
    > （依序回答訪談：base URL、登入、CI、issue tracker、Playwright、門檻）

跑完產生：

    config/shopnow/product-context.md
    config/shopnow/ci-backend-github-actions.md
    config/shopnow/issue-tracker-github.md
    config/shopnow/sdet-config.yaml

之後要打這個專案的 charter 這樣寫：

    charter:
      project: shopnow
      goal: ...

`explore` 執行時讀 charter 的 `project` 欄位，組出路徑 `config/shopnow/product-context.md` 取得 base URL 與登入方式；charter 沒填 `project` 時，維持原行為——target URL 由 charter 自己帶，不查 `config/`。

### 驗證工具是否已安裝

- **Playwright MCP**：確認 MCP client（如 `claude mcp list`）裡有 `playwright` 且能連；不確定就實際跑一次 snapshot 動作試探，不要只看設定檔存在。
- **`playwright-cli`**：跑 `playwright-cli --version`；沒有就 `npm install -g @playwright/cli@latest`，再跑 `playwright-cli install --skills` 補齊技能包。
- **`gh`（GitHub CLI）**：跑 `gh auth status`；沒登入就無法產出可用的 `ci-backend-github-actions.md`、`issue-tracker-github.md`，設定收尾時列為必填缺漏，不能算完成。

### 驗證 AI 有讀到產生出來的 config

寫檔不等於之後讀得到。收尾時要求 agent 重新 `Read` 一次剛寫入的 `config/<project>/*`（不是複誦訪談時使用者講過的答案），在摘要裡逐項覆誦讀回的值。覆誦不出來，代表寫檔路徑、專案 slug 或檔名有誤，當場攔下重寫，不能算設定完成。日後其他 skill 第一次讀某個 `config/<project>/` 檔案時，也建議照同一個模式先覆誦一次讀到的值，確認沒有讀錯專案。

### 設計理念（為什麼這樣設計）

- **後端可替換。** skill 內文只寫「file to the issue tracker」「讀 CI run」，實際指令放 `config/`。這是從 Jenkins/JIRA 遷到 GitHub Actions/Issues 不必重寫邏輯的關鍵。
- **祕密不落地。** 帳密/token 只記變數名（`env:VAR`），不記值、不在對話裡索取。把安全變成機制，不靠自律。
- **user-invoked。** 設定是有後果的動作，使用者可直接打 `/setup-sdet`，或在 `/ask-sdet` 明確要求設定後接入（`disable-model-invocation: true`）。純諮詢不啟動設定，寫檔前仍列出具體內容確認。
- **一次一個主題、可重複執行。** 不一次丟六段表單；重跑時先讀現有 config、只問缺的。
- **開工前先驗 trace 能力。** 讓「跑完才發現沒 trace」提前到設定階段就攔下。
- **API 是另一個介面層，不是另一個產品。** 所以它是 `product-context.md` 裡的一段，不是另一個 project slug。契約來源填「無」也是有效答案，它讓下游知道 contract oracle 不可用、要降級成狀態碼語意與一致性判準，而不是讓下游自己去猜有沒有 spec。
- **專案隔離。** `config/` 與 `knowledge/` 用同一組 `<project>` slug 分資料夾，同一個 repo 能同時養多個常態受測產品，不會因為只有一份扁平 `product-context.md` 就互相覆蓋。一次性探索（charter 不填 `project`）不受影響，照舊直接帶 target URL。
