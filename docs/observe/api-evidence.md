# API Evidence

`evidence-package` 的姊妹 skill。同一件事（留下能重現、能被別人獨立檢驗的證據），換一個介面層做。

## 為什麼不是把 API 模式塞進 evidence-package

`evidence-package` 從第一步就綁瀏覽器 session：開瀏覽器、開 trace、`snapshot` 取 ref、關鍵操作前後截圖、收工打包 trace。純 API 任務裡這些步驟**一個都不成立**，硬塞會讓那支 skill 每一段都要先問「這次有沒有畫面」，讀起來變成兩支 skill 擠在一份文件裡，兩邊的鐵則也會互相稀釋。

分開之後，兩支各自的鐵則都能寫死：`evidence-package` 可以繼續說「缺 trace 要開 bug 單就停手」，本 skill 可以說「回應 body 沒留就不算留證」。混在一起就只能寫成「視情況」。

## 為什麼證據單位是「請求與回應對」

畫面證據的問題是它只記錄結果的樣子，API 證據可以記錄**完整的因與果**：送了什麼、換回什麼、花多久。所以這裡不做「截圖等價物」，而是把每個請求存成一行結構化紀錄，加一份原始回應，讓下游能用 grep 找非 2xx、能用 schema 驗契約、能照序號重講一遍故事。

`requests.jsonl` 選 JSON Lines 而不是一個大 JSON，理由是它是**追加寫**的：探索途中隨時可能中斷，追加寫的檔案中斷了仍然可讀，一個要收尾才閉合的 JSON 陣列中斷了就整份壞掉。

## repro.sh 為什麼是必要產物而不是加分項

`bug-verifier` 的設計前提是**盲驗**：拿不到 hunter 的推理，只吃證據包從零重現。UI 情境下它至少還能照著截圖自己點一遍；API 情境下沒有 `repro.sh`，它得從 `requests.jsonl` 反推指令、猜 header、猜請求順序，那已經不是重現而是重寫。所以這份檔案是產出物的一部分，不是方便性工具。

## 憑證不落地為什麼要寫成鐵則

證據包會被貼進 issue、上傳成 CI artifact、留在磁碟很久。UI 證據裡的 token 藏在 trace 深處，API 證據裡的 token 就明擺在指令第二行。這是本 skill 相對高的風險，所以規範寫成「指令裡一律寫 `$VAR`」加「收工前把 `raw/*.headers` 的 `Authorization` 與 `Set-Cookie` 改成 `<redacted>`」兩道，而不是靠當下的記憶。

## 不省略前置請求

拿 token、建前置資料這些步驟很容易被當成雜訊而不被記。但 API bug 常常就藏在順序與狀態裡：同一個請求，帶新 token 過、帶舊 token 不過；先建再刪跟先刪再建結果不同。把前置請求刪掉的證據包，看起來乾淨，但重現不出來。
