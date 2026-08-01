# sdet-skills 架構

這是一套**可以重複使用的 SDET 的技能包**，主要涵蓋（GitHub Actions · Playwright MCP/CLI · GitHub Issues）。它的核心設計原則：是讓 AI 能夠執行探索產品 Bug 和撰寫自動化測試的能力。

## 心智模型

作為一個 QA/SDET 的同事，除了擁有相關的技能以外，同時還需要知道產品的知識與專案流程，在這個 sdet-skilss 裡面，將其獨立分層並且能夠互相存取對方的知識。


| 名稱                | 說明             | 檔案位置               | 備註                                       |
| ----------------- | -------------- | ------------------ | ---------------------------------------- |
| **技能（how）**       | 描述如何做某件事       | `skills/`          | 與產品知識無關，主要是將 SDET 的技能包裝起來，可以重複使用在不同的專案裡。 |
| **產品知識（what）**    | 測試產品知識         | `knowledge/`       | 產品專屬的知識或流程                               |
| **專案流程（process）** | 串接專案的流程與管理     | `skills/workflow/` | 主要是與專案有關，包含整個專案開發流程或事件                   |
| **規範與設定**         | 後端設定、授權規範、其他參數 | `config/`          | 規定需要遵守的規範和其他需要的設定                        |


> 原則：`skills/` 裡的設計必須與產品無關，當需要產品知識或專案設定都是由 skill 去讀 `knowledge/` 或 `config/`，並且不將資料放置在 skills，保持 skills 可以使用在其他專案的狀態。

## Skill bucket 總表


| 資料夾           | 負責                    | 技能                                                                      |
| ------------- | --------------------- | ----------------------------------------------------------------------- |
| `foundation/` | 初始設定與產品背景知識           | setup-sdet、product-context(ref)                                         |
| `observe/`    | 用來觀察測試產品與留下相關證據       | evidence-package、api-evidence、structured-result、classify-anomaly       |
| `explore/`    | 自主探索產品                | exploration-charter、explore、test-oracle                                 |
| `agents/`     | 能夠自行探索、驗證問題、並且開立票     | bug-hunter、bug-verifier、issue-quality-gate、triage、bug-fixer、duty-oncall |
| `maintain/`   | 用來維護測試程式碼             | test-author、api-test-author、failure-analysis、test-heal、re-run-gate…    |
| `infra/`      | 用來維護測試的 CI 與測試的 infra | ci-pipeline、pipeline-triage、flaky-manager、quality-gate…                 |
| `economics/`  | 用來管理使用的 token         | route-by-risk、sdet-economics(ref)                                       |
| `workflow/`   | 專案相關的流程               | test-planning、traceability、status-report、release-signoff                |
| `meta/`       | 用來詢問如何使用 sdet-skills  | ask-sdet                                                                |


`maintain/` 主要是維護測試程式碼的撰寫、執行、並且修復失敗的測試案例，`infra/` 則是針對 CI 上面的錯誤進行分析、執行 pipeline 和相關活動。

## 介面層：畫面與端點

同一個 bucket 裡有些 skill 是成對的，差別在被測的介面層：留證有 `evidence-package`（畫面）與 `api-evidence`（端點），寫測試有 `test-author` 與 `api-test-author`。成對的理由是**手段完全不同**：一邊靠 snapshot 與截圖，一邊靠請求與回應；一邊講定位器與 web-first assertion，一邊講 schema 斷言與狀態碼語意。硬合成一支，紀律就會退化成「看情況適用」。

反過來，判定與分類**不成對**：`test-oracle` 與 `failure-analysis` 各自多一張 API 專屬的表就夠了，因為它們的流程一模一樣，只是判準多幾條。這條界線就是新增 skill 的門檻：**手段不同才開新的，判準不同只加一張表。**

哪一條規則該在哪一層驗，判準在 `references/test-design.md` 第 0 節；覆蓋對照用 `level: api|ui` 記在 `output/traceability.yaml`。

## `knowledge/` — 依照規模的大小，分層產品知識

主要是使用 skill 讀取相關知識，這也 `test-oracle` 的**規格 oracle 來源**，例如：購物網站 ，並不需規格的 oracle 說明；但如果公司的產品，就必須根據規格才能判斷是否有 Bug，我們可以把產品規格定義在 `knowledge/`，我們可以根據規格書的大小，分為下列三種：

1. **小型：只需要建立** 一份 `product-overview.md`
2. **中型**：根據模組或是功能分類在 `domains` 下面，並且每個模組一份 `domains/<module>.md` 每模組一份，根據漸進式揭露（progressive disclosure）相關的知識
3. **大型 / 易於變動** ：使用 RAG 檢索或 MCP resource 指向活文件（live document)，避免文件過期與增加維護成本。

> 這些檔案不需要 commit，只需要 commit `*.example.md` 範立，記得新增對應的檔案，需要將檔案增加到 gitignore 清單中，

## `workflow/` — 專案活動

主要是串接團隊或是產品開發流程的 skills，目前提供下列幾種 skills

- **test-planning**：將 JIRA/Linear Ticket / PRD 轉換成測試範圍和評估測試的風險，主要支援可以轉 charter 格式使用。
- **traceability**：分析需求並且轉換成測試需要的格式，並且根據 finding 找出可能的 gap
- **status-report**：standup / 測試報告 / release-readiness 摘要
- **release-signoff**：檢查是否這次 release 能不能通過驗收標準

總共會有三個閘門，每個閘門都需要獨立通過：`issue-quality-gate`（單張 issue）&lt; `infra/quality-gate`（pipeline 放行）&lt; `workflow/release-signoff`（整個 release 對需求/風險驗收）。

## 資料流

```
knowledge/               產品知識與規格
charters/<slug>.yaml     由人設定目標與邊界（可由 test-planning 產生）
  └─> output/sessions/<date>_<slug>
        └─> /findings/F-*.yaml   explore 發現可能的 bug 與問題（包含 oracle 判斷）
        └─> /verdicts/V-*.yaml   使用 bug-verifier 能夠獨立重現並且增加信心指數
              └─> /gate.yaml     是否可以重現？移除重複的 Bug？
                    └─> GitHub Issue → PR（並需要由人決定是否能夠合併 PR）
        └─> /runs/<date>.yaml
tests/*.spec.ts          使用 test-author（畫面）或 api-test-author（端點）撰寫的測試程式碼，用來執行迴歸測試(Regression Testing)
  └─> 使用 CI run 或是 Local 機器執行
```

session 資料夾一輪一個，裝的是「這一輪的判斷」；跨輪累積的登錄簿（`output/issues-index.yaml`、`output/calibration.yaml`、`output/known-false-positives.yaml`、`output/flaky-registry.yaml`）留在 `output/` 根，切進單輪就失去去重與校準的能力。完整清單見 `docs/state-files.md`。

> 需要跨 skill 的狀態檔規範可以參考 `docs/state-files.md`。`results.yaml`（skill 會有各自的狀態）並貫穿其他 skill，記得不可以自己新創狀態相關的詞彙。

