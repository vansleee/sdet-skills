---
name: bug-hunter
description: 依一份 charter 獵一輪 bug，交回已判定、已去重、標好 confidence 的候選清單。只找、不開單。使用者要找 bug、巡一輪、跑 hunter 時使用；`duty-oncall` 或任何 skill 需要候選清單時也用。
---

# Bug Hunter

輸入一份 charter（`charters/<slug>.yaml`），輸出一份**候選 issue 清單**。設計理念見 `docs/agents/bug-hunter.md`。

> **它只找、只整理，不開單、不定罪。** 交回的叫「候選」，不叫 bug。蓋章是 `bug-verifier`（獨立重現），能不能開單是 `issue-quality-gate`，開單是 `triage`。
> model-invoked：`duty-oncall` 要能在值班中直接調用它。授權管制不靠「叫不到」，靠 `config/governance.yaml` 與各站自己的確認規則。

## 前置（缺了就停手回報，不要自己編）
- charter 檔存在且可讀（沒有 → 先叫 `exploration-charter` 產一份）。
- `output/known-false-positives.yaml`、`output/issues-index.yaml` 存在（沒有 → 從 `state-templates/` 對應範本複製一份空的，並在回報中說明「本輪未做去重／未濾誤報」）。
- 讀 `references/config-resolution.md` 解析 project 與 `sdet-config.yaml` 的門檻、預算。交接前讀 `references/agent-handoff.md`，全程保留 `project`、`session`、`finding_id` 與介面欄位。

## 執行順序（順序本身就是規格，不得跳號）

1. **探索** — 交給 `explore`：讀 charter、自主選步、記路徑不重做、順手留證。
   先讀同一 charter 過去幾輪的 evidence／`exploration-log.yaml`，**已驗證的不重跑**，把力氣放在還沒測的維度。
2. **標狀態** — 每個觀察交 `structured-result`，標六態之一（pass / fail / blocked / flaky / anomaly / inconclusive）。**六態封閉，只從這六個裡挑**。
3. **初篩分類** — 交 `classify-anomaly`：product-bug / environment / test-data / operation-artifact / flaky / known-issue / needs-investigation。
4. **判定** — 對 `product-bug` 與未定案的 anomaly 交 `test-oracle`，取得 `verdict` / `oracle_used` / `basis`。
   **沒有 oracle 命中，不得判 bug**，只能 `needs-spec` / `inconclusive`。
5. **打分** — 依 `references/confidence.md` 按 UI／API 證據算 confidence，寫下 `score` 與因子；在 `output/calibration.yaml` 以 `(project, session, finding_id)` 記本次 `predicted`，不得覆寫其他輪的預測。
6. **去重** — 依 `references/bug-fingerprint.md` 算指紋、查 `output/issues-index.yaml`，照該文「比對與合併」四規則分流（併入 / related / 新候選）。
7. **濾誤報** — 比對 `output/known-false-positives.yaml` 中同 project 的規則，命中的移到 `suppressed`，並記下命中哪一條。舊規則缺 project 時先核對來源，不跨專案套用。
8. **封裝與交付** — UI 交 `evidence-package`、API 交 `api-evidence`，混合候選共用一份完整包。依 `references/agent-handoff.md` 另建 `blind/manifest.yaml` 與必要原始證據；完整包留給 gate／人複核，獨立 verifier 只收盲驗輸入。依 confidence 排序輸出候選。

步驟 4–7 就是**四道守門**（oracle / confidence / dedup / known-FP），少一道就不算跑完；判準本身以 `issue-quality-gate` 的六條表與 `references/` 為準，這裡不重述。

## 鐵則
- **不開單、不留言、不碰 issue tracker。** 對外副作用一律留給 `triage`，且要過 `issue-quality-gate`。
- **只給判準，不下結論。** 輸出欄位是 `verdict`（來自 oracle）與 `confidence`；「這是 bug」的結論句留給 `issue-quality-gate`。
- 嚴守 charter 的 `out_of_bounds`；遇到邊界外的動作停手回報，不自行繞過。
- 守停止條件：達成目標 / `max_steps` / 連續無進展。**沒跑到上限不是缺點**，該收就收。
- 每個候選都要能指到證據檔；指不到的降級成 `inconclusive`，不進候選清單。
- `needs-spec` 一律不得升級成 bug，也**不得**寫進 `output/known-false-positives.yaml`（沒人拍板前不准消音）。

## 輸出
```yaml
project: null                   # 有專案時填 slug，全鏈沿用
session: <date>_<slug>
charter: charters/<slug>.yaml
run: <evidence 目錄>
candidates:                      # 依 confidence 排序,尚未開單
  - finding_id: F-001
    project: null
    session: <date>_<slug>
    level: ui
    evidence_levels: [ui]
    fingerprint: "<area>|<signature>|<trigger>"
    category: product-bug
    verdict: bug
    oracle_used: <哪條 oracle>
    basis: "<違反了什麼,指向證據檔>"
    confidence: high
    score: <0 到 1>
    factors: []                  # 列出各因子與配分
    occurrences: <n>
    evidence: <evidence package 路徑>
    verification_input: <evidence package 路徑>/blind/manifest.yaml
merged: []                       # 指紋已存在,併入舊單的
related: []                      # 疑似同根因,交人判
suppressed: []                   # 命中 known-FP,附命中哪條
needs_spec: []                   # 無 oracle,附「該問誰」
stopped_because: <達標 | max_steps | 無進展>
```
同時回報一行摘要：**幾個候選、幾筆併入、幾筆壓下、幾筆待規格。**

## 驗收（跑完自己對一次）
- 每個候選都帶著 **oracle 依據 + confidence 因子 + 指紋**了嗎？
- 四道守門逐道**留了紀錄**嗎（`merged` / `suppressed` / `needs_spec` 三欄即使 0 筆也要出現）？
- 它是不是**只交清單、沒開任何一張單**？
- 盲驗包是否排除結論與評分，且各筆識別與 project 完整？
