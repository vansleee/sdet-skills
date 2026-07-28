---
name: ci-pipeline
description: 用 GitHub Actions 建/改測試 pipeline：產 workflow、掛分片與環境、上傳 report/trace artifact。要把測試接進 CI、改觸發時機、修 artifact 設定時使用。關鍵詞：CI、pipeline、GitHub Actions、workflow、artifact、trace、接進 CI。
disable-model-invocation: true
---

# CI Pipeline

輸入一個 repo 的測試設定，輸出可用的 GitHub Actions workflow：跑測試、留證據、把 artifact 命名成下游讀得懂的樣子。infra 迴圈的**產生端**。設計理念見 `docs/infra/ci-pipeline.md`。

## 輸入 / 輸出
- **輸入**：repo（測試框架設定，如 `playwright.config.ts`）、觸發時機（PR / nightly / manual）、可選的 `route-by-risk` 範圍決定、可選的時限目標。
- **輸出**：`.github/workflows/<name>.yml`（先給 diff、人確認才寫）＋ artifact 命名契約說明。

## 步驟
1. **盤點**：讀 `playwright.config.ts` / `package.json` 取測試指令、reporter、專案矩陣；讀 `config/sdet-config.yaml` 取門檻與預算。缺什麼就問，不臆測。
2. **決定觸發**：PR（必跑、要快）、nightly（全量）、`workflow_dispatch`（手動重跑）。三者可並存於同一檔的不同 job。
3. **接風險閘**：把 `route-by-risk` 放在最前面當 job——它的 `must-test` / `sample` / `skip` 決定本輪跑什麼。PR 觸發預設吃 `must-test` + `sample`，nightly 跑全量。
4. **產 workflow**：checkout → setup-node（含 `cache: npm`）→ `npm ci` → `npx playwright install --with-deps`（快取瀏覽器）→ 跑測試 → 上傳 artifact。
5. **掛可選層**：需要分片交 `test-parallelize`（產 matrix + merge-reports job）；需要 seeding / ephemeral env 交 `test-env`（產前置與 teardown step）。本 skill 只留掛載點，不自己發明分片或環境邏輯。
6. **設 artifact**（**契約，見下**）：`if: always()` 上傳 report；trace 只在失敗時留。
7. **確認再寫**：把 workflow diff 完整列給使用者，得同意才寫檔。

## Artifact 命名契約（與 `pipeline-read` 共用）

下游一切分析都靠這幾個名字找檔案。**改名等於改 API，兩邊要一起改**。

| artifact 名 | 內容 | 上傳條件 | 誰讀 |
|---|---|---|---|
| `playwright-report` | HTML report | `if: always()` | `pipeline-read` / 人 |
| `test-results-json` | JSON / junit reporter 輸出 | `if: always()` | `pipeline-read`（解析失敗清單）|
| `traces` | `test-results/**/trace.zip` | `if: failure()` | `failure-analysis` / `evidence-package` |
| `blob-report-<shard>` | 分片的 blob report | `if: always()` | `test-parallelize` 的 merge job |

保留天數讀 `config/sdet-config.yaml` 的 `ci.artifact_retention_days`（預設 7；trace 佔空間，別無腦設 90）。

## 鐵則
- **trace 只留失敗**（`if: failure()`）。全留很快就把 storage 吃爆，且沒人看綠燈的 trace。
- **artifact 名是契約**，不是隨手命名；改名要同步 `pipeline-read` 與本表。
- **祕密只走 GitHub secrets / env**（`${{ secrets.* }}`），不寫死在 workflow、不寫進 SKILL.md、不進 `knowledge/`。
- **`if: always()` 不能省**——測試紅了才最需要報告，紅了就不上傳等於把證據丟掉。
- **改 workflow 是副作用**：先列 diff 給人確認，受 `config/governance.yaml` 管制。
- 本 skill 只建/改 pipeline。讀 run 是 `pipeline-read`、一片紅是 `pipeline-triage`、放行是 `quality-gate`。

## 輸出（格式，非某次執行結果）
```yaml
# .github/workflows/e2e.yml（節錄）
on:
  pull_request:
  schedule: [{ cron: "0 18 * * *" }]   # nightly 全量
  workflow_dispatch:
jobs:
  e2e:
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
