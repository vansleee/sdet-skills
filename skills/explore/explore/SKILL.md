---
name: explore
description: 依一份 Exploration Charter 自主探索產品：觀察現況、自己決定下一步、記住走過的路、順手留證，產出候選 findings。當要「自主探索」「給方向自己測」「不寫逐步腳本地探索某流程」時使用。關鍵詞：探索、自主、charter、exploration、找問題。
---

# Explore (v0.1)

輸入一份 charter（`charters/<slug>.yaml`，或 inline 的：目標 / 範圍 / oracles / 邊界），自主探索並產出 findings。設計理念見 `docs/explore/explore.md`。

> v0.1：本版把三大失敗模式的防呆寫死（見下方鐵則）。跑過真實 session 後再依表現收緊。charter 由 `exploration-charter` 產生；判定交 `test-oracle` / `classify-anomaly`；留證交 `evidence-package`。

## 探索迴圈（每一步）
1. **讀 charter**：目標、範圍、oracles、out-of-bounds。
2. **觀察現況**：`browser_snapshot` / `read_page` 看目前畫面與可操作元素。
3. **宣告下一步**：先寫「我現在看到什麼 + 為什麼選這個下一步（朝 charter 哪個目標）」，**且必須引用當前畫面的具體證據**，再動作。
4. **記路徑**：動作前查 `exploration-log.yaml`（走過的頁面 / 試過的操作），**做過的不重做**；動作後把這步寫回去。
5. **順手留證**：關鍵操作交 `evidence-package`（截圖 / console / network）。疑似問題標成 `anomaly` /「待確認」，**不當場定罪**。
6. **檢查停止條件**（見下）。

## 停止條件（一定要有）
- 達成 charter 目標，或
- 到 `max_steps`（`config/sdet-config.yaml`，預設 15），或
- 連續 N 步無進展（偵測到打轉）→ 停手、回報卡在哪。

## 邊界
嚴守 charter 的 out-of-bounds（例：不註冊、不付款、不對 production 寫入、只用測試帳號）。遇邊界外的動作 → 停手回報，不自行繞過。

## 鐵則（三大失敗模式的解藥）
- **防亂點**：每一步都要有理由且引用當前畫面證據，否則不動作。
- **防鬼打牆**：做過的操作/頁面不重複（靠 `exploration-log.yaml`）。
- **防幻覺**：沒有證據不宣稱「已完成 / 是 bug」；只描述看到的,判定留給 oracle。

## 輸出
- `findings`：候選發現清單（每筆附證據、狀態=fail/anomaly、待確認理由）→ 交 `structured-result` / `classify-anomaly`。
- `exploration-log.yaml`：這次走過的路徑（供續跑與人審)。
