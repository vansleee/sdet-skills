# Bug Verifier

以獨立 subagent 重現候選 bug，輸出 confirmed / not-reproduced / inconclusive，不繼承 hunter 的偏見。

## 設計理念
- **找的人不能當判的人。** 作者對自己的發現有確認偏誤；複核照搬人類團隊的 code review：找第二雙眼睛從零重現。
- **不共享記憶是刻意設計。** 它只拿得到 Evidence Package，拿不到 hunter 的推理——聽過說法就只會背書，只看證據才會真的重現。
- **兌現 Day 11 的可攜性。** 證據站不站得住，在沒有本次記憶的 verifier 面前現形；不可攜就退回，不硬驗。
- **not-reproduced 是價值，不是失敗。** 每一筆攔下的 not-reproduced，都是一次沒發生的誤報、一分沒被消耗的信任。
- **verdict 是給人複核的，不是給人相信的。** 盲驗的產出若只有一句 `confirmed`，人要嘛照單全收、要嘛自己重跑一次——兩種都讓這一站失去意義。所以 `verifier-run/` 要留可重播的軌跡（trace + 關鍵前後截圖 + 實際做過的步驟），讓複核的成本是「看五分鐘」而不是「再跑一輪」。這也是 2026-07-30 那輪的教訓：有一筆 verdict 寫「靠讀值確認、不必截圖」，人就無從檢視，只能退回重驗。

## 上下游
上游：`bug-hunter`（候選 + Evidence Package）。下游：`issue-quality-gate`（拿 verdict 當第一條檢查）。回填：`output/calibration.yaml`。編排它的：`duty-oncall`。

## 成長路徑
v0.1：單一候選、單輪重現。之後：多輪 / 跨環境重現、自動重試策略。
