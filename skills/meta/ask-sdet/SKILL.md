---
name: ask-sdet
description: 不知道該用哪支 SDET skill 或走哪條流程時，問我。這是所有 user-invoked skill 的路由器：說出你想做的事，我告訴你用哪個、以及它前後接什麼。
disable-model-invocation: true
---

# Ask SDET

說出你想做的事，我幫你對到正確的 skill 或流程。設計理念見 `docs/meta/ask-sdet.md`。

> 只列「你要自己打」的 user-invoked 入口。其餘 model-invoked skill（evidence-package、explore、bug-verifier、failure-analysis…）agent 遇到對的任務會自己觸發，不用你記。

## 你想做什麼 → 用哪支
| 你的情境 | 打這個 |
|---|---|
| 新 repo 還沒設定 / 要換工具、改門檻 | `/setup-sdet` |
| 要讓同事自主探索找 bug：先定目標與邊界 | `/exploration-charter` |
| 發動一次自主找 bug（在選定範圍打獵） | `/bug-hunter` |
| 有個確定的 product-bug，要開成 GitHub Issue | `/triage` |
| 要牠排程獨立值班，把整條 pipeline 跑一輪 | `/duty-oncall` |
| 把一次成功探索固化成自動化測試 | `/test-author` |
| CI 一片紅，要收斂根因、分組派工開單 | `/pipeline-triage` |
| 要把測試接進 GitHub Actions、改觸發時機或 artifact | `/ci-pipeline` |
| 要判「這個 build 能不能 merge / 放行」 | `/quality-gate` |
| 要判「這一版能不能出」並留簽核紀錄 | `/release-signoff` |
| 不知道用哪個 | `/ask-sdet`（就是我） |

## 主要流程（誰接誰）
**找新 bug**：`/exploration-charter` 定目標 → `/bug-hunter` 打獵（自動用 explore／evidence-package／test-oracle）→ bug-verifier 獨立重現 → issue-quality-gate 把關 → `/triage` 開單 → bug-fixer 開 PR（人 merge）

**顧測試**：`/test-author` 寫測試 → 進 CI 跑 → 紅了 failure-analysis 分析 → test-heal 修測試 → re-run-gate 重跑到綠

**顧產線**：route-by-risk 決定跑什麼 → `/ci-pipeline` 建 pipeline（掛 test-env／test-parallelize）→ pipeline-read 讀 run → `/pipeline-triage` 合併根因+派工 → flaky-manager 治理 flaky → `/quality-gate` 判放行 → pipeline-observability 算指標，把超標的路由回上游

**接團隊**：test-planning 圈範圍+排風險 →（`/exploration-charter` 探索／`/test-author` 固化）→ traceability 對覆蓋、把 gap 回饋下一輪 → status-report 回報 → `/release-signoff` 判這版能不能出

**三層閘門**（各管一層，上層吃下層產物）：issue-quality-gate（一張單能不能開）→ `/quality-gate`（一個 build 能不能放行）→ `/release-signoff`（一版 release 能不能簽）

**串起來**：`/duty-oncall` 在授權（`config/governance.yaml`）內把上面整條排程跑完。

## 維護規則
新增／改名／移除任一 user-invoked skill，或改了它在流程裡的位置，就要回來更新這張表——過時的路由器會騙人。
