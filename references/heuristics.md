# 測試啟發式 Heuristics（reference，被 explore / test-oracle 讀）

Happy path = 一連串沒說出口的假設。Heuristic = 「常見隱形假設 → 怎麼把它反過來測」。`explore` 用它把 happy path 一條條翻過來；`test-oracle` 用它當判斷依據。

**紀律**：每次挑戰前，先點名「打的是哪個假設」（寫進 log 的 `assumption` 欄）。挑戰出的可疑現象一律標 `anomaly`、不當場定罪（判定交 `test-oracle`）。

| heuristic | 隱含假設 | 反過來怎麼測 | 購物車情境例子 |
|---|---|---|---|
| 逆操作 | 有新增就有還原 | 加了就移除、設了就清空、上一步/返回 | 加入後移除、數量歸零 |
| 非法狀態轉移 | 使用者照步驟順序走 | 跳過前置、直接打後面步驟的 URL、返回已完成步驟 | 未登入直接進 `/checkout` |
| 狀態組合 | 每種狀態畫面都正常 | 空/滿、登入/未登入、新/舊資料，看同一畫面 | 空車時看 navbar（cart icon 還在嗎） |
| 重複 / 併發 | 使用者只做一次 | double-click、兩個分頁、reload 中途送出 | 連點兩次 Add to cart |
| 權限越界 | 只有該看的人會看 | 未登入打需授權資源、用別人的 id | 未登入頁面對 `/users/me` 的行為 |
| 過期 / staleness | 資料永遠新鮮 | 放久了再操作、用過期的 id / session | 用很久前的 cart id 去結帳 |
| 中斷 / 取消 | 使用者會把流程走完 | 中途離開、reload、關頁再回來 | 填到一半 reload 結帳頁 |

用法：搭配 tour——tour 給路線（error / configuration…），heuristic 給「到了那裡戳哪個假設」。不必每次全跑，用風險挑最相關的幾個（呼應 `route-by-risk`）。
