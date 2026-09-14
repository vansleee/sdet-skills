# Agent 副作用授權

`triage`、`bug-fixer` 與編排者在執行副作用前讀本文件及全域 `config/governance.yaml`。動作名稱定義在 `config/governance.example.yaml`；同一動作不因換成 CLI、MCP 或本地檔案就改名。

1. 先備好可檢視的內容與精確目標：project、repository／檔案、Issue／PR、變更範圍。讀取與草稿準備可以先做。
2. 確認設定可讀、分級為清單。同一動作出現在多級時採較嚴格的一級：`forbidden` 優先，其次 `needs_review`，再來 `autonomous`。
3. `forbidden` 不執行，也不把一般確認當成解除禁止。不得為完成本輪任務自行修改 governance。
4. `autonomous` 是專案已授予的自主權限，只在本次任務範圍內使用。`needs_review` 或未列出的動作，須有使用者涵蓋該目標與範圍的授權；已授權可沿用，不重複詢問。缺少授權才提出具體內容供確認。
5. 每個副作用都獨立檢查：開 Issue 不包含留言／改標籤，改碼不包含 push／開 PR，開 PR 不包含 merge。執行環境的 sandbox 與工具權限仍須滿足。
6. 在本輪交付報告記下動作、目標、分級與授權來源。授權被撤回、內容或目標超出範圍時重新確認。被擋就回報草稿與原因，不改走另一個後端規避。

`governance.yaml` 缺失或格式不明時，保留草稿並回報設定問題，不自行把範本當成已生效的授權。`merge_pr` 必須維持 forbidden；閘門放行只代表品質合格，不能替代執行權限。
