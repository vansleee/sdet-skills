# 全書狀態 / 資料檔（跨 skill 讀寫，非 SKILL.md）

檔案分兩類：**一輪探索自己的產物**收在 `output/sessions/<date>_<slug>/` 底下，一輪一夾、彼此不干擾；**跨輪累積的登錄簿**留在 `output/` 根目錄，因為去重、校準、flaky 追蹤本來就要跨輪比對。`<date>` 用 `YYYY-MM-DD`（例：`output/sessions/2026-08-01_academybugs/`）。

## 一輪一夾：`output/sessions/<date>_<slug>/`

| 檔案 | 產生 / 維護的 skill | 用途 |
|---|---|---|
| exploration-log.yaml | explore | 這次探索走過的路徑 |
| findings/F-*.yaml | explore | 候選發現（含 oracle 判定） |
| verdicts/V-*.yaml | bug-verifier | 獨立重現結果與本輪證據，不含 hunter 評分 |
| reports/<finding_id>.md | triage | Issue 草稿、精確目標與副作用授權來源 |
| gate.yaml | issue-quality-gate | **一張 issue** 能不能開的閘門結果 |
| runs/<date>.yaml | duty-oncall | 一次值班的計量（tokens/cost_usd/cost_by_stage_usd/duration/model/findings/gate/issues/confirmed）→ ROI。token 與成本取自 `output/token-ledger`，靠 `ledger_run` 欄位對回逐階段明細 |
| runs/reruns-<date>.yaml | re-run-gate | 逐支測試的重跑紀錄（次數/逐次結果/裁決）→ flaky 趨勢 |

## 跨輪累積：`output/` 根目錄

| 檔案 | 產生 / 維護的 skill | 用途 |
|---|---|---|
| output/issues-index.yaml | triage 建立；bug-hunter 合併本地觀察；issue-quality-gate 讀 | 以 project + fingerprint 去重；不替代 tracker 授權（範本 `state-templates/issues-index.example.yaml`）|
| output/calibration.yaml | hunter 寫 predicted；呼叫端／gate 回填 verifier；明確人判才填 human | 以 project + session + finding_id 定位預測（範本 `state-templates/calibration.example.yaml`）|
| output/known-false-positives.yaml | issue-quality-gate 維護、bug-hunter 讀 | 已知誤報（範本 `state-templates/known-false-positives.example.yaml`）|
| output/flaky-registry.yaml | flaky-manager 寫；quality-gate / pipeline-observability / re-run-gate 讀 | flaky 名單與 quarantine 狀態、到期日（範本 `state-templates/flaky-registry.example.yaml`）|
| output/traceability.yaml | traceability 寫；test-planning / release-signoff / pipeline-observability 讀 | 需求 ↔ 測試 ↔ finding 覆蓋對照與 gap（範本 `state-templates/traceability.example.yaml`）|
| output/pipeline-gate.yaml | infra/quality-gate 寫；release-signoff / pipeline-observability / status-report 讀 | **一個 build** 能不能放行 + override 留痕（範本 `state-templates/pipeline-gate.example.yaml`）|
| output/signoffs/<version>.yaml | release-signoff | **整個 release** 能不能簽出去 + 簽核留痕（範本 `state-templates/signoff.example.yaml`）|
| output/plans/<slug>.md | test-planning | 本輪測試範圍 + 風險排序 + out-of-scope 理由 |
| output/triage-reports/<date>_<run>.md | pipeline-triage | 一片紅的根因群 → owner → issue 對照報告 |
| output/reports/health-<date>.md | pipeline-observability | 測試健康指標、趨勢與行動路由 |
| output/reports/status-<date>.md | status-report | standup / 測試報告 / release-readiness 摘要 |
| output/token-ledger/<session_id>.yaml | `scripts/token-ledger.py`（Stop / SessionEnd hook 自動寫） | 單一 session 逐次 skill 呼叫的 token 與成本：`calls[]`（run / stage / skill / action / models / input / output / cache_write_5m / cache_write_1h / cache_read / cost_usd）＋ `by_run`（逐次 run 的逐階段成本，靠編排者打的 mark 分段）/ `by_skill` / `by_action` / `total` |
| output/token-ledger/rollup.yaml | 同上，每次寫入後重算 | 跨 session 累積：依 skill 與依動作（hunt / verify / rerun / file / fix …）的呼叫次數、token、美金成本 → 餵 `sdet-economics` 的 ROI |
| output/evidence/<YYYYMMDD>-<slug>/ | evidence-package、api-evidence | 畫面側：截圖 / console / network / trace；API 側：requests.jsonl / repro.sh / raw/。兩者共用同一夾，manifest 只寫一份 |
| output/evidence/<YYYYMMDD>-<slug>/blind/ | hunter 或 verifier 呼叫端 | 去除推理與結論的 manifest.yaml 及原始證據副本，只供盲驗輸入 |
| output/evidence/<YYYYMMDD>-<slug>-verifier/ | bug-verifier 呼叫留證 skill | 與 hunter 分開的獨立證據；重驗另加序號，不能覆寫前次產物 |

## Agents 共用欄位

交接規則見 `references/agent-handoff.md`，回填規則見 `references/confidence.md`。下列欄位是資料契約，不由各 skill 自行改名。

| 資料 | 必填欄位與語意 |
|---|---|
| 候選／盲驗／verdict／gate／分派 | `project`（null 表預設專案）、`session`（本輪目錄名）、`finding_id`、`level: ui\|api`；混合證據另填 `evidence_levels: [ui, api]` |
| verdict | `verifier: independent-subagent\|independent-session`、`steps_followed`、`observed`、`verdict: confirmed\|not-reproduced\|inconclusive`、`verified_at`、`independent_evidence`、`trace`；trace 為 null 時須有 `trace_reason` |
| gate | `candidate`（fingerprint）、六條 `checks` 各填 pass／fail、`result: pass\|hold\|block`；hold／block 填 `blocked_on`，重複項填 `existing_issue` |
| issues-index | `project`、`fingerprint`、`issue`、`occurrences`、`confidence`、`evidence`、`observations`（各筆 session + finding_id，防止重複計數） |
| known-false-positives | `project` 與原有 pattern／scope／reason／decided_by／decided_at；只套用同 project 的規則 |
| calibration 預測 | `project`、`session`、`finding_id`、`finding`、`fingerprint`、`predicted`、數值 `score`、`predicted_at` |
| calibration 獨立驗證 | `verifier_verdict`、`verifier_verdict_at`、`verifier_evidence`（verdict 檔路徑）；未驗為 null |
| calibration 閘門 | `gate_result`、`gate`（gate 檔路徑）；未跑為 null |
| calibration 人工裁定 | `human_verdict`、`human_verdict_at`、`human_verdict_by`、`human_evidence`；未裁定為 null |

`verifier_verdict` 沿用 verifier 的三態；`human_verdict` 沿用 confirmed／not-reproduced／not-a-bug。不得把閘門的 block 當成人工否定，也不得把 verifier 結果複製成人工結果。舊 `verdict_at` 僅作歷史欄位，來源明確才搬到對應時間戳；來源不明的資料保留且排除新指標，不刪除或猜填。

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
