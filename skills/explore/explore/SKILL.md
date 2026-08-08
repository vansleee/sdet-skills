---
name: explore
description: 依照一份 Exploration Charter 自主探索產品：觀察現況、自己決定下一步、記住走過的路、並且留下證據，產生候選 findings。當需要「自主探索」「給方向自己測」「不用寫腳本逐步地探索某流程」時使用。
  關鍵詞：探索、自主、charter、exploration、找問題。
---

# Explore (v0.1)

輸入一份 charter（`charters/<slug>.yaml`，或 inline 的：目標 / 範圍 / oracles / 邊界），自主探索並產出 findings。設計理念見 `docs/explore/explore.md`。

> v0.1：本版把三大失敗模式的防呆寫死（見下方鐵則）。跑過真實 session 後再依表現收緊。charter 由 `exploration-charter` 產生；判定交 `test-oracle` / `classify-anomaly`；留證畫面側交 `evidence-package`、端點側交 `api-evidence`。

## 開跑前：解析 project
讀 charter 的 `charter.project`，照 `references/config-resolution.md` 解析出這一輪要讀的 `config/<project>/product-context.md` 與 `sdet-config.yaml`，取 base URL、登入方式、trace 來源、API 段與門檻。**解析不到就停手回報，不得回退讀扁平 `config/`**，否則會拿別的產品的設定去打這一站。第一次讀完在輸出裡覆誦一次 slug 與 base URL。charter 沒有 `project` 時不查 config，target URL 由 charter 的 `target` 自己帶。解析出的 slug 往下傳給 `evidence-package`、`api-evidence`、`test-oracle`，下游不重新解析。

## 探索迴圈（每一步）
1. **讀 charter**：目標、範圍、oracles、out-of-bounds。
2. **觀察現況**：`playwright-cli snapshot` 看目前畫面與可操作元素，動作用它回傳的 ref（`playwright-cli click e6`）。畫面一變就重新 snapshot，別拿舊 ref 動作。
3. **宣告下一步**：先寫「我現在看到什麼 + 為什麼選這個下一步（朝 charter 哪個目標）」，**且必須引用當前畫面的具體證據**，再動作。
4. **記路徑**：動作前查 `output/sessions/<date>_<slug>/exploration-log.yaml`（走過的頁面 / 試過的操作），**做過的不重做**；動作後把這步寫回去。
5. **順手留證**：關鍵操作交 `evidence-package`（截圖 / console / network）。疑似問題標成 `anomaly` /「待確認」，**不當場定罪**。
6. **檢查停止條件**（見下）。

## API 探索迴圈（charter 有 `endpoints` 時，與上面的迴圈交替跑）
畫面側用 `snapshot` 取 ref，端點側沒有 ref 可取，觀察的單位換成請求與回應。留證交 `api-evidence`，判定一樣交 `test-oracle`。

1. **列端點**：優先讀解析後的 `product-context.md` 的契約來源（OpenAPI／GraphQL schema）；沒有契約就從既有 `output/evidence/**/network.log` 或畫面操作時實際打出去的請求反推。反推出來的清單要在 log 註明「來源＝觀察，非契約」，它一定不完整。
2. **先打一次正常請求**當基準：記下正常的狀態碼、回應結構、耗時。沒有基準就沒得比，後面每個異常都會變成「不確定本來是不是這樣」。
3. **宣告下一步**：跟畫面側同一條規矩，寫「我打算戳哪個假設」（讀 `references/heuristics.md` 的 API 列），且引用基準回應的具體內容。
4. **打請求**：交 `api-evidence` 執行與留證。有副作用的請求先確認，`out_of_bounds` 與「不得碰的端點」一律不碰。
5. **記路徑**：寫回 `exploration-log.yaml`，單位是「端點＋方法＋這次改動的變因」。同一個端點換一個變因算新的一步，重打完全相同的請求不算。
6. **檢查停止條件**（與畫面側共用 `max_steps`）。

## 停止條件（一定要有）
- 達成 charter 目標，或
- 到 `max_steps`（解析後的 `sdet-config.yaml`，預設 15），或
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
- **端點不會自己現身。** 畫面沒呼叫過的端點（舊版本遺留、只給行動端用、只給管理端用）不會出現在 network 紀錄裡，卻常常是授權最鬆的一批。有契約就照契約列，沒契約就在 log 寫明清單來源是觀察、涵蓋不完整，不准拿「畫面打過的都試了」當走完。

## 輸出（路徑固定，全部落在 `output/` 底下）

```
    output/sessions/<YYYY-MM-DD>_<slug>/
    ├── exploration-log.yaml               # 這次走過的路徑（供續跑與人審）；開頭記 project slug 與解析到的 config 路徑
    └── findings/F-NNN-<slug>.yaml         # 一筆一檔，候選發現

    output/evidence/<YYYYMMDD>-<slug>/     # 截圖 / console / network，由 evidence-package 建
```

- `findings`：每筆附證據、狀態＝fail/anomaly、待確認理由 → 交 `structured-result` / `classify-anomaly`。
- 不得寫在 repo 根目錄（`findings/`、`evidence/` 都不行）；完整檔案地圖見 `docs/state-files.md`。
