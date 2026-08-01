---
name: explore
description: 依一份 Exploration Charter 自主探索產品：觀察現況、自己決定下一步、記住走過的路、順手留證，產出候選 findings。當要「自主探索」「給方向自己測」「不寫逐步腳本地探索某流程」時使用。關鍵詞：探索、自主、charter、exploration、找問題。
---

# Explore (v0.1)

輸入一份 charter（`charters/<slug>.yaml`，或 inline 的：目標 / 範圍 / oracles / 邊界），自主探索並產出 findings。設計理念見 `docs/explore/explore.md`。

> v0.1：本版把三大失敗模式的防呆寫死（見下方鐵則）。跑過真實 session 後再依表現收緊。charter 由 `exploration-charter` 產生；判定交 `test-oracle` / `classify-anomaly`；留證交 `evidence-package`。

## 探索迴圈（每一步）
1. **讀 charter**：目標、範圍、oracles、out-of-bounds。
2. **觀察現況**：`playwright-cli snapshot` 看目前畫面與可操作元素，動作用它回傳的 ref（`playwright-cli click e6`）。畫面一變就重新 snapshot，別拿舊 ref 動作。
3. **宣告下一步**：先寫「我現在看到什麼 + 為什麼選這個下一步（朝 charter 哪個目標）」，**且必須引用當前畫面的具體證據**，再動作。
4. **記路徑**：動作前查 `output/sessions/<date>_<slug>/exploration-log.yaml`（走過的頁面 / 試過的操作），**做過的不重做**；動作後把這步寫回去。
5. **順手留證**：關鍵操作交 `evidence-package`（截圖 / console / network）。疑似問題標成 `anomaly` /「待確認」，**不當場定罪**。
6. **檢查停止條件**（見下）。

## 停止條件（一定要有）
- 達成 charter 目標，或
- 到 `max_steps`（`config/sdet-config.yaml`，預設 15），或
- 連續 N 步無進展（偵測到打轉）→ 停手、回報卡在哪。

停止前先跑一次「覆蓋鐵則」自檢，把結果寫進 `exploration-log.yaml` 的 `stop_reason`。**「charter 範圍走完」是自我宣告，不是覆蓋證明**；沒有外部判準時，至少要說得出哪幾條鐵則過了、哪幾條沒過。

## 邊界
嚴守 charter 的 out-of-bounds（例：不註冊、不付款、不對 production 寫入、只用測試帳號）。遇邊界外的動作 → 停手回報，不自行繞過。

## 鐵則（三大失敗模式的解藥）
- **防亂點**：每一步都要有理由且引用當前畫面證據，否則不動作。
- **防鬼打牆**：做過的操作/頁面不重複（靠 `exploration-log.yaml`）。
- **防幻覺**：沒有證據不宣稱「已完成 / 是 bug」；只描述看到的，判定留給 oracle。

## 覆蓋鐵則（防漏檢）
上面三條管「別亂跑」，這五條管「別漏看」。收工前逐條自檢，任何一條沒過就別宣告走完。校準依據見 `docs/explore/explore.md`。

- **每條相對判準配一條絕對判準。** 「跟其他 N 個一樣」只抓得到離群值，整批一致地錯就沒有訊號。內部一致性 oracle 一律再補一條不靠比對的判準（量圖高等不等於容器高，別問它跟其他張一不一樣高）。
- **靜態解析只用來選目標，不用來下結論。** `fetch` 加 DOM 屬性讀取可以快速圈出候選，但行為改寫藏在事件處理器裡。判「這個連結沒問題」之前，點過它。
- **通過條件寫到終態。** 不准拿「可送出」「有回應」「沒報錯」當 pass，要等到成功、失敗或逾時三者之一才記結果。
- **控制項換頁重測，變因交叉配對。** 同一個控制項在不同頁面常是不同實作；選項乘數量、篩選乘排序這類組合狀態要明列配對表，不能各測各的。
- **把沒被畫面主動端出來的東西列進計畫。** 收合的元件、要點開才長出 DOM 的區塊、主流程沒連過去的頁面，都要在 charter 裡寫到 URL 或元件層級，不能靠功能區塊名稱隱含涵蓋。

## 輸出（路徑固定，全部落在 `output/` 底下）
    output/sessions/<YYYY-MM-DD>_<slug>/
    ├── exploration-log.yaml               # 這次走過的路徑（供續跑與人審）
    └── findings/F-NNN-<slug>.yaml         # 一筆一檔，候選發現

    output/evidence/<YYYYMMDD>-<slug>/     # 截圖 / console / network，由 evidence-package 建

- `findings`：每筆附證據、狀態＝fail/anomaly、待確認理由 → 交 `structured-result` / `classify-anomaly`。
- 不得寫在 repo 根目錄（`findings/`、`evidence/` 都不行）；完整檔案地圖見 `docs/state-files.md`。
