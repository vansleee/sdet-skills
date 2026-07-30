# Classify Anomaly
看到異常，先分類是哪一種原因，再決定是否往下，而不是每看到紅字就當 bug。

## 設計理念
- **一個異常有很多種原因，只有一種是產品 bug。** 環境、測資、操作錯、flaky、已知問題。不分類就報，等於開一間誤報工廠。
- **依證據判類，不靠猜。** 每次判類都要指出依據哪條 evidence。
- **跨 finding 檢查。** 多筆共用同一錯誤簽章，通常是 environment 或 stack-wide 事件，歸一類。
- **只有 product-bug 能往下。** 其餘不直接變 Issue，控制 False Positive 的源頭（把關見 `issue-quality-gate`）。

上游：`structured-result`。下游：`test-oracle` → `bug-verifier` → `triage`。
