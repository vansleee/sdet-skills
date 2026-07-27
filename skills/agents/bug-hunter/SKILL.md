---
name: bug-hunter
description: 依一份 charter 自主獵一輪 bug：跑完探索、六態標記、異常分類、oracle 判定、confidence 打分、指紋去重、已知誤報過濾，交回一份「已判定、已去重、已濾誤報、標好信心」的候選清單。只找、不開單。使用者說「獵一輪」「找 bug」「跑一輪 hunter」時使用。關鍵詞：獵、找 bug、hunter、候選清單、巡一輪。
disable-model-invocation: true
---

# Bug Hunter (v0.1)

輸入一份 charter（`charters/<slug>.yaml`），輸出一份**候選 issue 清單**。設計理念見 `docs/agents/bug-hunter.md`。

> **它只找、只整理，不開單、不定罪。** 交回的叫「候選」，不叫 bug。蓋章是 `bug-verifier`（獨立重現），能不能開單是 `issue-quality-gate`，開單是 `triage`。
> user-invoked：派它去獵一輪是你有意識下的決定，不該讓模型在背景自行觸發。

## 前置（缺了就停手回報，不要自己編）
- charter 檔存在且可讀（沒有 → 先叫 `exploration-charter` 產一份）。
- `known-false-positives.yaml`、`issues-index.yaml` 存在（沒有 → 從 `*.example.yaml` 複製一份空的，並在回報中說明「本輪未做去重／未濾誤報」）。
- `config/sdet-config.yaml` 的門檻與預算（`confidence.min_to_file`、`budget.max_actions_per_explore`）。

## 執行順序（順序本身就是規格，不得跳號）

1. **探索** — 交給 `explore`：讀 charter、自主選步、記路徑不重做、順手留證。
   先讀同一 charter 過去幾輪的 evidence／`exploration-log.yaml`，**已驗證的不重跑**，把力氣放在還沒測的維度。
2. **標狀態** — 每個觀察交 `structured-result`，標六態之一（pass / fail / blocked / flaky / anomaly / inconclusive）。**不得自創狀態詞彙。**
3. **初篩分類** — 交 `classify-anomaly`：product-bug / environment / test-data / operation-artifact / flaky / known-issue / needs-investigation。
4. **判定** — 對 `product-bug` 與未定案的 anomaly 交 `test-oracle`，取得 `verdict` / `oracle_used` / `basis`。
   **沒有 oracle 命中，不得判 bug**——只能 `needs-spec` / `inconclusive`。
5. **打分** — 依 `references/confidence.md` 算 confidence，寫下用了哪幾個因子與分數，並在 `calibration.yaml` 記一列 `predicted`。
6. **去重** — 依 `references/bug-fingerprint.md` 算指紋，查 `issues-index.yaml`：已存在 → 併入（`occurrences += 1`、append evidence），不列為新候選；`area+signature` 相同但 `trigger` 不同 → 標 `related` 交人判。
7. **濾誤報** — 比對 `known-false-positives.yaml`，命中的移到 `suppressed`，並記下命中哪一條。
8. **封裝與交付** — 剩下的候選交 `evidence-package` 封裝（**可攜、自帶脈絡**，不得寫「如上一步所說」——下游 `bug-verifier` 是沒有本次記憶的獨立 subagent），依 confidence 排序輸出。

## 四道守門（少一道就不算跑完）
| 門 | 擋什麼 | 依據 |
|---|---|---|
| oracle | 「怪」被當成「錯」 | `test-oracle`：沒命中就不是 bug |
| confidence | 沒把握的自動往下走 | `references/confidence.md` 的封頂與門檻 |
| dedup | 同一個 bug 報十次 | `references/bug-fingerprint.md` + `issues-index.yaml` |
| known-FP | 判過的誤報再報一次 | `known-false-positives.yaml` |

## 鐵則
- **不開單、不留言、不碰 issue tracker。** 對外副作用一律留給 `triage`，且要過 `issue-quality-gate`。
- **不定罪。** 輸出欄位叫 `verdict`（來自 oracle）與 `confidence`，不寫「這是 bug」的結論句。
- 嚴守 charter 的 `out_of_bounds`；遇到邊界外的動作停手回報，不自行繞過。
- 守停止條件：達成目標 / `max_steps` / 連續無進展。**沒跑到上限不是缺點**，該收就收。
- 每個候選都要能指到證據檔；指不到的降級成 `inconclusive`，不進候選清單。
- `needs-spec` 一律不得升級成 bug，也**不得**寫進 `known-false-positives.yaml`（沒人拍板前不准消音）。

## 輸出
```yaml
charter: charters/<slug>.yaml
run: <evidence 目錄>
candidates:                      # 依 confidence 排序,尚未開單
  - fingerprint: "<area>|<signature>|<trigger>"
    verdict: bug
    oracle_used: <哪條 oracle>
    basis: "<違反了什麼,指向證據檔>"
    confidence: high             # 附 score 與 factors
    occurrences: <n>
    evidence: <evidence package 路徑>
merged: []                       # 指紋已存在,併入舊單的
related: []                      # 疑似同根因,交人判
suppressed: []                   # 命中 known-FP,附命中哪條
needs_spec: []                   # 無 oracle,附「該問誰」
stopped_because: <達標 | max_steps | 無進展>
```
同時回報一行摘要：**幾個候選、幾筆併入、幾筆壓下、幾筆待規格。**

## 驗收（跑完自己對一次）
- 每個候選都帶著 **oracle 依據 + confidence 因子 + 指紋**了嗎？
- 四道守門**都有生效**嗎（有壓下的、有併入的、needs-spec 沒被硬當 bug）？
- 它是不是**只交清單、沒開任何一張單**？
