# Re-run Gate
修完測試後，確認是「穩定的綠」才放行；超過上限仍紅就 escalate。

## 設計理念
- **過一次不算修好。** 3 次過 1 是 flaky 不是綠。只認「連續 N 次全綠」。
- **1/N 不是 pass：`test-heal` 綠色作弊的延伸防線。** 「重跑到過為止」一樣是騙綠燈，明文禁止。
- **一定要有停止條件。** 無限重試燒錢又拖延；到 max_retries 就 escalate 交人。
- **埋計量。** 逐次結果寫 `output/sessions/<date>_<slug>/runs/`，是 ROI 的分母之一，也是 flaky 趨勢來源。
- **只裁決不修。** 再修回 `test-heal`、穩定性問題交 `flaky-manager`。
前身：`re-run-gate`。
