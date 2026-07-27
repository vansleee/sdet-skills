# 全書狀態 / 資料檔（跨 skill 讀寫，非 SKILL.md）

| 檔案 | 產生 / 維護的 skill | 用途 |
|---|---|---|
| charters/<slug>.yaml | exploration-charter | 探索目標與邊界 |
| sessions/…/findings/F-*.yaml | explore | 候選發現(含 oracle 判定) |
| verdicts/V-*.yaml | bug-verifier | 獨立重現 + confidence |
| calibration.yaml | bug-hunter 寫 predicted、bug-verifier / 人複核回填 | confidence 校準（範本 `calibration.example.yaml`）|
| known-false-positives.yaml | issue-quality-gate 維護、bug-hunter 讀 | 已知誤報（範本 `known-false-positives.example.yaml`）|
| issues-index.yaml | triage 寫、bug-hunter / issue-quality-gate 讀 | bug fingerprint 去重索引（範本 `issues-index.example.yaml`）|
| gate.yaml | issue-quality-gate | 品質閘結果 |
| governance.yaml | setup-sdet 建骨架、各副作用 skill 參照 | 授權分級(見 config/governance.example.yaml) |
| tests/*.spec.ts | test-author | 固化的回歸資產 |
| runs/<date>.yaml | duty-oncall / re-run-gate | 每次執行計量(tokens/duration/model/findings/gate/issues/confirmed)→ ROI |

## 慣例
- 真檔在 repo 根目錄、已 gitignore（含產品/專案的實際判斷結果，不進版控）；
  只 commit `*.example.yaml` 範本，`setup-sdet` 或使用者複製一份開始用。
- 計分與去重的**規則**不放在狀態檔裡，放 `references/confidence.md`、`references/bug-fingerprint.md`，
  由 skill 讀取——狀態檔只存「資料」，不存「演算法」。
