# Bug Fingerprint 去重規則（reference，被 bug-hunter / triage / issue-quality-gate 讀）

同一個 bug 出現四次，是「信心 ×4」，不是「單子 ×4」。
指紋的工作：讓**同一個 bug 的不同次觀察算出同一個字串**，不同 bug 算出不同字串。

## 格式

```
<area>|<signature>|<trigger>
```

| 欄位 | 是什麼 | 規則 |
|---|---|---|
| `area` | 行為區域 | 用路由或功能名（`checkout`、`cart`、`login`），**去掉 query string 與 id** |
| `signature` | 錯誤簽章或現象 | 錯誤型別 + 關鍵屬性名，或一句穩定的現象描述；**不含 stack trace、行號** |
| `trigger` | 觸發條件「類別」 | 動詞-名詞（`enter-checkout`、`set-qty-0`），描述**做了什麼類型的事**，不是具體值 |

全部小寫、以 `-` 連字。

## 正規化（算之前先做）

- UUID / ULID / hash → `<id>`
- 具體數字（次數、金額、qty 值） → `<n>`；但**分類性的值保留**（`qty-0` 與 `qty-negative` 是不同 bug）
- 時間戳、session id、cart id → 移除
- 大小寫統一、空白轉 `-`

## 不准放進指紋（放了就永遠去不了重）

出現次數、時間戳、cart id / session id、螢幕截圖路徑、瀏覽器版本、測試帳號、環境名稱。
這些屬於**觀察紀錄**，掛在 issue 的 evidence 上，不進指紋。

## 鬆緊拿捏

- **太鬆**（只用 `checkout|typeerror`）→ 把不同 bug 併成一張，開發者看不懂。
- **太緊**（把 `29 次`、cart id 算進去）→ 同一個 bug 每次指紋都不同，永遠去不了重。
- 判準：**只放「換一次觀察也不會變的本質」**。

## 比對與合併

1. 算出指紋 → 查 `issues-index.yaml`。
2. **完全相同** → 不開新單：舊單 `occurrences += 1`、把新證據 append 到 `evidence`、必要時更新 `confidence`。
3. **`area` + `signature` 相同但 `trigger` 不同** → 標 `related`，**不自動合併**，列給人判（可能是同一根因的兩個入口，也可能真是兩個 bug）。
4. **找不到** → 才開新單，並把指紋寫進 index。

## 範例（取自 toolshop 四輪真跑）

```yaml
# issues-index.yaml
- fingerprint: "checkout|typeerror:cart_items-undefined|enter-checkout"
  issue: "#<n>"
  occurrences: 4          # 四輪各一次,一張單
  confidence: high
- fingerprint: "cart|http-404-on-stale-cart-id|use-expired-local-cart-id"
  occurrences: 2          # 匿名 + 已登入,同一指紋 → 併入
- fingerprint: "cart|footer-total-stale|set-qty-0"
  occurrences: 1
```

## 為什麼這件事不只是省事

併成一張、標上 `occurrences: 4`，直接告訴開發者「這不是偶發，是穩定重現」。
**分散成四張單，反而看不出嚴重度。** 去重與 confidence 在這裡合流：複現次數同時餵給「信心」和「這張單多值得修」。
