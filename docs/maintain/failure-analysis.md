# Failure Analysis
一支測試紅了，先歸類根因、再分流，而不是直接動手修。

## 設計理念
- **紅了先別修。** 不知道是 locator drift 還是產品迴歸就修，很容易把測試改爛。先分類。
- **assertion-mismatch 一定過 oracle。** 「預期≠實際」可能是測試過時、也可能是真迴歸。用 `test-oracle` 判「產品該不該這樣」來決定改測試 vs 開 bug，不另造判斷邏輯。
- **依證據判類。** basis 指向 trace/console/network，不憑印象。
- **只分類不修。** 修測試交 `test-heal`、開產品單走 `triage`、flaky 交 `flaky-manager`。
- **一筆的引擎、一批的零件。** `pipeline-triage` 合併根因後每群呼叫本 skill 一次；本 skill 不自己做批次合併。
- **分類表要跟得上介面層。** `locator` 與 `wait-timing` 是畫面專屬的分類，API 測試紅了永遠不會命中它們。少了對應的 API 分類，這些失敗只能落進 `unknown` 或被硬塞進 `environment`，派工就會派錯人：契約漂移該找寫測試的人或後端，憑證過期該找環境，兩者都不是「重試看看」。
- **`contract-drift` 跟 `assertion-mismatch` 走同一個分岔。** 回應結構變了，究竟是契約也改了（測試過時）還是後端改壞了（產品迴歸），一樣不自己猜，交 `test-oracle`。
前身：`pytest-selenium-failure-analysis`。
