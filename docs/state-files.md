# 全書狀態 / 資料檔（跨 skill 讀寫，非 SKILL.md）

| 檔案 | 產生 / 維護的 skill | 用途 |
|---|---|---|
| charters/<slug>.yaml | exploration-charter | 探索目標與邊界 |
| sessions/…/findings/F-*.yaml | explore | 候選發現(含 oracle 判定) |
| verdicts/V-*.yaml | bug-verifier | 獨立重現 + confidence |
| calibration.yaml | bug-verifier | confidence 校準 |
| known-false-positives.yaml | issue-quality-gate | 已知誤報 |
| issues-index.yaml | triage | bug fingerprint 去重索引 |
| gate.yaml | issue-quality-gate | 品質閘結果 |
| governance.yaml | setup-sdet 建骨架、各副作用 skill 參照 | 授權分級(見 config/governance.example.yaml) |
| tests/*.spec.ts | test-author | 固化的回歸資產 |
| runs/<date>.yaml | duty-oncall / re-run-gate | 每次執行計量(tokens/duration/model/findings/gate/issues/confirmed)→ ROI |
