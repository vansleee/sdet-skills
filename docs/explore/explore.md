# Explore

依 charter 自主探索：自己決定下一步、記路徑、留證，產出候選 findings。

## 設計理念
- **自主的心臟，也是最容易翻車的地方。** LLM agent 放手後三大失敗模式：亂點、鬼打牆、幻覺。本 skill 的價值不在「會點」，而在用三條硬規則把這三件事擋掉。
- **下一步必須引用當前畫面證據** → 防亂點（不能憑空決定）。
- **路徑記憶，做過不重做** → 防鬼打牆。
- **沒證據不喊 bug** → 防幻覺；判定外包給 `test-oracle` / `classify-anomaly`，探索只負責「看與試」。
- **一定要有停止條件。** 達標 / max_steps / 偵測打轉就停，不無限探索。
- **charter 決定邊界。** out-of-bounds 硬守，遇到就停手回報。

上游：`exploration-charter`（給目標與邊界）。下游：`structured-result`、`classify-anomaly`、`bug-verifier`。
