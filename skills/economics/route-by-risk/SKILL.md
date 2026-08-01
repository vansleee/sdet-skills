---
name: route-by-risk
description: 用風險決定要不要測、先測什麼，放在 pipeline 最前面當閘門。
---

# Route by Risk

輸入一批候選測試/探索目標，輸出每一項的風險分數與 route 決定（`must-test` / `sample` / `skip`），供上游排序、下游收斂範圍。**放在最前面**：先決定值不值得測，再決定怎麼測。設計理念見 `docs/economics/route-by-risk.md`。

## 輸入 / 輸出
- **輸入**：一批候選項（模組、路由、feature、PR 變更檔案清單，或 `test-planning` 圈出的範圍），可選：本輪預算上限（讀 `config/sdet-config.yaml` 的 `budget`）。
- **輸出**：每個候選項的 `score` / `route` / `factors` / `reason`（見下方格式），交回呼叫者（`test-planning` 排範圍、`ci-pipeline` / `duty-oncall` 決定本輪跑什麼）。本 skill 不自己跑測試、不自己開 PR。

## 風險因子（讀 `config/sdet-config.yaml` 的 `risk.weights`）

| 因子 | 訊號來源 | 沒資料時 |
|---|---|---|
| `change_frequency` | 近期改動頻率（該模組相關檔案的 commit 數/頻率） | 用中性值 0.5，並在 `factors` 註記「資料源缺」 |
| `user_traffic` | `knowledge/` 是否標記為關鍵路徑/主要轉換流程 | 同上，用中性值 0.5 |
| `past_failures` | `output/issues-index.yaml` 該 area 命中次數（確認過的 bug/regression） | 無命中記錄視為 0（真的沒有，不是缺資料） |

每個因子先估成 0–1 的 `factor_value`，`score = Σ(factor_value × weight)`。權重預設 `{change_frequency: 0.4, user_traffic: 0.4, past_failures: 0.2}`（見 `config/sdet-config.example.yaml`），專案可調。

## Route 門檻（預設值，可依專案調整）

| score | route | 意思 |
|---|---|---|
| ≥ 0.6 | `must-test` | 本輪一定要測/探索 |
| 0.3–0.6 | `sample` | 預算/時間夠才做，優先度低於 must-test |
| < 0.3 | `skip` | 本輪不測 |

## 附帶輸出：建議的測試層級

決定「要測」之後，順手給一個 `level` 建議（`api` / `ui` / `both`），判準照 `references/test-design.md` 第 0 節：規則、計算、驗證、權限 → `api`；呈現、互動、可及性 → `ui`；整合風險 → `both`，但 UI 只留一條代表路徑。

這只是建議，不是決定：呼叫者（`test-planning`）拿它去挑 `how`（`api-test-author` 還是 `test-author`）。判不出來就寫 `level: unknown` 並說明，**不要預設 `ui`**。「不確定就用 UI 測」正是套件長成一堆慢測試的來源。

## 規則
- **`skip` 不是丟掉，是留痕。** 每個 `skip` 都要寫 `reason`，交回呼叫者的紀錄裡；本 skill 不做「靜默排除」。之後有人要回頭查「這塊為什麼沒測到」，要查得到。
- **資料源缺不等於低風險。** 缺資料一律用中性值 0.5，不准直接判 0（那會讓「沒人量過的風險」被錯誤地當成「沒風險」）。
- **本 skill 只評分排序，不做「不可逆」決定。** 真的要跳過某塊完全不測，屬於會漏掉風險的決定；若專案在 `config/governance.yaml` 啟用分級，這類決定歸 `needs_review`，由人偶爾抽查，不是本 skill 自己拍板。
- 只讀 `config/`、`knowledge/`、`output/issues-index.yaml`，不把任何專案專屬的風險判準寫死在本 skill 裡。

## 輸出（格式，非某次執行結果）
```yaml
target: "checkout module"
score: 0.82
route: must-test
level: api                 # api | ui | both | unknown（建議，非決定）
level_reason: "折扣與稅額計算是後端規則,分支多;UI 只需一條代表路徑接起來"
factors:
  - "change_frequency: 0.9（近 7 天 12 次 commit）× 0.4 = 0.36"
  - "user_traffic: 1.0（knowledge/ 標記為主要轉換路徑）× 0.4 = 0.40"
  - "past_failures: 0.3（output/issues-index.yaml 近 30 天 2 筆確認 bug）× 0.2 = 0.06"
reason: "高改動頻率 + 主要轉換路徑，score 超過 must-test 門檻"
```

## 上下游
上游：`test-planning`（圈出候選範圍）或直接吃 PR 變更檔案清單。下游：`ci-pipeline` / `duty-oncall` 依 route 決定本輪跑什麼、`explore` 的 charter 可依此排優先序。與 `economics/sdet-economics` 分工：本 skill 決定「要不要測」，`sdet-economics` 決定「用什麼成本測」。
