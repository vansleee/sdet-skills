---
name: status-report
description: 把近期探索 / 測試 / 開單活動整理成 standup 更新、測試報告或 release-readiness 摘要。要回報進度、寫測試報告、給團隊看時使用。關鍵詞：回報、standup、測試報告、進度、release readiness、摘要。
---

# Status Report

> 狀態：骨架（預留，TODO 待實作）

讀近期的 runs / findings / issues，產出對人的摘要：今天測了什麼、發現什麼、還卡什麼、風險在哪。輸出格式依對象（standup / 測試報告 / release-readiness）。

## TODO
- [ ] 定義輸入（runs、findings、issues 一段期間）/ 輸出（三種格式的摘要）
- [ ] 寫執行步驟：彙整 → 分「進度 / 發現 / 阻塞 / 風險」→ 依對象挑格式
- [ ] 讀 `runs/`、`issues-index.yaml`（見 `docs/state-files.md`），不重算已有數據
- [ ] 補 `agents/openai.yaml` 與 `docs/project/status-report.md`
