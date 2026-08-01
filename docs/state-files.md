# 全書狀態 / 資料檔（跨 skill 讀寫，非 SKILL.md）

檔案分兩類：**一輪探索自己的產物**收在 `output/sessions/<date>_<slug>/` 底下，一輪一夾、彼此不干擾；**跨輪累積的登錄簿**留在 `output/` 根目錄，因為去重、校準、flaky 追蹤本來就要跨輪比對。`<date>` 用 `YYYY-MM-DD`（例：`output/sessions/2026-08-01_academybugs/`）。

## 一輪一夾：`output/sessions/<date>_<slug>/`

| 檔案 | 產生 / 維護的 skill | 用途 |
|---|---|---|
| exploration-log.yaml | explore | 這次探索走過的路徑 |
| findings/F-*.yaml | explore | 候選發現（含 oracle 判定） |
| verdicts/V-*.yaml | bug-verifier | 獨立重現 + confidence |
| gate.yaml | issue-quality-gate | **一張 issue** 能不能開的閘門結果 |
| runs/<date>.yaml | duty-oncall | 一次值班的計量（tokens/duration/model/findings/gate/issues/confirmed）→ ROI |
| runs/reruns-<date>.yaml | re-run-gate | 逐支測試的重跑紀錄（次數/逐次結果/裁決）→ flaky 趨勢 |

## 跨輪累積：`output/` 根目錄

| 檔案 | 產生 / 維護的 skill | 用途 |
|---|---|---|
| output/issues-index.yaml | triage 寫、bug-hunter / issue-quality-gate 讀 | bug fingerprint 去重索引（範本 `state-templates/issues-index.example.yaml`）|
| output/calibration.yaml | bug-hunter 寫 predicted、bug-verifier / 人複核回填 | confidence 校準（範本 `state-templates/calibration.example.yaml`）|
| output/known-false-positives.yaml | issue-quality-gate 維護、bug-hunter 讀 | 已知誤報（範本 `state-templates/known-false-positives.example.yaml`）|
| output/flaky-registry.yaml | flaky-manager 寫；quality-gate / pipeline-observability / re-run-gate 讀 | flaky 名單與 quarantine 狀態、到期日（範本 `state-templates/flaky-registry.example.yaml`）|
| output/traceability.yaml | traceability 寫；test-planning / release-signoff / pipeline-observability 讀 | 需求 ↔ 測試 ↔ finding 覆蓋對照與 gap（範本 `state-templates/traceability.example.yaml`）|
| output/pipeline-gate.yaml | infra/quality-gate 寫；release-signoff / pipeline-observability / status-report 讀 | **一個 build** 能不能放行 + override 留痕（範本 `state-templates/pipeline-gate.example.yaml`）|
| output/signoffs/<version>.yaml | release-signoff | **整個 release** 能不能簽出去 + 簽核留痕（範本 `state-templates/signoff.example.yaml`）|
| output/plans/<slug>.md | test-planning | 本輪測試範圍 + 風險排序 + out-of-scope 理由 |
| output/triage-reports/<date>_<run>.md | pipeline-triage | 一片紅的根因群 → owner → issue 對照報告 |
| output/reports/health-<date>.md | pipeline-observability | 測試健康指標、趨勢與行動路由 |
| output/reports/status-<date>.md | status-report | standup / 測試報告 / release-readiness 摘要 |
| output/evidence/<YYYYMMDD>-<slug>/ | evidence-package | 截圖 / console / network / trace |

## 不在 output/ 底下

| 檔案 | 產生 / 維護的 skill | 用途 |
|---|---|---|
| charters/<slug>.yaml | exploration-charter | 探索目標與邊界；是**輸入**，人寫或 test-planning 產，要 commit |
| tests/*.spec.ts | test-author | 固化的回歸資產。**留在 repo 根**：要 commit、要被 CI 抓得到，放進被 gitignore 的 `output/` 等於永遠不進版控 |
| config/governance.yaml | setup-sdet 建骨架、各副作用 skill 參照 | 授權分級（見 `config/governance.example.yaml`）|
| .playwright-cli/ | playwright-cli | 工具自動落地的 snapshot 與 trace 暫存；`scripts/pack-trace.sh` 打包後清空（可用 `PW_TRACE_DIR` 覆寫）|

## 三層閘門，三個檔（別混用）
| 層級 | 問題 | skill | 檔案 |
|---|---|---|---|
| issue | 這張單能不能開？ | `issue-quality-gate` | `output/sessions/<date>_<slug>/gate.yaml` |
| build | 這個 build 能不能放行？ | `infra/quality-gate` | `output/pipeline-gate.yaml` |
| release | 這一版能不能簽出去？ | `release-signoff` | `output/signoffs/<version>.yaml` |

上層**吃**下層的檔案當證據，不重跑下層。共用檔名會讓兩邊互相覆寫，而且覆寫當下不會有人發現。

## 慣例
- 執行期真檔全在 `output/` 底下，整個 gitignore（含產品/專案的實際判斷結果，不進版控）；
  範本集中在 `state-templates/`，`setup-sdet` 或使用者複製到對應位置成同名真檔開始用。
- 計分與去重的**規則**不放在狀態檔裡，放 `references/confidence.md`、`references/bug-fingerprint.md`、
  `references/test-health-metrics.md`、`references/traceability-mapping.md`，
  由 skill 讀取。狀態檔只存「資料」，不存「演算法」。
- 門檻與預算放 `config/sdet-config.yaml`（範本 `config/sdet-config.example.yaml`），不寫死在 skill 裡。
- 跨輪登錄簿（issues-index、calibration、known-false-positives、flaky-registry）**不得**搬進 session 資料夾。
  它們的價值就在跨輪累積，切進單輪就失去去重與校準的能力。
- **2026-08-01 之前的舊產物不搬**：`output/verdicts/`、`output/gate.yaml`、`output/runs/` 底下的檔案留在原位當 legacy，
  對不回是哪一輪產的。讀到它們照讀，**但不要再往那些路徑寫**；新的一輪一律走 `output/sessions/<date>_<slug>/`。
