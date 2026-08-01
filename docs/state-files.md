# 全書狀態 / 資料檔（跨 skill 讀寫，非 SKILL.md）

| 檔案 | 產生 / 維護的 skill | 用途 |
|---|---|---|
| charters/<slug>.yaml | exploration-charter | 探索目標與邊界 |
| output/sessions/<date>_<slug>/exploration-log.yaml | explore | 這次探索走過的路徑 |
| output/sessions/<date>_<slug>/findings/F-*.yaml | explore | 候選發現（含 oracle 判定） |
| output/evidence/<YYYYMMDD>-<slug>/ | evidence-package | 截圖 / console / network / trace |
| output/evidence/_traces/ | Playwright MCP（`--output-dir`） | 工具自動落地的 snapshot 與 console 暫存 |
| output/verdicts/V-*.yaml | bug-verifier | 獨立重現 + confidence |
| output/calibration.yaml | bug-hunter 寫 predicted、bug-verifier / 人複核回填 | confidence 校準（範本 `state-templates/calibration.example.yaml`）|
| output/known-false-positives.yaml | issue-quality-gate 維護、bug-hunter 讀 | 已知誤報（範本 `state-templates/known-false-positives.example.yaml`）|
| output/issues-index.yaml | triage 寫、bug-hunter / issue-quality-gate 讀 | bug fingerprint 去重索引（範本 `state-templates/issues-index.example.yaml`）|
| output/gate.yaml | issue-quality-gate | **一張 issue** 能不能開的閘門結果 |
| governance.yaml | setup-sdet 建骨架、各副作用 skill 參照 | 授權分級（見 config/governance.example.yaml） |
| tests/*.spec.ts | test-author | 固化的回歸資產 |
| output/runs/<date>.yaml | duty-oncall | 一次值班的計量（tokens/duration/model/findings/gate/issues/confirmed）→ ROI |
| output/runs/reruns-<date>.yaml | re-run-gate | 逐支測試的重跑紀錄（次數/逐次結果/裁決）→ flaky 趨勢 |
| output/triage-reports/<date>_<run>.md | pipeline-triage | 一片紅的根因群 → owner → issue 對照報告 |
| output/flaky-registry.yaml | flaky-manager 寫；quality-gate / pipeline-observability / re-run-gate 讀 | flaky 名單與 quarantine 狀態、到期日（範本 `state-templates/flaky-registry.example.yaml`）|
| output/pipeline-gate.yaml | infra/quality-gate 寫；release-signoff / pipeline-observability / status-report 讀 | **一個 build** 能不能放行 + override 留痕（範本 `state-templates/pipeline-gate.example.yaml`）|
| output/reports/health-<date>.md | pipeline-observability | 測試健康指標、趨勢與行動路由 |
| output/plans/<slug>.md | test-planning | 本輪測試範圍 + 風險排序 + out-of-scope 理由 |
| output/traceability.yaml | traceability 寫；test-planning / release-signoff / pipeline-observability 讀 | 需求 ↔ 測試 ↔ finding 覆蓋對照與 gap（範本 `state-templates/traceability.example.yaml`）|
| output/reports/status-<date>.md | status-report | standup / 測試報告 / release-readiness 摘要 |
| output/signoffs/<version>.yaml | release-signoff | **整個 release** 能不能簽出去 + 簽核留痕（範本 `state-templates/signoff.example.yaml`）|

## 三層閘門，三個檔（別混用）
| 層級 | 問題 | skill | 檔案 |
|---|---|---|---|
| issue | 這張單能不能開？ | `issue-quality-gate` | `output/gate.yaml` |
| build | 這個 build 能不能放行？ | `infra/quality-gate` | `output/pipeline-gate.yaml` |
| release | 這一版能不能簽出去？ | `release-signoff` | `output/signoffs/<version>.yaml` |

上層**吃**下層的檔案當證據，不重跑下層。共用檔名會讓兩邊互相覆寫，而且覆寫當下不會有人發現。

## 慣例
- 真檔在 repo 根目錄、已 gitignore（含產品/專案的實際判斷結果，不進版控）；
  範本集中在 `state-templates/`，`setup-sdet` 或使用者複製到根目錄成同名真檔開始用。
- 計分與去重的**規則**不放在狀態檔裡，放 `references/confidence.md`、`references/bug-fingerprint.md`、
  `references/test-health-metrics.md`、`references/traceability-mapping.md`，
  由 skill 讀取。狀態檔只存「資料」，不存「演算法」。
- 門檻與預算放 `config/sdet-config.yaml`（範本 `config/sdet-config.example.yaml`），不寫死在 skill 裡。
