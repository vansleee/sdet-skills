# Confidence 計分規則（reference，被 bug-hunter / bug-verifier / issue-quality-gate 讀）

一個 finding 值不值得往下花力氣（送獨立驗證、開單），先看它的 confidence。
**confidence 不是「這是不是 bug」的判決，是「這筆該不該自動往下走」的分流分數。** 蓋章的是 `bug-verifier`。

規則：**每個分數都要說得出憑哪幾個因子**，不接受「我覺得 high」。

## 因子與配分（總分 0–1）

| 因子 | 判準 | 配分 |
|---|---|---|
| 獨立複現次數（最強） | 4 次以上跨輪 / 跨情境 | 0.35 |
| | 3 次 | 0.25 |
| | 2 次 | 0.15 |
| | 只有 1 次 | 0 |
| oracle 強度 | 內部一致性 / API↔UI / 無 console error（不需外部規格） | 0.25 |
| | 規格、需求文件 | 0.20 |
| | 使用者期待、領域常識（主觀） | 0.10 |
| | 無 oracle 命中（needs-spec / inconclusive） | 0（且觸發封頂，見下） |
| 證據完整度 | 截圖 + network + console + 可重現步驟俱全 | 0.20 |
| | 部分（缺其中一類） | 0.10 |
| | 只有文字描述 | 0 |
| 分類確定性 | `product-bug` 且 `basis` 指得到具體證據檔 | 0.10 |
| | 其他分類 / `needs-investigation` | 0 |
| 跨情境一致 | 跨身分（guest ↔ 登入）、跨環境、跨瀏覽器都中 | 0.10 |

## 調整項（modifiers）

| 情況 | 調整 | 為什麼 |
|---|---|---|
| 產品自動回復、終態正確（使用者實際看不到錯誤結果） | **−0.20** | 複現度再高，「值不值得開單」仍存疑，該讓人判 |
| 只在單一環境 / 單一瀏覽器出現，未再驗證 | **−0.10** | 可能是環境噪音而非產品 |

## 封頂規則（硬性，先於加總）

- `verdict` 為 `needs-spec` 或 `inconclusive` → **封頂 low**。沒有 oracle 命中就不准進開單流程。
- 湊不出可重現步驟 → **封頂 low**。（呼應 `triage`／`issue-quality-gate` 的「無法重現不開單」）
- 只出現 1 次且無跨情境佐證 → **封頂 med**。單一因子撐不起 high。

## 分數 → 下一步

| 分數 | 等級 | 下一步 |
|---|---|---|
| ≥ 0.70 | `high` | 可自動送 `bug-verifier` → 走開單流程 |
| 0.40–0.69 | `med` | 進人工複核佇列，不自動開單 |
| < 0.40 | `low` | 擋下，只留紀錄（needs-spec 者記「該問誰」） |

門檻值讀 `config/sdet-config.yaml` 的 `confidence.min_to_file`（預設 0.7）；此處為預設值，專案可調。

## 寫回 finding

```yaml
- id: F-01
  finding: "checkout 進入時 console 噴 TypeError: cart_items undefined"
  confidence: high            # 0.35+0.25+0.20+0.10+0.10 = 1.00
  factors:
    - "4 輪獨立複現(29/34/36/31)  +0.35"
    - "oracle=無 console error   +0.25"
    - "證據齊(截圖/network/console/步驟) +0.20"
    - "分類 product-bug、basis 指到 console.log +0.10"
    - "guest 與 customer 兩身分都中 +0.10"
  next_step: "自動送 bug-verifier"
```

## 校準：`calibration.yaml`

打完分還要知道分數**準不準**。每筆進入下游的 finding 都在 `calibration.yaml` 留一列：`predicted` vs `human_verdict`（由 `bug-verifier` 或人複核後回填）。

- 打 `high` 卻常被打槍 → **系統性過度自信**，調高門檻或降低「單次複現」的配分。
- 大量後來確認的真 bug 被壓成 `low` → **太保守**，漏報成本高。

**沒有 calibration，confidence 只是一個沒人驗證過的自我感覺。** 累積的數據同時餵給 `runs/<date>.yaml` 的績效計量。
