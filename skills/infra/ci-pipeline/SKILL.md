---
name: ci-pipeline
description: 用 GitHub Actions 建/改測試 pipeline：產 workflow、掛分片與環境、依契約上傳 artifact。使用者要把測試接進 CI、改觸發時機、修 artifact 設定時使用；`test-env` 與 `test-parallelize` 要把自己產的步驟掛進 workflow 時也用。
---

# CI Pipeline

輸入一個 repo 的測試設定，輸出可用的 GitHub Actions workflow：跑測試、留證據、把 artifact 命名成下游讀得懂的樣子。infra 迴圈的**產生端**。設計理念見 `docs/infra/ci-pipeline.md`。

## 輸入 / 輸出
- **輸入**：repo（測試框架設定，如 `playwright.config.ts`）、觸發時機（PR / nightly / manual）、可選的 `route-by-risk` 範圍決定、可選的時限目標。
- **輸出**：`.github/workflows/<name>.yml`（先給 diff、人確認才寫）＋ artifact 命名契約說明。

## 步驟
1. **盤點**：讀 `playwright.config.ts` / `package.json` 取測試指令、reporter、專案矩陣；讀 `config/sdet-config.yaml` 取門檻與預算。缺什麼就問，不臆測。
2. **決定觸發**：PR（必跑、要快）、nightly（全量）、`workflow_dispatch`（手動重跑）。三者可並存於同一檔的不同 job。
3. **接風險閘**：把 `route-by-risk` 放在最前面當 job。它的 `must-test` / `sample` / `skip` 決定本輪跑什麼。PR 觸發預設吃 `must-test` + `sample`，nightly 跑全量。
4. **產 workflow**：checkout → setup-node（含 `cache: npm`）→ `npm ci` → `npx playwright install --with-deps`（快取瀏覽器）→ 跑測試 → 上傳 artifact。
4b. **API 測試分成獨立 job**（`config/product-context.md` 有 API testDir 時）：**不裝瀏覽器**（省掉 `playwright install`，這步通常是整條最慢的），跑得完就先跑，當 PR 的快 lane。UI job 設 `needs: api-test`，讓後端規則的紅燈在幾十秒內先亮，而不是等瀏覽器測試跑完十分鐘才知道。API job 的 artifact 用 `api-test-results-json`，跟 UI 的分開，`pipeline-read` 才解析得出是哪一層紅的。
5. **掛可選層**：需要分片交 `test-parallelize`（產 matrix + merge-reports job）；需要 seeding / ephemeral env 交 `test-env`（產前置與 teardown step）。本 skill 只留掛載點，不自己發明分片或環境邏輯。
6. **設 artifact**：照 `references/artifact-contract.md` 的名稱與上傳條件，一個都別漏。
7. **確認再寫**：把 workflow diff 完整列給使用者，得同意才寫檔。

## 鐵則
- **artifact 名是契約**，不是隨手命名：名稱、上傳條件、保留天數一律照 `references/artifact-contract.md`，改名要連那份表一起改。
- **祕密只走 GitHub secrets / env**（`${{ secrets.* }}`），不寫死在 workflow、不寫進 SKILL.md、不進 `knowledge/`。
- **改 workflow 是副作用**：先列 diff 給人確認，受 `config/governance.yaml` 管制。
- **`needs: api-test` 只用在 PR 觸發**。nightly 要的是完整訊號，兩層都得跑完；掛了依賴，API 一紅整批 UI 會變成 skipped，隔天早上看到的是一份缺一半的報告，而 `quality-gate` 的驗數會把它當成靜默失蹤擋下來。

## 輸出（格式，非某次執行結果）
```yaml
# .github/workflows/e2e.yml（節錄）
on:
  pull_request:
  schedule: [{ cron: "0 18 * * *" }]   # nightly 全量
  workflow_dispatch:
jobs:
  api-test:                              # 快 lane：不裝瀏覽器
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npx playwright test tests/api --reporter=json
        env:
          API_BASE_URL: ${{ secrets.API_BASE_URL }}
          API_TOKEN_USER1: ${{ secrets.API_TOKEN_USER1 }}
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: api-test-results-json, path: results.json, retention-days: 7 }

  e2e:
    needs: api-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test
        env:
          BASE_URL: ${{ secrets.BASE_URL }}
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: playwright-report, path: playwright-report/, retention-days: 7 }
      - uses: actions/upload-artifact@v4
        if: failure()
        with: { name: traces, path: test-results/**/trace.zip, retention-days: 7 }
```

## 上下游
上游：`route-by-risk`（本輪跑什麼）、`setup-sdet`（初始設定）。可選掛載：`test-parallelize`、`test-env`。下游：這支產出的 run 由 `pipeline-read` 讀進來，整條 infra 迴圈才轉得起來。
