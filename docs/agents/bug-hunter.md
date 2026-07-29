# Bug Hunter

依一份 charter 自主獵一輪，交回「已判定、已去重、已濾誤報、標好信心」的候選 issue 清單。

## 設計理念

- **它不發明能力，它的價值是編排。** 探索、標狀態、分類、判定、打分、去重、濾誤報，這七件事前面都各自有 skill；Hunter 做的是把它們接成一條線，並**保證順序**（先判定再打分、先去重再濾誤報），讓使用者一句話就能拿到乾淨結果。
- **「找的人」不能當「判的人」。** Hunter 對自己找到的東西有確認偏誤，所以它的權力被刻意切窄：只輸出「候選」。獨立蓋章交 `bug-verifier`（沒有 Hunter 記憶的 subagent），能不能開單交 `issue-quality-gate`。這是 `agents/` 最重要的治理設計。
- **model-invoked。** `duty-oncall` 得在值班中直接調用它，user-invoked 會讓整條編排叫不到它。「會消耗預算、會操作產品」不靠 invocation mode 擋，靠 charter 的 `out_of_bounds`、`config/sdet-config.yaml` 的 `budget`，以及「不開單、不碰 tracker」的鐵則——真正不可逆的那一下留在 `triage` / `bug-fixer` 的確認步驟與 `governance.yaml`。
- **四道守門缺一不可。** oracle 擋「把怪當成錯」、confidence 擋「沒把握的自動往下」、dedup 擋「同一個報十次」、known-FP 擋「判過的再報一次」。前三週教的規矩，在這裡第一次被強制執行而不只是好習慣。
- **證據必須可攜。** 下游 verifier 是獨立 context，拿得到證據、拿不到 Hunter 的推理。Evidence Package 站不站得住，這裡就會現形。

## 上下游

上游：`exploration-charter`（給目標與邊界）。
內部依序：`explore` → `structured-result` → `classify-anomaly` → `test-oracle` → confidence（`references/confidence.md`）→ dedup（`references/bug-fingerprint.md`）→ known-FP → `evidence-package`。
下游：`bug-verifier` → `issue-quality-gate` → `triage` / `bug-fixer`。
編排它的：`duty-oncall`（排班值勤時的第一站）。

## 狀態檔

讀：`output/known-false-positives.yaml`、`output/issues-index.yaml`、`config/sdet-config.yaml`。
寫：`output/calibration.yaml`（predicted）、evidence 目錄、候選清單。
**不寫** issue tracker。
