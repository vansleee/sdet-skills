---
name: exploration-charter
description: 把一個探索目標談成一份 Exploration Charter（目標 / 範圍 / oracle / 邊界），作為 explore 自主探索的輸入。當要「開始一次自主探索」「定探索任務」「不寫逐步腳本地測某流程」時，先用它。
disable-model-invocation: true
---

# Exploration Charter

跟使用者把探索任務談清楚，產出 `charters/<slug>.yaml`，作為 `explore` 的輸入。**動手前先談，不要急著跑。** 設計理念見 `docs/explore/exploration-charter.md`。

## 訪談（一次問一個主題，不要一次丟整張表單）
0. **project**（只在 `config/` 底下有專案子目錄時才問）— 這次探索打哪個常態受測產品的 slug，寫進 `charter.project`，`explore` 據此決定讀哪組 `config/<project>/`（規則見 `references/config-resolution.md`）。一次性探索（練習站、demo 站）不填，改由 `target` 自己帶網址。
1. **goal** — 一句話任務（要達成什麼）。
2. **scope** — 允許探索的區域/頁面。**只寫「去哪」，不要寫「怎麼走」。**
2b. **endpoints**（要探索 API 才問）— 允許直接打的端點或端點群（`GET /products`、`/users/*`），可寫「契約來源列出的全部」。跟 `scope` 分開寫：畫面與端點是兩個介面層，混在一起 `explore` 分不出該用 `snapshot` 還是該打請求。有 `endpoints` 就一定要有 `auth_context`（用哪個帳號的憑證、要不要另備一個「別人」的帳號驗授權邊界）。
3. **oracles** — 怎麼算「對」（判斷依據），至少一條。例：UI 與 API 狀態碼一致、正常操作無 console error。有 `endpoints` 時至少再補一條 API 專屬的（狀態碼語意、契約 schema、授權邊界；清單見 `test-oracle`）。
4. **out_of_bounds** — 絕對不准做的（護欄），至少涵蓋：不對 production 寫入、不付款、只用測試帳號。有 `endpoints` 時另外涵蓋：不打 `config/product-context.md` 標記「不得碰」的端點、不做資料列舉或 dump、不自動化連打（會撞速率限制，把 `429` 變成雜訊）。
5. **test_account / max_steps** — 用哪個測試帳號、最多幾步（停止條件；預設讀解析後的 `sdet-config.yaml`）。

## 甜蜜點自檢（寫入前，擋兩種壞味道）
- **太細**（scope 塞了逐步操作）→ 這是偽裝的 test case，退回：scope 只留「去哪」。
- **太空**（goal 只寫「測一測」、缺 oracle 或邊界）→ explore 會亂跑，退回補齊。
- 合格 = **目標明確、路徑開放、界線清楚**。

## 寫入前確認
把整理好的 charter 列給使用者看，確認後才寫 `charters/<slug>.yaml`。

## 產出格式
```yaml
charter:
  project: "<slug>"                 # 對應 config/<slug>/ 與 knowledge/<slug>/；一次性探索省略
  goal: "..."
  target: "https://..."             # 沒有 project 時必填；有 project 時可省，base URL 由 config 取
  scope: [...]                      # 畫面側：頁面 / 區域
  endpoints: ["GET /products", "/users/*"]   # API 側；沒有要探索 API 就整個省略
  auth_context:                     # 有 endpoints 時必填
    as: "env:API_TOKEN_USER1"
    other: "env:API_TOKEN_USER2"    # 驗授權邊界用的「別人」；沒有就寫 none 並說明
  oracles: ["...", "..."]
  out_of_bounds: [...]
  test_account: "..."
  max_steps: 15
```

## 鐵則
- **一定要有 `oracles` 與 `out_of_bounds`**。缺了，explore 放手就不安全。
- **`project` 要嘛填得對、要嘛不填。** 填了就必須有對應的 `config/<slug>/`；`explore` 解析不到會停手，不會回退去讀別的專案設定。不確定 slug 就先不填，用 `target` 帶網址。
- `scope` 只說「去哪」，不寫「怎麼走」。留白給 explore。
- **`scope` 與 `endpoints` 分開寫。** 把「API 授權」塞進 `scope` 當一個項目，`explore` 只會用畫面去戳它，端點層其實沒被走過。
- **`auth_context` 只寫變數名，不寫 token 值。**
- 一個探索任務一份，存進 `charters/`。
