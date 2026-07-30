# sdet-skills — 專案規則

Agentic SDET 技能組：GitHub Actions · Playwright (TypeScript) · GitHub Issues。
一套可重用的 skill，讓 agent 探索找 bug、驗證回報、修產品、顧測試與整條 CI 生產線。

## 四層心智模型（把「能力」和「產品/專案」分乾淨）
- **能力（how）** → `skills/`，產品無關、可重用。
- **事實（what）** → `knowledge/`，受測產品專屬。
- **流程（process）** → `skills/workflow/`，團隊/SDLC 專屬（仍是 skill，但讀 knowledge + 專案設定）。
- **規則與設定** → `config/`，環境專屬，祕密走 env。
- 鐵則：**產品知識與專案設定是「輸入」，skill 讀它、不內嵌**，否則 reuse 就死了。詳見 `architecture/sdet-skills-architecture.md`。

## Skill 分層（bucket）
- `foundation/` — 開工設定與後端抽象層
- `observe/`    — 觀察與留證（截圖/console/network/結構化結果/異常分類）
- `explore/`    — 自主探索（charter/探索迴圈/test oracle）
- `agents/`     — 代理人：找 bug、獨立驗證、品質閘、開單、修產品、值班
- `maintain/`   — 測試維護「一支」層級：寫測試、根因分析、修測試、重跑到綠、減法
- `infra/`      — CI Pipeline 與 Testing Infra「一批」層級：建 pipeline、平行、環境、讀 run、批次 triage、flaky 治理、放行閘、觀測
- `economics/`  — 成本治理（風險路由 + 成本 reference）
- `workflow/`   — 專案活動（**預留，骨架**）：測試規劃、覆蓋追溯、狀態回報、release 放行，把 SDET 接進團隊/SDLC
- `meta/`       — 路由（ask-sdet）

**「一筆 vs 一批」原則：** `maintain/` 處理一支測試/一次失敗；`infra/` 處理整批（幾百支、一片紅、跨 run 趨勢）。同名能力（如 failure-analysis vs pipeline-triage、flaky-detect vs flaky-manager）在兩層不是重複，是規模升級。一批必須先 fan-in 合併根因再分析。

## 每支 skill 的規範
- 一定要有 `SKILL.md` 與 `agents/openai.yaml`。
- 宣告 invocation：user-invoked（`disable-model-invocation: true` + openai.yaml `policy.allow_implicit_invocation: false`）或 model-invoked（兩者都省略）。
- 後端相依（GitHub / 網址 / 帳密）不寫死在 SKILL.md，放 `config/`；產品知識放 `knowledge/`；祕密只用環境變數。
- SKILL.md 保持短（祈使句），rationale 放 `docs/`。
- 副作用動作（開 issue/PR、改測試、reset env、release 放行）一律先確認，並受 `config/governance.yaml` 授權分級管制。
- skill 之間用「skill 名稱」互相指涉（如「交給 test-oracle」），不要用外部章節/週次。
- 新增/改名/改行為的 skill，要同步更新 `README.md`、`.claude-plugin/plugin.json`、`meta/ask-sdet`。
- 中文行文照 de-ai-tone：標點全形、破折號只當插入語、不用中國用語與空轉話語標記。CI 跑 `scripts/check-de-ai-tone.py` 擋，本機可先跑一次。

## 產品知識與資料
- `knowledge/` — 受測產品的「事實」（產品專屬，是 `test-oracle` 的規格判準來源）；skill 讀它、不內嵌。真檔 gitignore，只 commit 範本（`*.example.md`）。依規模分層：單檔 → `domains/` 多檔 → RAG/MCP。
- 跨 skill 的資料流檔（charters/、findings/、output/verdicts/、output/issues-index.yaml、output/runs/…）見 `docs/state-files.md`。
