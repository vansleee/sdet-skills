---
name: classify-anomaly
description: 探索或測試時看到異常，先分類它是哪一種（產品 bug / 環境 / 測資 / 操作造成 / flaky / 已知 / 待查），再決定是否往下走。看到 error、非 2xx、畫面怪、當機、時好時壞時使用。關鍵詞：分類、異常、是不是 bug、誤報、environment、flaky。
---

# Classify Anomaly

輸入一個 `fail` 或 `anomaly`（來自 `structured-result`，需附證據），輸出「哪一類 + 信心 + 下一步」。**看到異常不等於找到 bug——先分類，不定罪。** 設計理念見 `docs/observe/classify-anomaly.md`。

## 類別（category）
| category | 訊號 | 是否可往下開單 |
|---|---|---|
| product-bug | 可重現、與規格/預期不符、非環境或測試所致 | 是（續走 test-oracle / bug-verifier）|
| environment | 服務 5xx、逾時、CDN、DNS、憑證、資料被重置、基礎設施 | 否 |
| test-data | 帳號被鎖/過期、髒資料、前一步污染狀態 | 否 |
| operation-artifact | agent 自己操作造成（順序錯、前置沒做、選錯元素）| 否 |
| flaky | 同操作間歇重現（重現率 < 100%）| 否（記重現率、觀察）|
| known-issue | 命中已知問題清單 | 否 |
| needs-investigation | 證據不足以歸類 | 否（再蒐證）|

## 步驟
1. 讀該筆 finding 的 evidence（network / console / 截圖 / trace）。
2. 依證據判類，**不靠猜**；寫下判類依據（指向哪條 evidence）。
3. 給 confidence（low / med / high）與下一步（如 environment→重試並查服務；product-bug→嘗試穩定重現後續走）。
4. **跨 finding 檢查**：多筆共用同一錯誤簽章（同一逾時 / 5xx / 連線錯）→ 很可能是 environment 或 stack-wide 事件，歸一類，不要逐筆當產品 bug。

## 規則
- 只有 `product-bug` 可往下（`test-oracle` → `bug-verifier` → 開單）。其餘一律不直接變 Issue（False Positive 控制，見 `issue-quality-gate`）。
- `flaky` 必記重現率；`needs-investigation` 必寫「還缺什麼證據」。
- 判類寫回該 finding：`category` / `confidence` / `basis`（證據依據）/ `next_step`。
- basis 要能區分「前端還是後端的鍋」：同一個異常，證據脈絡不同結論不同（例：畫面顯示 -$70.75，若 reload 後回復、變更未寫入後端＝前端沒驗證；若 reload 後仍在、真存進後端＝後端也沒驗證）。

## 輸出（附加到 finding）
```yaml
- id: R-03
  status: fail
  category: product-bug
  confidence: high
  basis: "前端讓 -5 通過顯示 -$70.75;變更未觸發寫入呼叫、reload 後回復 1(從未寫入後端) → 問題在前端,排除環境"
  next_step: "嘗試穩定重現 3 次後交 bug-verifier"
```
