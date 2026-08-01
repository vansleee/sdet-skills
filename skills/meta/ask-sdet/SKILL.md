---
name: ask-sdet
description: 不知道該用哪支 SDET skill 或走哪條流程時，問我。這是所有 user-invoked skill 的路由器：說出你想做的事，我告訴你用哪個、以及它前後接什麼。
disable-model-invocation: true
---

# Ask SDET

說出你想做的事，我幫你對到正確的 skill 或流程。設計理念見 `docs/meta/ask-sdet.md`。

> 只列「你要自己打」的 user-invoked 入口。其餘 model-invoked skill（evidence-package、explore、bug-hunter、triage、failure-analysis…）agent 遇到對的任務會自己觸發，不用你記；你想手動指定時照樣可以直接打名字。

## 你想做什麼 → 用哪支
| 你的情境 | 打這個 |
|---|---|
| 新 repo 還沒設定 / 要換工具、改門檻 | `/setup-sdet` |
| 要讓同事自主探索找 bug：先定目標與邊界 | `/exploration-charter` |
| 要牠排程獨立值班（獵→驗→閘→開單→開 PR 跑一輪） | `/duty-oncall` |
| 把一次成功探索固化成自動化測試（畫面）| `/test-author` |
| 要把一條後端規則、驗證或權限固化成 API 測試 | `/api-test-author` |
| 要判「這個 build 能不能 merge / 放行」 | `/quality-gate` |
| 要判「這一版能不能出」並留簽核紀錄 | `/release-signoff` |
| 不知道用哪個 | `/ask-sdet`（就是我） |

## 主要流程（誰接誰）
**找新 bug**：`/exploration-charter` 定目標 → bug-hunter 打獵（自動用 explore／evidence-package／test-oracle）→ bug-verifier 獨立重現 → issue-quality-gate 把關 → triage 開單 → bug-fixer 開 PR（人 merge）。整條要一次跑完，打 `/duty-oncall`。

**顧測試**：`/test-author`（畫面）或 `/api-test-author`（端點）寫測試 → 進 CI 跑 → 紅了 failure-analysis 分析 → test-heal 修測試 → re-run-gate 重跑到綠

**該用哪一層**：規則、計算、驗證、權限 → API；呈現、互動、可及性 → UI；不確定就先問 `route-by-risk`，判準見 `references/test-design.md` 第 0 節。留證同理：經畫面走 evidence-package，直接打端點走 api-evidence。

**顧產線**：route-by-risk 決定跑什麼 → ci-pipeline 建 pipeline（掛 test-env／test-parallelize）→ pipeline-read 讀 run → pipeline-triage 合併根因+派工 → flaky-manager 治理 flaky → `/quality-gate` 判放行 → pipeline-observability 算指標，把超標的路由回上游

**接團隊**：test-planning 圈範圍+排風險 →（`/exploration-charter` 探索／`/test-author` 固化）→ traceability 對覆蓋、把 gap 回饋下一輪 → status-report 回報 → `/release-signoff` 判這版能不能出

**三層閘門**（各管一層，上層吃下層產物）：issue-quality-gate（一張單能不能開）→ `/quality-gate`（一個 build 能不能放行）→ `/release-signoff`（一版 release 能不能簽）

**串起來**：`/duty-oncall` 在授權（`config/governance.yaml`）內把上面整條排程跑完。

## 維護規則
新增／改名／移除任一 user-invoked skill，或改了它在流程裡的位置，就要回來更新這張表。過時的路由器會騙人。
