---
name: evidence-package
description: 執行測試、操作產品、驗證功能或探索頁面時，蒐集並整理測試證據（截圖 / console / network / trace）。凡是會改變頁面狀態的操作序列（登入、送出、建立資料）都必須使用。關鍵詞：測試、驗證、重現、截圖、證據、trace、console、network。
---

# Evidence Package

Playwright 產生證據，本 skill 只負責組裝成一份可攜證據包 + manifest。設計理念見 `docs/observe/evidence-package.md`。

## 開工前
1. 建資料夾 `evidence/<YYYYMMDD>-<任務代號>/`。
2. 確認 trace：工具集有 `browser_start_tracing` → 呼叫它開錄；沒有 → 走降級規則、manifest 標「無 trace」。

## 執行中
3. 關鍵操作前後各截圖，檔名 `<步驟>-<動作>-<before|after>.png`。關鍵操作＝任何送出、頁面跳轉、將在結論引用的畫面。
4. 全程監聽 console → `console.log`。
5. 全程記錄 API（xhr/fetch）method/URL/狀態碼 → `network.log`；非 2xx 全部標記。

## 對照
6. UI ↔ API：API 真實狀態碼 vs 畫面結果。不一致（畫面成功、API 非 2xx）＝ finding，寫進 notes 並指向 `network.log`。

## 收工
7. 有開 trace → `browser_stop_tracing`，再 `bash scripts/pack-trace.sh evidence/<YYYYMMDD>-<任務代號>/`。
8. 寫 `manifest.md`：任務目標、環境、時間、Trace 狀態、UI↔API 對照結論、步驟↔截圖對應、各檔位置。
9. 寫 `notes.md`：目標、步驟（每步引截圖）、觀察（只寫看到的）、結論（每條至少一項證據）。

## 產出物
    evidence/<YYYYMMDD>-<任務代號>/
    ├── manifest.md
    ├── notes.md
    ├── console.log
    ├── network.log
    ├── trace.zip          # 降級時可能無
    └── NN-<動作>-before|after.png

## 鐵則
- 缺 trace：煙霧測試可降級（截圖+console+network 頂替、manifest 聲明）；要開 bug 單則停手回報。
- 「畫面說成功」必須有 API 狀態碼佐證。
- 無證據的觀察標「未留證」、降為待確認。
- 證據夾外的檔案不得引用。
- 產出形狀固定，供 bug-verifier / triage 直接讀。
