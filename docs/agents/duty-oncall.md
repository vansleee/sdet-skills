# Duty Oncall

排程下把整條 pipeline 跑完一輪的「獨立值班」總編排：hunter → verifier → gate → triage / fixer，最後寫 run log。

## 設計理念
- **它不發明能力，它排班。** 每一站都是既有 skill；oncall 的價值是讓它們自己接力跑完，而不是人逐站點名。
- **敢放手，是因為門都建好了。** 值班 = 自動化的觸發 + 前面所有治理，一個都不少；編排不越權，各站鐵則原封生效。
- **發起交給排程，拍板留給人。** merge 是人按、PO 問題是人去問、hold 是人來判；它值的是「探索、驗證、把關、備好」，人值的是「不可逆的那幾下」。
- **run log 是寫給未來的自己。** ROI 與校準的原始資料只能當下埋、不能事後補；今天不記 tokens 和 gate_passed，之後就算不出一個 bug 花多少錢。
- **摘要要五分鐘能複核完**，不是要人重跑一遍。

## 上下游
輸入：charter ＋ 排程／使用者觸發。內部依序：`bug-hunter` → `bug-verifier` → `issue-quality-gate` → `triage` / `bug-fixer`。輸出：`output/runs/<date>.yaml`、值班摘要、人工佇列。

## 成長路徑
v0.1：單 charter 單班。之後：多 charter 排班、與 route-by-risk 決定值什麼、餵 sdet-economics 算帳。
