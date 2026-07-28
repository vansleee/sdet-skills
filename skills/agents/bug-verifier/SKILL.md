---
name: bug-verifier
description: 以獨立 subagent 重現候選 bug：只吃 Evidence Package、不聽 hunter 的推理，在乾淨 context 從零重現一次，輸出 confirmed / not-reproduced / inconclusive 與獨立證據，並回填 calibration。使用者說「驗這個」「獨立重現」「交叉確認」「verify」時使用。關鍵詞：驗證、重現、verifier、蓋章、交叉確認。
disable-model-invocation: true
---

# Bug Verifier (v0.1)

輸入一個候選（fingerprint ＋ Evidence Package），輸出一份獨立 verdict。設計理念見 `docs/agents/bug-verifier.md`。

> **找的人不能當判的人。** Hunter 對自己的發現有確認偏誤，所以蓋章交給一個**沒有 Hunter 記憶**的獨立 subagent：拿得到證據，拿不到推理。能被沒參與過的人從零重現，才叫真的。

## 前置（缺了就停手回報）
- 候選附完整 Evidence Package（manifest、重現步驟、佐證檔）。**證據不可攜（有「如上一步」式指涉、缺步驟）→ 直接退回 hunter 補證據，不硬驗。**
- 驗證是在真的操作產品：嚴守 charter 的 `out_of_bounds` 與 `config/sdet-config.yaml` 預算。

## 執行順序

1. **隔離** — 以獨立 subagent 開乾淨 session，**只讀 Evidence Package**；不讀 hunter 的對話、推理、結論句。
2. **重現** — 照 package 內的重現步驟自己跑一次，過程中蒐集**自己的**截圖 / console / network（存 `verifier-run/`）。
3. **判定** — 三選一，不自創詞彙：
   - `confirmed`：照步驟跑、**自己觀察到同一現象**。
   - `not-reproduced`：照步驟跑完、現象未出現。
   - `inconclusive`：步驟跑不完（被擋、環境壞、資料缺），附卡在哪一步。
4. **寫 verdict** — 存 `verdicts/V-<slug>.yaml`（格式見下），證據指向**自己這輪**的檔案，不複製 hunter 的。
5. **回填校準** — 在 `calibration.yaml` 對應列補 `verifier_verdict`，供 confidence 校準（見 `references/confidence.md`）。

## 輸出
```yaml
# verdicts/V-<slug>.yaml
candidate: "<area>|<signature>|<trigger>"
verifier: independent-subagent        # 無 hunter 記憶
steps_followed: [ ... ]               # 實際照做的步驟
observed: "<自己觀察到什麼>"
verdict: confirmed | not-reproduced | inconclusive
independent_evidence: [verifier-run/...]
note: "<本次 + hunter n 輪 = 共幾次獨立重現>"
```

## 鐵則
- **只靠證據，不靠說法。** 開工前不得讀 hunter 的推理；讀了就不是獨立複核，是背書。
- `confirmed` 的門檻是「**我自己也重現了**」，不是「我看了覺得有道理」。
- 每個 verdict 都要附**自己這輪**的獨立證據；指不到 → 降 `inconclusive`。
- `not-reproduced` 不是失敗：它攔下的是一次還沒發生的誤報。退回 hunter 補證據或降級，**不開單、不修**。
- 不開單、不留言、不碰 issue tracker——下一站是 `issue-quality-gate`。

## 驗收（跑完自己對一次）
- 是不是**真的只讀了 Evidence Package**、沒接觸 hunter 的推理？
- verdict 附的是**自己這輪**的證據，不是複製來的嗎？
- `calibration.yaml` 回填了嗎？
