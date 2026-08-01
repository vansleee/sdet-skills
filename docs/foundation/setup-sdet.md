# Setup SDET

一次性設定：訪談受測產品、登入、CI、issue tracker、Playwright、門檻，產出所有其他 skill 讀取的 `config/`。

## 設計理念（為什麼這樣設計）

- **後端可替換。** skill 內文只寫「file to the issue tracker」「讀 CI run」，實際指令放 `config/`。這是從 Jenkins/JIRA 遷到 GitHub Actions/Issues 不必重寫邏輯的關鍵。
- **祕密不落地。** 帳密/token 只記變數名（`env:VAR`），不記值、不在對話裡索取。把安全變成機制，不靠自律。
- **user-invoked。** 設定是有後果的動作，只有人打 `/setup-sdet` 才會啟動（`disable-model-invocation: true`），AI 不會自作主張改設定。
- **一次一個主題、可重複執行。** 不一次丟六段表單；重跑時先讀現有 config、只問缺的。
- **開工前先驗 trace 能力。** 讓「跑完才發現沒 trace」提前到設定階段就攔下（缺 `playwright-cli` → 提示裝）。

