# Bug Verifier

以不繼承對話的獨立 subagent／session 重現候選，輸出 confirmed / not-reproduced / inconclusive。Claude Code、Codex 與 ChatGPT 共用 `references/agent-handoff.md` 的契約，依實際平台建立乾淨 context。

## 設計理念
- **找的人不能當判的人。** 作者對自己的發現有確認偏誤；複核照搬人類團隊的 code review：找第二雙眼睛從零重現。
- **不共享記憶是刻意設計。** 它只收盲驗包，允許另讀必要執行設定。完整 Evidence Package 的 notes 與 manifest 含結論，留給 gate 與人，不交 verifier。
- **兌現 Day 11 的可攜性。** 證據站不站得住，在沒有本次記憶的 verifier 面前現形；不可攜就退回，不硬驗。
- **not-reproduced 是價值，不是失敗。** 每一筆攔下的 not-reproduced，都是一次沒發生的誤報、一分沒被消耗的信任。
- **verdict 要能複核。** UI 留本輪 trace、前後截圖與步驟；API 留本輪請求／回應、body 與可重現請求。產物寫獨立 evidence 目錄。API 沒有畫面，不能用截圖缺失否定其證據。
- **確認的是問題重現。** confirmed 表示同一現象再次出現，不表示修復成功。這一站在 gate 與修復之前；修復後的先紅後綠由 bug-fixer 負責。

## 上下游
上游：hunter 或呼叫端提供盲驗輸入。下游：issue-quality-gate。verifier 不讀 calibration；呼叫端或 gate 依完整識別回填 verifier 欄位，人工裁定另存 human 欄位。

## 成長路徑
v0.1：單一候選、單輪重現。之後：多輪 / 跨環境重現、自動重試策略。
