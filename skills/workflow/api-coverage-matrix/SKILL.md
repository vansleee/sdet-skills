---
name: api-coverage-matrix
description: 把一份 API 設計文件（design doc、OpenAPI、Confluence spec）轉成一張逐端點、逐方法、正負向情境的優先序測試案例矩陣，含代表性 payload、回應與可重現的 cURL。範圍已經由 test-planning 或人決定要枚舉時使用；產出餵 api-test-author 的待辦、traceability 的需求來源。
disable-model-invocation: true
---

# API Coverage Matrix

輸入一份 API 設計文件，輸出**一張逐端點 × 逐方法 × 正負向情境的優先序案例矩陣**，附代表性 payload、回應與可重現的 cURL。設計理念見 `docs/workflow/api-coverage-matrix.md`。

> **不是 test-planning 的替代品。** 範圍與「值不值得測」由 `test-planning`／`route-by-risk` 決定；本 skill 只在已經判定要枚舉某段 API surface 之後動手。枚舉出來的優先序回答「先做哪個、先自動化哪個」，不是「要不要做」，兩者是不同問題，不衝突。
> **每一列是需求單位，不是操作手冊。** 近似 `traceability` 的 `req_id`：可獨立驗證、有優先序、有覆蓋狀態，但不是要人照著跑的逐步腳本。長期回歸交 `api-test-author` 固化。

## 輸入 / 輸出
- **輸入**：API 設計文件（連結或內文）＋ `config/product-context.md` 的「API」段（base URL、認證方式）＋ `knowledge/`（RBAC/LBAC、旗標語意等商業規則）＋ 可選：既有自動化測試清單或 suite 名稱（用來標覆蓋狀態）。
- **輸出**：`output/api-coverage-matrix/<slug>.csv`（單一事實來源，git 可 diff），可選再產 `.xlsx`／`.html` 給非技術關係人審閱或簽核用；三者一律由同一份產生腳本輸出，**不手動改其中一份**，否則格式之間會失真。

## 步驟
1. **列端點清單**：從設計文件抽出每個 endpoint × method，連同對應的請求／回應 schema。
2. **每個端點分正負向**：Positive 是成功路徑與有意義的邊界值；Negative 是缺必填、型別錯誤、格式錯誤、衝突／重複、找不到、越權。每個端點至少一正一負，不必窮舉所有型別排列。
3. **加橫切構面**：套用下方「橫切構面」表，不是每個端點各自展開一輪，是挑代表性端點抽查。
4. **排優先序**：套用下方「優先序判準」表，逐列標 P0～P3。
5. **標覆蓋狀態**：對照既有自動化測試清單或 suite 名稱，能對上的標「已覆蓋」＋出處；對不上的標 `Gap`。**查不到就是 Gap，不得用合理推測算已覆蓋。**
6. **補代表性 payload／回應與 cURL**：每個乾淨、單一方法、單一端點的案例都補一組請求 payload、預期回應與可重現的 cURL；`multiple`／組合方法／跨端點彙整的列留質化描述即可，不必硬湊一支 cURL。**cURL 與 payload 一律用 `<TENANT>`／`<API_TOKEN>` 佔位符，不得寫入真實租戶或金鑰**；要在輸出的 HTML 版本做本機互動代填時，值只能存瀏覽器 `localStorage`、不得外送或寫回檔案。
7. **輸出並確認**：把矩陣摘要（案例數、正負向比例、Gap 數）列給使用者，確認後寫入 `output/api-coverage-matrix/<slug>.csv`（與可選的 `.xlsx`／`.html`）。

## 優先序判準（P0～P3）

本層只在「已經進入 in-scope」的前提下排序，不重新評估要不要測；要不要測是 `route-by-risk` 的事，兩套判準疊在一起會出現「兩個答案」，因此不共用同一張表。

| 優先序 | 判準 | 範例 |
|---|---|---|
| P0 | 核心 CRUD 的成功路徑、攸關資料完整性的邊界（如刪除層疊、跨資源一致性）、安全性閘門的極端案例（旗標全關、角色被全面擋下、最高權限的完整存取） | `GET /rules` 200、雙旗標全關全端點 403、RBAC 最低權限擋下全部寫入操作 |
| P1 | 常見的單一維度負向情境、單一旗標關閉、單一角色的正向存取流程、常見的 4xx 驗證錯誤 | 缺必填欄位 400、單一旗標關閉 403、View 權限可讀不可寫 |
| P2 | 較少見的欄位邊界、排序／分頁等非核心行為、跨資源生命週期的中間狀態 | 分頁邊界、排序條件、資源從 A 群組移到 B 群組 |
| P3 | 極端排列組合、已知限制或暫緩實作的文件化案例、效能與可用性以外的裝飾性檢查 | 已知回傳 501 的端點（另案追蹤中）、多重罕見組合 |

若整段 API surface 本身在 `route-by-risk` 判定為低風險，可整體下修一階，不必逐列重新判準。

## 橫切構面

| 構面 | 檢查什麼 | 範圍原則 |
|---|---|---|
| CRUD／核心流程 | 每個端點 × 方法的成功路徑與主要負向分支 | 每個端點至少一正一負 |
| 邊界／驗證 | 必填缺漏、型別錯誤、長度或範圍邊界、重複／衝突 | 挑對業務規則有意義的邊界，不窮舉所有型別 |
| RBAC/LBAC | 角色 × 資源存取矩陣、標籤／範圍隔離（跨範圍存取應被拒絕，含直接以 id 存取，不只列表過濾） | 基本抽查，不是重新驗證共用機制本身；每個角色至少代表性抽一條 |
| 旗標／授權閘門 | 各開關組合（全開、各自關一個、全關） | 抽代表性端點驗證組合，不必每個端點各測一輪 |
| Audit log | 代表性抽樣，每個會寫入 audit 的操作類型各一 | 機制本身若已有共用測試，這裡只驗有沒有正確掛上 |
| 跨資源 | 端對端跨資源生命週期（如建立、搬移、刪除層疊） | 挑會影響資料一致性的關聯，不必每組關聯都寫 |
| 新租戶預設值 | 全新環境、零配置下的預設行為（旗標預設值、設定預設值） | 只驗證「沒人動過設定」的初始狀態 |

## 鐵則
- **範圍不是本 skill 決定的。** 要不要枚舉某段 API 交給 `test-planning`／`route-by-risk`；本 skill 只負責「已經決定要枚舉」之後的展開與排序。
- **是需求清單，不是操作手冊。** 每一列可獨立驗證、有優先序、有覆蓋狀態；長期要守的回歸交 `api-test-author` 一支一支固化，這裡不寫測試程式碼。
- **查不到覆蓋就是 Gap。** 不得用「應該有測到」的推測填覆蓋欄位；灌水的覆蓋比沒有覆蓋更危險（同 `traceability` 的鐵則）。
- **憑證一律佔位符。** cURL／payload 不得寫入真實租戶或金鑰；本機互動代填只能存瀏覽器端，不外送、不落地。
- **產物是單一事實來源的多格式輸出。** 不手動改 csv／xlsx／html 其中一份，一律回頭改產生腳本重新輸出。

## 輸出（格式，非某次執行結果）
```
TC ID,Priority,Resource/Area,Endpoint,Method,Status Code,Type,Scenario,Steps,Expected,Repo Coverage
NPLAN-XXXX-TC-001,P0,Rules,/v2/x/rules,GET,200,Positive,"列出全部規則","呼叫 GET /rules，租戶至少有一筆規則","200，body 為規則陣列","feature_rules.robot CRUD-3"
NPLAN-XXXX-TC-002,P0,RBAC,/v2/x/rules/*,multiple,403,Negative,"最低權限擋下全部 Rules 操作","以 None 權限呼叫列表／建立／更新／刪除","全部回 403","Gap"
```

## 上下游
上游：人／`test-planning`（決定要枚舉的 API surface）、API 設計文件、`knowledge/`（RBAC/LBAC、旗標語意等商業規則）、`config/product-context.md`。下游：`api-test-author`（把 Gap 且高優先序的列固化成自動化測試）、`traceability`（把每一列當成一個 `req_id` 併入覆蓋對照表）、`release-signoff`（拿矩陣當簽核證據）。
