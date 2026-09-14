# Confidence 計分規則（reference，被 bug-hunter / duty-oncall / issue-quality-gate 讀）

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

證據完整度依 `references/agent-handoff.md` 的介面表判斷：UI 用上表；API 的 requests.jsonl、headers／body 與含前置的重現請求俱全，同樣得 0.20，缺一類得 0.10，只有文字得 0。混合候選取兩側較低分。純 API 不因沒有截圖、console 或瀏覽器 trace 扣分；證據分數不能替代 gate 的完整性檢查。

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

門檻值讀依 `references/config-resolution.md` 解析後的 `sdet-config.yaml`，取 `confidence.min_to_file`（預設 0.7）；比較使用數值 `score`，不得拿 `high` 字串與數字比較。

## 寫回 finding

```yaml
- id: F-01
  project: null
  session: "<date>_<slug>"
  finding_id: F-01
  finding: "checkout 進入時 console 噴 TypeError: cart_items undefined"
  confidence: high            # 0.35+0.25+0.20+0.10+0.10 = 1.00
  score: 1.00
  factors:
    - "4 輪獨立複現(29/34/36/31)  +0.35"
    - "oracle=無 console error   +0.25"
    - "證據齊(截圖/network/console/步驟) +0.20"
    - "分類 product-bug、basis 指到 console.log +0.10"
    - "guest 與 customer 兩身分都中 +0.10"
  next_step: "自動送 bug-verifier"
```

## 校準：`output/calibration.yaml`

格式依 `state-templates/calibration.example.yaml` 與 `docs/state-files.md`。每筆預測以 `(project, session, finding_id)` 唯一定位；fingerprint 用於跨輪關聯，不用來選取要覆寫的列。

1. hunter 寫入 `predicted`、`score`、`predicted_at`，連同識別與 fingerprint。同輪續跑保留原始預測；新一輪另增一列。
2. 獨立 verifier 只產 verdict。呼叫端（通常是 duty-oncall，單獨送驗時為該次編排者）或 gate 核對識別後，寫 `verifier_verdict`、`verifier_verdict_at` 與 `verifier_evidence`；不得把 confidence 或 calibration 傳給 verifier。
3. verifier 結果只用 `confirmed`／`not-reproduced`／`inconclusive`。同一 verdict 重複回填不新增觀察；重驗結果以 `verified_at` 判斷先後，較舊結果不得蓋掉較新結果，歷次 verdict 檔保留。
4. gate 另寫 `gate_result` 與 `gate` 路徑。收到明確人工裁定時，才填 `human_verdict`、`human_verdict_at`、`human_verdict_by` 與 `human_evidence`。既有人工詞彙保留 `confirmed`／`not-reproduced`／`not-a-bug`；缺判定為 null。
5. 缺列、識別不唯一或 verdict 與該列不符時，回報並先修復來源關聯，不猜測填入另一輪。verifier 的 confirmed 只證明現象可重現，不能當成人工判定為 bug。

舊紀錄缺識別或只有 `human_verdict`／`verdict_at` 時，保留原資料。只有證據能確認 project、session、finding 與裁定者時才補欄位或搬到正確欄；來源不明的舊結果不得算入新的人工／獨立驗證指標。不要因新版欄位為 null，就把舊結論猜填進去。

績效分開計算：人工 precision 只用來源明確且已裁定的 high；獨立重現率只用 verifier 有明確結果的 high，排除 null／inconclusive。兩者都回報樣本數與未完成數，分母為零就記 null。

- 打 `high` 卻常被打槍 → **系統性過度自信**，調高門檻或降低「單次複現」的配分。
- 大量後來確認的真 bug 被壓成 `low` → **太保守**，漏報成本高。

**沒有 calibration，confidence 只是沒人驗證過的自我感覺。** 累積的資料同時餵給各輪 `output/sessions/**/runs/*.yaml` 的績效計量。
