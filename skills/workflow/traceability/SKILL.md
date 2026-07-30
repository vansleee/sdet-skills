---
name: traceability
description: 維護「需求 ↔ 測試 ↔ finding」的覆蓋對照，指出哪些需求還沒被覆蓋、哪些測試或 finding 對不到需求。要看追溯、什麼還沒測時使用；`release-signoff` 要覆蓋證據時也用。
---

# Traceability

輸入需求 + 測試 + findings，輸出**覆蓋對照表 + gap 清單 + 孤兒清單**。設計理念見 `docs/workflow/traceability.md`。

> **覆蓋不等於測得好。** 這份表回答「有沒有東西在守」，不回答「守得夠不夠」。報告裡要明說這個限制，不要讓它變成一個好看的百分比。
> 狀態檔：`output/traceability.yaml`（範本 `state-templates/traceability.example.yaml`）。對應規則見 `references/traceability-mapping.md`。

## 輸入 / 輸出
- **輸入**：需求（`knowledge/` 的業務規則 ＋ `output/plans/<slug>.md` 的 in-scope）＋ 測試（掃 `tests/**/*.spec.ts`）＋ findings（`output/sessions/**/findings/F-*.yaml`）＋ issues（`output/issues-index.yaml`）。
- **輸出**：`output/traceability.yaml`（對照表）＋ gap 清單（依風險排序）＋ 孤兒清單（附處置建議）。

## 步驟
1. **收需求**：從 `knowledge/` 抽業務規則，每條給一個穩定的 `req_id`（規則見 `references/traceability-mapping.md`）。
2. **收測試**：掃測試檔，依對應規則（annotation / tag / 命名 / 對照檔）找出它宣告覆蓋哪些 `req_id`。
3. **收 finding / issue**：每筆 finding 與 issue 試著對到 `req_id`。
4. **建對應**：產生三欄關係。對不確定的標 `uncertain`，**不猜**。
5. **標 gap**：沒有任何測試或 finding 對到的需求 → gap。把 gap 整批交 `route-by-risk` 排序（先補高風險的洞）。
6. **標孤兒**（雙向，見下表）。
7. **輸出**：寫 `output/traceability.yaml`（先給人看）＋ 報告 gap 與孤兒。

## 孤兒處置

| 孤兒類型 | 意思 | 處置 |
|---|---|---|
| 測試孤兒 | 測試對不到任何需求 | 交 `test-prune` 評估（**只是候選，不是判死刑**；也可能是需求沒寫進 `knowledge/`，那就補 knowledge）|
| finding 孤兒 | finding 對不到任何需求 | 需求外的意外收穫。**這是好事**（探索本來就該找到規格沒寫的東西），建議補 `knowledge/` 或確認是否為隱性需求 |

## 鐵則
- **不猜對應，不確定就標 `uncertain`。** 灌水的覆蓋率比沒有覆蓋率危險，它會讓人以為有安全網。
- **不算單一覆蓋率數字。** 輸出的是對照表與 gap 清單。一個「覆蓋率 82%」會立刻變成 KPI，然後有人靠寫廢測試把它衝到 95%。
- **測試孤兒不等於該刪。** 先問「是不是需求沒寫進 `knowledge/`」，再談 prune；順序反了會把有用的測試砍掉。
- **對應規則放 `references/traceability-mapping.md`，資料放 `output/traceability.yaml`。** 狀態檔只存資料、不存演算法（見 `docs/state-files.md`）。
- **純讀分析、無副作用：它是對照表，不是執行者。** 指出哪裡有洞，補洞交下游。

## 輸出（格式，非某次執行結果）
```yaml
# output/traceability.yaml（節錄）
generated_at: 2026-07-29
requirements:
  - req_id: REQ-CHECKOUT-005
    source: "knowledge/domains/checkout.md#折扣碼"
    statement: "過期折扣碼不得套用,並顯示明確錯誤"
    covered_by:
      tests:    ["tests/checkout-coupon.spec.ts > rejects expired coupon"]
      findings: ["F-2026-07-24-003"]
    status: covered            # covered | gap | uncertain
  - req_id: REQ-CHECKOUT-006
    source: "knowledge/domains/checkout.md#折扣碼"
    statement: "折扣碼與會員點數不得同時使用"
    covered_by: { tests: [], findings: [] }
    status: gap
    risk_score: 0.71           # 來自 route-by-risk
gaps:
  - { req_id: REQ-CHECKOUT-006, risk_score: 0.71, suggestion: "交 test-planning 排進下輪" }
orphans:
  tests:
    - nodeid: "tests/legacy-promo.spec.ts > applies promo banner"
      note: "對不到任何 req;先確認 knowledge/ 是否漏寫此需求,再談 test-prune"
      route: test-prune
  findings:
    - id: "F-2026-07-26-011"
      note: "折扣碼大小寫不敏感——knowledge/ 未記載,可能是隱性需求"
      route: "補 knowledge/"
caveat: "本表只回答『有沒有東西在守』,不回答『守得夠不夠』;uncertain 3 筆未計入 covered。"
```

## 上下游
上游：`knowledge/`、`test-planning`（in-scope 範圍）、`explore`（findings）、`triage`（issues）。下游：gap 回饋 `test-planning`（排下輪）、測試孤兒交 `test-prune`、覆蓋表交 `release-signoff`（放行證據）、`pipeline-observability`（`coverage_gap` 指標）。
