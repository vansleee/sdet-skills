---
name: test-planning
description: 把一張 ticket / PRD 轉成「這次要測什麼」的範圍 + 風險清單，可續轉成 exploration charter。規劃一個 sprint / feature 要測什麼時使用。關鍵詞：測試規劃、test plan、範圍、風險、ticket、PRD、要測什麼。
---

# Test Planning

> 狀態：骨架（預留，TODO 待實作）

吃一張 ticket / PRD，讀 `knowledge/` 的產品知識，產出「這次的測試範圍 + 風險排序」，並可續轉成 `charters/<slug>.yaml` 交給 `explore`。

## TODO
- [ ] 定義輸入（ticket/PRD 連結或內文）/ 輸出（範圍 + 風險 + 建議 charter）
- [ ] 寫執行步驟：讀需求 → 對照 `knowledge/` → 圈範圍 → 標風險（接 `economics/route-by-risk`）
- [ ] 讀 `knowledge/` 與 `config/`，不把產品知識寫死
- [ ] 補 `agents/openai.yaml` 與 `docs/project/test-planning.md`
