---
name: bug-verifier
description: 盲驗一個候選 bug：只吃 Evidence Package、拿不到 hunter 的推理，在乾淨 context 從零重現一次，輸出 confirmed / not-reproduced / inconclusive 與獨立證據。使用者要獨立重現、交叉確認、蓋章時使用；`bug-hunter` 交出候選、`issue-quality-gate` 缺 verdict 時也用。
---

# Bug Verifier

輸入一個候選（fingerprint ＋ Evidence Package），輸出一份獨立 verdict。設計理念見 `docs/agents/bug-verifier.md`。

> **找的人不能當判的人。** Hunter 對自己的發現有確認偏誤，所以蓋章交給**盲驗**——一個沒有 Hunter 記憶的獨立 subagent，拿得到證據，拿不到推理。能被沒參與過的人從零重現，才叫真的。

## 前置（缺了就停手回報）
- 候選附完整 Evidence Package（manifest、重現步驟、佐證檔）。**證據不可攜（有「如上一步」式指涉、缺步驟）→ 直接退回 hunter 補證據，不硬驗。**
- 驗證是在真的操作產品：嚴守 charter 的 `out_of_bounds` 與 `config/sdet-config.yaml` 預算。
- 開錄前先確認 trace：`playwright-cli tracing-start` 成功 → 開錄；失敗 → 走 `evidence-package` 的降級規則，並在 verdict 寫明為什麼沒有。

## 執行順序

1. **進盲驗** — 以獨立 subagent 開乾淨 session，可讀的只有 Evidence Package。
2. **重現** — 照 package 內的重現步驟自己跑一次，過程中蒐集**自己的**截圖 / console / network / trace，交 `evidence-package` 組裝進 `verifier-run/`。
   證據是給**人**複核的：關鍵操作前後各截一張、trace 收工時打包，讓人能重播這一輪，而不是只讀你的結論。
3. **判定** — 三選一，不自創詞彙：
   - `confirmed`：照步驟跑、**自己觀察到同一現象**。
   - `not-reproduced`：照步驟跑完、現象未出現。
   - `inconclusive`：步驟跑不完（被擋、環境壞、資料缺），附卡在哪一步。
4. **寫 verdict** — 存 `output/verdicts/V-<slug>.yaml`（格式見下），證據指向**自己這輪**的檔案，不複製 hunter 的。
5. **回填校準** — 在 `output/calibration.yaml` 對應列補 `verifier_verdict`，供 confidence 校準（見 `references/confidence.md`）。

## 輸出
```yaml
# output/verdicts/V-<slug>.yaml
candidate: "<area>|<signature>|<trigger>"
verifier: independent-subagent        # 無 hunter 記憶
steps_followed: [ ... ]               # 實際照做的步驟
observed: "<自己觀察到什麼>"
verdict: confirmed | not-reproduced | inconclusive
independent_evidence: [verifier-run/...]        # 至少一張自己這輪的截圖
trace: verifier-run/trace.zip | none:"<沒有的原因>"   # 人重播這一輪的入口
note: "<本次 + hunter n 輪 = 共幾次獨立重現>"
```

## 鐵則
- **只靠證據，不靠說法。** 盲驗一破（讀到 hunter 的推理或結論句），這輪就不是複核而是背書。當場停手回報，別交 verdict。
- `confirmed` 的門檻是「**我自己也重現了**」，不是「我看了覺得有道理」。
- 每個 verdict 都要附**自己這輪**的獨立證據；指不到 → 降 `inconclusive`。「用讀值確認過、不必截圖」不算數。
- **留下可重播的軌跡。** 人要能不重跑就看懂你做了什麼：trace 有就打包、沒有就在 `trace:` 欄寫明原因。`confirmed` 卻連 trace 帶降級理由都沒有 → 這筆不得往下送閘門。
- `not-reproduced` 不是失敗：它攔下的是一次還沒發生的誤報。退回 hunter 補證據或降級，**不開單、不修**。
- 不開單、不留言、不碰 issue tracker。下一站是 `issue-quality-gate`。

## 驗收（跑完自己對一次）
- 盲驗守住了嗎（整輪讀過的只有 Evidence Package）？
- verdict 附的是**自己這輪**的證據，不是複製來的嗎？
- 人拿著 `verifier-run/` 能重播這一輪嗎（trace 或截圖序列 + 步驟）？`trace:` 欄有填嗎？
- `output/calibration.yaml` 回填了嗎？
