# Failure Analysis
一支測試紅了，先歸類根因、再分流，而不是直接動手修。

## 設計理念
- **紅了先別修。** 不知道是 locator drift 還是產品迴歸就修，很容易把測試改爛。先分類。
- **assertion-mismatch 一定過 oracle。** 「預期≠實際」可能是測試過時、也可能是真迴歸。用 `test-oracle` 判「產品該不該這樣」來決定改測試 vs 開 bug，不另造判斷邏輯。
- **依證據判類。** basis 指向 trace/console/network，不憑印象。
- **只分類不修。** 修測試交 `test-heal`、開產品單走 `triage`、flaky 交 `flaky-manager`。
- **一筆的引擎、一批的零件。** `pipeline-triage` 合併根因後每群呼叫本 skill 一次；本 skill 不自己做批次合併。
前身：`pytest-selenium-failure-analysis`。
