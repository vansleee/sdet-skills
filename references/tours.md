# 探索 Tours（reference，被 exploration-charter / explore 讀）

Tour = 探索的「鏡頭」：給 agent 一個角度，不是一串步驟。憲章可引用 `tours: [data, error]`，explore 照鏡頭系統性地挖。

| tour | 意圖 | 在購物車情境的例子 |
|---|---|---|
| feature | 走主要功能，確認主線可用 | 登入 → 加入購物車 → checkout |
| data | 專攻輸入邊界 | 數量欄:0 / 負數 / 超大 / 小數 / 非數字 / 空值 |
| error | 故意走錯誤路徑 | 錯密碼、無權限存取、不存在的商品、中途取消 |
| configuration | 換狀態看同一畫面 | 登入/未登入、空車/滿車、不同語系 |
| money（主流程） | 死盯最貴的路徑 | 結帳、付款前的每一步金額 |
| back-alley | 專挑最少人走的角落 | 少用的篩選、深層設定、邊緣連結 |

用法建議：不要每次全跑；用風險選 2–3 個最相關的（呼應 route-by-risk）。
