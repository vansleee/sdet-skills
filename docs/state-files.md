# 全書狀態 / 資料檔（跨 skill 讀寫，非 SKILL.md）

| 檔案 | 產生 / 維護的 skill | 用途 |
|---|---|---|
| charters/<slug>.yaml | exploration-charter | 探索目標與邊界 |
| sessions/…/findings/F-*.yaml | explore | 候選發現(含 oracle 判定) |
| verdicts/V-*.yaml | bug-verifier | 獨立重現 + confidence |
| calibration.yaml | bug-hunter 寫 predicted、bug-verifier / 人複核回填 | confidence 校準（範本 `calibration.example.yaml`）|
| known-false-positives.yaml | issue-quality-gate 維護、bug-hunter 讀 | 已知誤報（範本 `known-false-positives.example.yaml`）|
| issues-index.yaml | triage 寫、bug-hunter / issue-quality-gate 讀 | bug fingerprint 去重索引（範本 `issues-index.example.yaml`）|
| gate.yaml | issue-quality-gate | **一張 issue** 能不能開的閘門結果 |
| governance.yaml | setup-sdet 建骨架、各副作用 skill 參照 | 授權分級(見 config/governance.example.yaml) |
| tests/*.spec.ts | test-author | 固化的回歸資產 |
| runs/<date>.yaml | duty-oncall / re-run-gate | 每次執行計量(tokens/duration/model/findings/gate/issues/confirmed)→ ROI |
| triage-reports/<date>_<run>.md | pipeline-triage | 一片紅的根因群 → owner → issue 對照報告 |
| flaky-registry.yaml | flaky-manager 寫;quality-gate / pipeline-observability / re-run-gate 讀 | flaky 名單與 quarantine 狀態、到期日（範本 `flaky-registry.example.yaml`）|
| pipeline-gate.yaml | infra/quality-gate 寫;release-signoff / pipeline-observability / status-report 讀 | **一個 build** 能不能放行 + override 留痕（範本 `pipeline-gate.example.yaml`）|
| reports/health-<date>.md | pipeline-observability | 測試健康指標、趨勢與行動路由 |
| plans/<slug>.md | test-planning | 本輪測試範圍 + 風險排序 + out-of-scope 理由 |
| traceability.yaml | traceability 寫;test-planning / release-signoff / pipeline-observability 讀 | 需求 ↔ 測試 ↔ finding 覆蓋對照與 gap（範本 `traceability.example.yaml`）|
| reports/status-<date>.md | status-report | standup / 測試報告 / release-readiness 摘要 |
| signoffs/<version>.yaml | release-signoff | **整個 release** 能不能簽出去 + 簽核留痕（範本 `signoff.example.yaml`）|

## 三層閘門，三個檔（別混用）
| 層級 | 問題 | skill | 檔案 |
|---|---|---|---|
| issue | 這張單能不能開？ | `issue-quality-gate` | `gate.yaml` |
| build | 這個 build 能不能放行？ | `infra/quality-gate` | `pipeline-gate.yaml` |
| release | 這一版能不能簽出去？ | `release-signoff` | `signoffs/<version>.yaml` |

上層**吃**下層的檔案當證據，不重跑下層。共用檔名會讓兩邊互相覆寫，而且覆寫當下不會有人發現。

## 慣例
- 真檔在 repo 根目錄、已 gitignore（含產品/專案的實際判斷結果，不進版控）；
  只 commit `*.example.yaml` 範本，`setup-sdet` 或使用者複製一份開始用。
- 計分與去重的**規則**不放在狀態檔裡，放 `references/confidence.md`、`references/bug-fingerprint.md`、
  `references/test-health-metrics.md`、`references/traceability-mapping.md`，
  由 skill 讀取——狀態檔只存「資料」，不存「演算法」。
- 門檻與預算放 `config/sdet-config.yaml`（範本 `config/sdet-config.example.yaml`），不寫死在 skill 裡。
