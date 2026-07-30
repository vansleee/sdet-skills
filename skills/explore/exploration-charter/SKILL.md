---
name: exploration-charter
description: 把一個探索目標談成一份 Exploration Charter（目標 / 範圍 / oracle / 邊界），作為 explore 自主探索的輸入。當要「開始一次自主探索」「定探索任務」「不寫逐步腳本地測某流程」時，先用它。
disable-model-invocation: true
---

# Exploration Charter

跟使用者把探索任務談清楚，產出 `charters/<slug>.yaml`，作為 `explore` 的輸入。**動手前先談，不要急著跑。** 設計理念見 `docs/explore/exploration-charter.md`。

## 訪談（一次問一個主題，不要一次丟整張表單）
1. **goal** — 一句話任務（要達成什麼）。
2. **scope** — 允許探索的區域/頁面。**只寫「去哪」，不要寫「怎麼走」。**
3. **oracles** — 怎麼算「對」（判斷依據），至少一條。例：UI 與 API 狀態碼一致、正常操作無 console error。
4. **out_of_bounds** — 絕對不准做的（護欄），至少涵蓋：不對 production 寫入、不付款、只用測試帳號。
5. **test_account / max_steps** — 用哪個測試帳號、最多幾步（停止條件；預設讀 `config/sdet-config.yaml`）。

## 甜蜜點自檢（寫入前，擋兩種壞味道）
- **太細**（scope 塞了逐步操作）→ 這是偽裝的 test case，退回：scope 只留「去哪」。
- **太空**（goal 只寫「測一測」、缺 oracle 或邊界）→ explore 會亂跑，退回補齊。
- 合格 = **目標明確、路徑開放、界線清楚**。

## 寫入前確認
把整理好的 charter 列給使用者看，確認後才寫 `charters/<slug>.yaml`。

## 產出格式
```yaml
charter:
  goal: "..."
  scope: [...]
  oracles: ["...", "..."]
  out_of_bounds: [...]
  test_account: "..."
  max_steps: 15
```

## 鐵則
- **一定要有 `oracles` 與 `out_of_bounds`**。缺了，explore 放手就不安全。
- `scope` 只說「去哪」，不寫「怎麼走」。留白給 explore。
- 一個探索任務一份，存進 `charters/`。
