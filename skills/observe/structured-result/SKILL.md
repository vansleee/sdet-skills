---
name: structured-result
description: 把測試/觀察結果表達成超越 Pass/Fail 的結構化狀態（pass / fail / blocked / flaky / inconclusive / anomaly），每筆附證據。回報結果、記錄檢查點、判定狀態時使用。關鍵詞：結果、pass、fail、blocked、flaky、狀態、結構化、results。
---

# Structured Result

一次探索的結果＝一份 `results.yaml`，每個檢查點一筆，放進當次 evidence package。設計理念見 `docs/observe/structured-result.md`。

## 狀態（status，必填，六選一）
**通過只有一種標準（行為符合預期），失敗有五種原因。** 六選一就是把那五種拆開。

| status | 用於 |
|---|---|
| pass | 預期行為出現（含錯誤情境被正確擋下）|
| fail | 確定不符預期 → 候選 bug |
| blocked | 前置壞了、沒測到判斷點（非產品錯）|
| flaky | 有時 pass 有時 fail（填 repro_rate）|
| anomaly | 可疑但還不判定：範圍外，或範圍內但要有規格才判得動（只描述）|
| inconclusive | 測到了，但證據不足以判斷 |

## 三組界線（填錯最多的地方）
| 分不清 | 判準 |
|---|---|
| blocked ／ inconclusive | **沒測到判斷點是 blocked；測到了但看不出來是 inconclusive。** |
| fail ／ anomaly | **有明確預期可比對就是 fail；要先有規格才判得動就是 anomaly。** 例：數量填 `-5` 顯示負金額＝fail（本來就該擋）；填 `0` 導致總計沒重算＝anomaly（要看規格怎麼定義）|
| flaky ／ 穩定壞掉 | **能穩定重現就是 fail，不是 flaky。** 時好時壞才是 flaky，且要重跑幾次量出 `repro_rate` 才填 |

## 每筆欄位
`id` / `check` / `status` / `expected`+`actual`（pass·fail）/ `reason`·`detail`（blocked·inconclusive·anomaly）/ `repro_rate`（flaky）/ `evidence[]`（指向 evidence 包，可用 `file#Ln`）

## 規則
- status 必填、六選一；每筆至少一項 evidence（blocked/inconclusive 也要附「被什麼擋／為何判不了」）。
- 錯誤情境被正確擋下＝pass，不是 fail。
- anomaly 只描述、不判定是否為 bug。
- 只有 fail（及經分類確認的 anomaly）可往下開單；blocked / inconclusive 不得直接開 Issue。
- 寫 results.yaml 前，先讀過本次 evidence 包裡所有原始檔（console.log / network.log 等）。每一則 error / warning 至少要對應一筆 result；判斷為預期行為也要留一筆 pass 或 anomaly 交代理由，不能只寫進 notes.md 就整批省略。
- **UI 全綠但 console 有紅字**：與受測行為無關 → `pass`（留一筆交代理由）；與受測行為有關 → `anomaly` 並寫明關聯。不得因為畫面沒問題就整批忽略。
- **同一個現象可以拆成兩筆。** 例：帳號被鎖，「擋得對」是 pass、「因此測不到的檢查點」是 blocked。不要混成一筆。

## 範例
```yaml
results:
  - id: R-03
    check: "購物車數量欄輸入 -5"
    status: fail
    expected: "數量欄應拒絕負數(前端擋下並提示)"
    actual: "前端零驗證,Total 顯示 -$70.75;變更未觸發 API 呼叫(純前端),reload 後回復 1、未寫入後端"
    evidence: [network.log#L8, 05-qty-negative.png]
  - id: R-04
    check: "登入後的結帳檢查"
    status: blocked
    reason: "測試帳號回 423 Locked,無法登入,測不到判斷點"
    evidence: [network.log#L12, 06-account-locked.png]
  - id: R-05
    check: "購物車數量欄輸入 0"
    status: anomaly
    detail: "單列 Total 變 $0.00,但頁尾總計未重算(仍 $14.15);未觸發 API 呼叫(純前端)"
    evidence: [network.log#L15, 07-qty-zero.png]
```
