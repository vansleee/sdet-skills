# sdet-skills 架構

一套**可重用**的 Agentic SDET 技能組（GitHub Actions · Playwright · GitHub Issues）。核心設計原則：把「能力」和「產品／專案」分乾淨，換一個產品時 skill 不用改。

## 四層心智模型

一個真正的 SDET 同事，不是只有「能力」就夠——他還得「知道產品」和「參與專案」。所以把四種東西分開，彼此是「讀取」關係，不互相寫死：

| 層 | 是什麼 | 放哪 | 特性 |
|---|---|---|---|
| **能力（how）** | 怎麼做一件事 | `skills/` | 產品無關、可重用 |
| **事實（what）** | 受測產品是什麼 | `knowledge/` | 產品專屬 |
| **流程（process）** | 怎麼接進團隊 / SDLC | `skills/project/` | 團隊/專案專屬（仍是 skill，但讀 knowledge + 專案設定） |
| **規則與設定** | 後端、授權、參數 | `config/` | 環境專屬；祕密走 env |

> 鐵則：`skills/` 保持產品無關；產品知識與專案設定是**輸入**，skill 去讀，不內嵌。一旦把產品知識塞進 skill，reuse 就死了。

## Skill bucket 總表

| bucket | 負責 | 代表 skill |
|---|---|---|
| `foundation/` | 開工設定與抽象層 | setup-sdet、product-context(ref) |
| `observe/` | 觀察與留證 | evidence-package、structured-result、classify-anomaly |
| `explore/` | 自主探索 | exploration-charter、explore、test-oracle |
| `agents/` | 代理人與治理 | bug-hunter、bug-verifier、issue-quality-gate、triage、bug-fixer、duty-oncall |
| `maintain/` | 測試維護「一支」層級 | test-author、failure-analysis、test-heal、re-run-gate… |
| `infra/` | CI 與 Testing Infra「一批」層級 | ci-pipeline、pipeline-triage、flaky-manager、quality-gate… |
| `economics/` | 成本治理 | route-by-risk、sdet-economics(ref) |
| `project/` | **專案活動（預留，骨架）** | test-planning、traceability、status-report、release-signoff |
| `meta/` | 路由 | ask-sdet |

**「一筆 vs 一批」：** `maintain/` 修一支測試 / 一次失敗；`infra/` 顧整批（幾百支、一片紅、跨 run 趨勢）。同名能力在兩層不是重複，是規模升級。

## `knowledge/` — 產品知識，依規模分層

skill 讀它、不內嵌。它也是 `test-oracle` 的**規格 oracle 來源**：購物 demo 靠「內部一致性 / API↔UI」這類不需規格的 oracle 就夠；公司產品很多對錯只有規格說得準，那份規格就住在這裡。

1. **小** → 一份 `product-overview.md`
2. **中** → `domains/<module>.md` 每模組一份，progressive disclosure
3. **大 / 會變** → RAG 檢索或 MCP resource 指向活文件，避免過期

真檔 gitignore，只 commit `*.example.md` 範本。

## `project/` — 專案活動（預留中）

把 SDET 從「跑測試」延伸到「參與測試生命週期」。目前為骨架，逐一實作：

- **test-planning**：ticket / PRD → 測試範圍 + 風險（可續轉 charter）
- **traceability**：需求 ↔ 測試 ↔ finding 覆蓋對照，找 gap
- **status-report**：standup / 測試報告 / release-readiness 摘要
- **release-signoff**：整個 release 能不能出的專案層級放行

閘門三層，別混：`issue-quality-gate`（單張 issue）< `infra/quality-gate`（pipeline 放行）< `project/release-signoff`（整個 release 對需求/風險簽核）。

## 資料流

```
knowledge/               產品事實(規格 oracle 來源)
charters/<slug>.yaml     人設定目標與邊界(可由 test-planning 產生)
  └─> findings/F-*.yaml     explore 候選發現(含 oracle 判定)
        └─> verdicts/V-*.yaml   bug-verifier 獨立重現 + confidence
              └─> gate.yaml         可重現?去重?非 FP?
                    └─> GitHub Issue → PR(人 merge)
                          └─> tests/*.spec.ts → CI run → runs/<date>.yaml(算帳)
```

跨 skill 的狀態檔慣例見 `docs/state-files.md`。`results.yaml`（六狀態）貫穿各週，各處不得自創狀態詞彙。
