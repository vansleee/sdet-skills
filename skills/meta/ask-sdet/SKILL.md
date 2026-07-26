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
| 不知道用哪個 | `/ask-sdet`（就是我） |

## 主要流程（誰接誰）
**找新 bug**：`/exploration-charter` 定目標 → `/bug-hunter` 打獵（自動用 explore／evidence-package／test-oracle）→ bug-verifier 獨立重現 → issue-quality-gate 把關 → `/triage` 開單 → bug-fixer 開 PR（人 merge）

**顧測試**：`/test-author` 寫測試 → 進 CI 跑 → 紅了 failure-analysis 分析 → test-heal 修測試 → re-run-gate 重跑到綠

**顧產線**：pipeline-read 讀 run → `/pipeline-triage` 合併根因+派工 → flaky-manager／quality-gate／pipeline-observability

**串起來**：`/duty-oncall` 在授權（`config/governance.yaml`）內把上面整條排程跑完。

## 維護規則
新增／改名／移除任一 user-invoked skill，或改了它在流程裡的位置，就要回來更新這張表——過時的路由器會騙人。
