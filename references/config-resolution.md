# Config 解析規則（專案資料夾）

每個受測產品一個資料夾 `projects/<project>/`，所有讀設定、產品知識或 charter 的 skill 都照這份解析，不能各自寫另一套路徑邏輯。設定怎麼產生見 setup-sdet。

## 佈局

```
projects/
  governance.yaml          # 跨專案共用的授權分級表
  _template/               # 新專案範本（進版控）
  <project>/
    config/                # 怎麼連上產品：product-context.md、sdet-config.yaml、test-style.md、
                           #   ci-backend-github-actions.md、issue-tracker-github.md / issue-tracker-local-md.md
    knowledge/             # 產品是什麼：product-overview.md 或 domains/<area>.md
    charters/              # 探索章程（進版控）
```

`config/` 與 `knowledge/` 是真檔，不進版控；`_template/` 與各專案的 `charters/` 進版控。

## 解析 project

依序取第一個有值的來源：

1. 呼叫端明講的 `project`。
2. 收到的交接資料包的 `project`。
3. charter 所在的資料夾：`projects/<project>/charters/<slug>.yaml`。charter 裡若另寫 `project` 欄位，必須和資料夾一致。
4. 都沒有：`projects/` 底下只有一個專案有 `config/product-context.md` 就用它；有多個就停手問使用者，不要猜。

來源之間互相衝突就停手核對，不在同一 finding 中途切換專案。`project` 一定是 slug，沒有「預設專案」或 `null`。

## 鐵則

- **路徑只有一條。** 設定是 `projects/<project>/config/<檔名>`，知識是 `projects/<project>/knowledge/`，授權分級是 `projects/governance.yaml`。
- **缺檔就停，不回退。** `projects/shopnow/config/product-context.md` 不存在時，回報「專案 shopnow 的設定不存在，請先跑 `setup-sdet`」，**不得改讀其他專案或 `_template/`**。回退的後果是拿 A 產品的 base URL 與帳號去打 B 產品，證據全錯而且看起來很正常。
- **第一次讀就覆誦。** 讀到 `product-context.md` 後，在輸出裡覆誦一次 slug 與 base URL。覆誦不出來代表讀錯專案或路徑寫錯，當場攔下。
- **往下傳，不重解析。** 探索與 agents 全鏈沿用同一 project。候選、盲驗輸入、verdict、gate 與分派都帶 `project`、`session`、`finding_id`，格式見 `references/agent-handoff.md`。設定路徑由 project 推得，不接受資料包另指定其他路徑。
- **沒有 `config/` 的專案只能探索。** 練習站、demo 站可以只有 `charters/`：`explore` 用 charter 的 `target` 與 `max_steps` 跑。要走 agents 鏈（門檻、預算、issue tracker）或 `maintain/`、`infra/`、`workflow/`，先跑 `setup-sdet` 建 `config/`。不得把 target URL 當成 Issue repository。
- **後端只在該專案的 `config/` 裡選。** 有已設定 repository 的 `issue-tracker-github.md` 就用 GitHub；該檔不存在且有 `issue-tracker-local-md.md` 才用本地。GitHub 設定不完整或未登入時停手，不回退到本地或其他專案。對外指令明確指定設定中的 repository，label 也讀該設定；PR 目標另核對產品 repo。
