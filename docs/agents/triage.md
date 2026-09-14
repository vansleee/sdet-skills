# Triage
把通過分類的 product-bug 寫成可重現報告、開成 GitHub Issue。

## 設計理念
- **只吃 product-bug。** 非 product-bug（環境／測資／flaky…）在 `classify-anomaly` 就被擋掉，triage 不重判。
- **報告寫行為、不寫實作。** agent 從外部操作產品，被迫用使用者語言描述，報告天生耐久、跨得過重構。
- **重現步驟必填。** 湊不齊就不開單（更嚴的把關見 `issue-quality-gate`）。
- **後端隨 project。** 指令與 labels 讀解析後的專案設定，GitHub 明確指定 repository。本地 Issue 也保留 project 與 finding 識別；登入失敗不能偷偷換後端。
- **每個動作各有授權。** create_issue、comment_issue、update_issue 各自檢查全域 governance；沿用涵蓋範圍的既有授權，forbidden 優先。
- **送出前再去重。** gate pass 之後可能已有新單；最後再讀 index，命中就停止新單流程。舊單補證需要留言授權，不因禁止開新單就一併禁止準備補充資料。

## 成長路徑
v0.1：一張報告、手動開一張。之後：去重、委派 `bug-verifier`/`bug-fixer`、批次見 `pipeline-triage`。
前身：`jenkins-failure-triage` / `pytest-failure-triage`（JIRA 版）。
