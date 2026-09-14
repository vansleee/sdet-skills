---
name: bug-verifier
description: 在乾淨 context 盲驗候選，只收重現步驟、原始證據與執行限制；支援 UI 與 API，輸出 confirmed / not-reproduced / inconclusive。需要獨立重現，或 issue-quality-gate 缺驗證結果時使用。
---

# Bug Verifier

輸入 `blind/manifest.yaml` 與包內原始證據，輸出獨立 verdict。先讀 `references/agent-handoff.md` 的識別、盲驗與證據契約；設計理念見 `docs/agents/bug-verifier.md`。

由呼叫端用當前平台的獨立 subagent／session 啟動，關閉對話繼承；不能建立乾淨 context 就退回待驗，不在原 context 自稱盲驗。

## 前置（缺了就停手回報）
- 盲驗輸入含識別、目標、前置、步驟、客觀現象、操作限制與可攜原始證據；缺漏就退回呼叫端補齊。不得自行讀完整 hunter 包。
- 依 `references/config-resolution.md` 沿用 project；可讀該專案執行設定、全域 governance 與必要共用規則。嚴守傳入的 `out_of_bounds`、剩餘預算與工具權限。
- 依介面確認留證能力。UI 開 trace，失敗時依 `evidence-package` 處理；純 API 不啟動瀏覽器。副作用請求仍須通過 `api-evidence` 的授權檢查。

## 執行順序

1. **檢查隔離**：確認沒有 hunter 對話、推理或結論。讀到污染內容就中止，交呼叫端整理後另開乾淨 context。
2. **重現與留證**：照步驟自己操作，輸出到新的 `output/evidence/<YYYYMMDD>-<任務代號>-verifier/`。UI 交 `evidence-package`；API 先檢查 `repro.sh` 的請求與副作用，再交 `api-evidence`，使用本輪 env 與新輸出目錄。混合候選兩側都留證。
3. **判定** — 三選一，不自創詞彙：
   - `confirmed`：照步驟跑、**自己觀察到同一現象**。
   - `not-reproduced`：照步驟跑完、現象未出現。
   - `inconclusive`：步驟跑不完（被擋、環境壞、資料缺），附卡在哪一步。
4. **寫 verdict**：存 `output/sessions/<session>/verdicts/V-<finding_id>.yaml`，依交接契約驗收本輪證據。相同 finding 再驗時另加序號，不覆寫前次 verdict。
5. **交回呼叫端**：回傳 verdict 路徑，由呼叫端或 gate 依 `references/confidence.md` 回填 `verifier_verdict`。本 skill 不讀寫 calibration、不計算 hunter 跨輪次數。

## 輸出
```yaml
project: null
session: <date>_<slug>
finding_id: F-001
level: api
evidence_levels: [api]
verifier: independent-subagent        # 或 independent-session
steps_followed: [ ... ]               # 實際照做的步驟
observed: "<自己觀察到什麼>"
verdict: confirmed | not-reproduced | inconclusive
verified_at: <ISO 時間>
independent_evidence: [output/evidence/<本輪>-verifier/manifest.md]
trace: null                          # UI 填本輪 trace 路徑
trace_reason: "API 驗證不經瀏覽器"     # trace 為 null 時必填
```

## 鐵則
- **只靠證據，不靠說法。** 盲驗一破（讀到 hunter 的推理或結論句），這輪就不是複核而是背書。當場停手回報，別交 verdict。
- `confirmed` 的門檻是「**我自己也重現了**」，不是「我看了覺得有道理」。
- 每個 verdict 附本輪獨立證據，依 `references/agent-handoff.md` 的介面表驗收；指不到就降 `inconclusive`。API 請求／回應可作證，不要求截圖。
- UI 缺 trace 要寫原因；煙霧降級不能取得開單資格。API 的 `trace: null` 不影響完整請求／回應證據的效力。
- `not-reproduced` 不是失敗：它攔下的是一次還沒發生的誤報。退回 hunter 補證據或降級，**不開單、不修**。
- 不開單、不留言、不碰 issue tracker。下一站是 `issue-quality-gate`。

## 驗收（跑完自己對一次）
- 是否只讀盲驗輸入與允許的執行設定，沒有 hunter 推理與對話？
- verdict 附的是**自己這輪**的證據，不是複製來的嗎？
- UI 或 API 的必要證據是否齊全，識別與 `verified_at` 是否已交回呼叫端？
