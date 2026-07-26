# Triage
把通過分類的 product-bug 寫成可重現報告、開成 GitHub Issue。

## 設計理念
- **只吃 product-bug。** 非 product-bug（環境／測資／flaky…）在 `classify-anomaly` 就被擋掉，triage 不重判。
- **報告寫行為、不寫實作。** agent 從外部操作產品，被迫用使用者語言描述，報告天生耐久、跨得過重構。
- **重現步驟必填。** 湊不齊就不開單（更嚴的把關見 `issue-quality-gate`）。
- **後端可替換。** 指令讀 `config/issue-tracker-github.md`。
- **開單先確認。** 對外副作用先列給人確認再呼叫 API。

## 成長路徑
v0.1：一張報告、手動開一張。之後：去重、委派 `bug-verifier`/`bug-fixer`、批次見 `pipeline-triage`。
前身：`jenkins-failure-triage` / `pytest-failure-triage`（JIRA 版）。
