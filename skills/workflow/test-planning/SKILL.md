---
name: test-planning
description: 把一張 ticket / PRD 轉成「這次要測什麼」的範圍 + 風險排序 + out-of-scope 理由，寫成 plan。規劃一個 sprint / feature 要測什麼時使用；`traceability` 的 gap、`release-signoff` 的補完清單都排回這裡。
---

# Test Planning

輸入一張 ticket / PRD，輸出**測試範圍 + 風險排序 + 每項怎麼測**。workflow 迴圈的入口。設計理念見 `docs/workflow/test-planning.md`。

> **規劃不是列一堆 test case。** 產出是「這輪測什麼、不測什麼、為什麼」——怎麼走留給 `explore`，逐步腳本留給 `test-author`。

## 輸入 / 輸出
- **輸入**：ticket / PRD（連結或內文；GitHub issue 用 `gh issue view <n> --json title,body,labels`）＋ `knowledge/` 產品事實 ＋ 可選：`traceability.yaml` 上一輪的 gap 清單。
- **輸出**：`plans/<slug>.md`——in-scope（含怎麼測）、out-of-scope（**含理由**）、風險排序、開放問題。

## 步驟
1. **讀需求**：抽出「改了什麼、影響誰、驗收條件是什麼」。驗收條件缺失就列進開放問題，不自己補一個。
2. **對照 `knowledge/`**：找出這次變更碰到的既有業務規則。
   - 需求與 `knowledge/` **衝突** → 標 `spec-conflict` 列進開放問題。這是 `test-oracle` 之後的判準素材，**現在就要標出來**，不要等測到一半才發現兩份規格打架。
   - `knowledge/` **沒有**相關事實 → 明寫「本規劃基於假設」，並建議補 `knowledge/`。
3. **圈範圍**：列候選項（改動的流程、被影響的相鄰流程、資料遷移、權限、跨裝置/瀏覽器）。
4. **評風險**：把候選項整批交 `route-by-risk`，拿回 `score` / `route` / `reason`。**不自己發明第二套評分**。
5. **決定怎麼測**：依 route 決定形式（見下表）。
6. **寫 out-of-scope**：`route-by-risk` 判 `skip` 的、以及人為排除的，**逐項寫理由**。
7. **輸出並確認**：把 plan 列給使用者，確認後寫 `plans/<slug>.md`。

## route → 測法

本 skill **只把路線寫進 plan，不代為發動**——plan 是待辦清單，誰去做、什麼時候做是下一步的事。

| route | 怎麼測 | plan 記什麼 |
|---|---|---|
| `must-test` + 行為未知/需求模糊 | 自主探索 | `how: explore`，`next` 指向要產的 `charters/<slug>.yaml`（由 `exploration-charter` 產）|
| `must-test` + 行為明確、要長期守 | 固化成自動化回歸 | `how: test-author`，`next` 寫要幾支測試——**`test-author` 由人發動**（多一支測試就是多一份長期資產）|
| `sample` | 預算夠才做，優先度低於 must-test | 同上，另標 `optional` |
| `skip` | 本輪不測 | 不進 in_scope，列 out-of-scope **並寫理由** |

## 鐵則
- **產品知識只從 `knowledge/` 讀，不內嵌。** 把產品事實寫進本 skill，reuse 就死了。
- **out-of-scope 一定要寫理由。** 「沒測到」和「決定不測」差別很大；三個月後有人問「這塊為什麼沒測」，要查得到。這和 `route-by-risk`「skip 不是丟掉，是留痕」是同一條紀律。
- **風險評分委給 `route-by-risk`。** 兩套評分＝兩個答案＝沒有答案。
- **不寫 test case、不寫程式、不開單。** 本 skill 只決定「測什麼」。
- 規格衝突與知識缺口要**明說**，不要用「合理推測」蓋過去。

## 輸出（格式，非某次執行結果）
```yaml
# plans/<slug>.md 的結構
ticket: "#312 結帳支援折扣碼"
in_scope:
  - target: "套用折扣碼 → 金額重算"
    route: must-test
    score: 0.85
    how: explore
    next: "charters/checkout-coupon.yaml"
  - target: "折扣碼過期 / 無效 / 重複套用"
    route: must-test
    score: 0.72
    how: test-author
    next: "回歸測試 3 支"
  - target: "訂單明細顯示折扣行"
    route: sample
    score: 0.44
    how: explore
    next: "預算夠才做（optional）"
out_of_scope:
  - target: "後台折扣碼管理介面"
    reason: "本次未改動；route-by-risk score 0.18 → skip"
  - target: "IE11 相容性"
    reason: "產品已停止支援（knowledge/browser-support.md）"
open_questions:
  - "折扣碼與會員點數可否同時使用？PRD 未寫，knowledge/ 也無 → spec-conflict，需 PM 確認"
knowledge_gaps:
  - "knowledge/ 無折扣相關業務規則，本規劃基於 PRD 假設，建議補 knowledge/domains/discount.md"
```

## 上下游
上游：ticket / PRD、`traceability`（上一輪 gap 回饋）。下游：`route-by-risk`（評分）、`exploration-charter` → `explore`（探索路線）、`test-author`（固化路線）、`traceability`（本 plan 的範圍是需求清單來源之一）。
