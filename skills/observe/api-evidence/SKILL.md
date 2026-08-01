---
name: api-evidence
description: 直接打 API 驗證或探索端點時，蒐集並整理 API 證據（請求與回應對、狀態碼、耗時、可重放的 repro 指令）。凡是不經畫面、直接對端點發請求的動作都必須使用。關鍵詞：API、端點、endpoint、curl、request、response、狀態碼、契約、schema、證據。
---

# API Evidence

`evidence-package` 的姊妹 skill：沒有畫面可截時，證據是**請求與回應本身**。輸出形狀比照 `evidence-package`，供 `test-oracle` / `bug-verifier` / `triage` 直接讀。設計理念見 `docs/observe/api-evidence.md`。

## 用哪一支
- 操作經過畫面（點按鈕、送表單）→ `evidence-package`，它的 `network.log` 已經涵蓋。
- 不經畫面、直接打端點（探索端點、驗授權邊界、驗契約）→ 本 skill。
- 同一任務兩者都有 → 共用**同一個** `$D`，`evidence-package` 收畫面側，本 skill 把 `requests.jsonl` 與 `raw/` 併進去，manifest 只寫一份。

## 開工前
1. 讀 `product-context.md`（哪一份由呼叫端傳來的 project slug 決定，規則見 `references/config-resolution.md`）的「API」段取 API base URL、認證方式、憑證的 env 變數名、契約來源、速率限制、**不得碰的端點**。缺這段就停手回報，不要自己猜 base URL。
2. 建資料夾 `output/evidence/<YYYYMMDD>-<任務代號>/`（以下用 `$D`）與 `$D/raw/`。
3. 憑證只從環境變數取，**指令裡一律寫 `$VAR`，不展開成值**。

## 執行中
4. 一個請求一個序號，狀態碼、耗時、body 一起留。範本：

       curl -sS -X GET "$API_BASE/products?page=1" \
         -H "Authorization: Bearer $API_TOKEN" \
         -D "$D/raw/07-products.headers" \
         -o "$D/raw/07-products.body.json" \
         -w '{"n":7,"method":"GET","path":"/products?page=1","status":%{http_code},"ms":%{time_total},"bytes":%{size_download}}\n' \
         >> "$D/requests.jsonl"

   `-w` 那行進 `requests.jsonl`（一行一請求、可直接 grep 非 2xx），headers 與 body 進 `raw/`。**失敗的請求照留**，它們往往才是發現。
5. 同步把這一行的可重放版本追加進 `$D/repro.sh`（同一條指令，憑證維持 `$VAR`）。
6. 有副作用的請求（`POST` / `PUT` / `PATCH` / `DELETE`、寄信、扣款）**送出前先列給使用者確認**，並照 `config/governance.yaml` 的分級走。product-context 標為「不得碰」的端點一律不打。

## 對照
7. 掃 `requests.jsonl` 的 `status`，非 2xx 全部標記；同時檢查「`200` 但 body 是錯誤訊息」這種狀態碼與語意不符的情形。判定交 `test-oracle` 的 API 專屬 oracle，本 skill 只留證、不定罪。
8. 任務同時有畫面時，做 UI ↔ API 對照，結論寫進 manifest。

## 收工
9. 寫 `manifest.md`：任務目標、環境與 API base URL、時間、認證方式（只寫變數名）、請求總數與非 2xx 數、契約來源（有無）、各檔位置。
10. 寫 `notes.md`：目標、每個請求做了什麼（引 `requests.jsonl` 的序號）、觀察（只寫看到的）、結論（每條至少一項證據）。

## 產出物
    output/evidence/<YYYYMMDD>-<任務代號>/
    ├── manifest.md
    ├── notes.md
    ├── requests.jsonl     # 一行一請求：n / method / path / status / ms / bytes
    ├── repro.sh           # 可直接重跑的請求序列，憑證維持 $VAR
    └── raw/NN-<動作>.headers|.body.json

## 鐵則
- **憑證絕不落地。** token、密碼、cookie 值不得寫進 `requests.jsonl`、`repro.sh`、`raw/` 或 manifest；`raw/*.headers` 裡的 `Authorization` 與 `Set-Cookie` 收工前改成 `<redacted>`。
- **回應 body 沒留就不算留證。** 只記狀態碼判不動契約、也判不動狀態碼語意。
- **每個請求都要能重放。** `repro.sh` 跑不起來的證據，`bug-verifier` 沒辦法盲驗。
- **不省略前置請求。** 拿 token、建前置資料那幾步一樣要進 `requests.jsonl`，否則別人重現不出來。
- **有副作用的請求先確認**，證據夾外的檔案不得引用。
- **`429` 先當自己打太快**，對照 product-context 的速率限制，不當場記成產品 bug。
