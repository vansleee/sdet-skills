# Exploration Charter

把探索目標談成一份憲章（目標/範圍/oracle/邊界），給 explore 用。

## 設計理念

- **從指揮轉成 Mentor 的第一步。** 不再寫「怎麼做」的逐步腳本，改寫「要達成什麼、界線在哪」，路徑留給 agent。
- **user-invoked：動手前先談。** 探索的品質八成取決於憲章的好壞，所以由人先把任務談清楚，不讓 agent 自己亂定目標。
- **oracle + out_of_bounds 是讓「放手」安全的關鍵。** oracle 給判斷力、邊界給護欄；兩者缺一，自主探索就會失控或亂喊。
- **甜蜜點：目標明確、路徑開放、界線清楚。** 太細退化成 test case、太空會亂跑。
- **一份憲章一個任務。** 存 `charters/`，可重跑、可人審。
- **`endpoints` 跟 `scope` 分兩個欄位。** 早期的 charter 把「API 授權」當成 `scope` 裡的一個項目，看起來涵蓋到了，實際上 `explore` 讀到的仍然是一個要用畫面去逛的區域名稱，端點層從來沒被直接打過。介面層不同、觀察手段不同、留證的 skill 也不同，欄位就該分開，讓「有沒有真的探索 API」變成看得出來的事。
- **`project` 是選填，但填了就是硬約束。** 多專案時，charter 要說清楚打哪個產品，`explore` 才知道讀哪組 `config/<project>/`。設計成選填是為了讓一次性探索（練習站、demo 站）照舊只帶 `target` 就能跑；設計成硬約束是因為解析不到時回退讀扁平設定，會拿 A 產品的 base URL 與帳號去打 B 產品，而且證據看起來完全正常。所以寧可停手。解析規則見 `references/config-resolution.md`。
- **`auth_context` 要求一個「別人」。** 授權邊界是 API 最常見也最貴的一類 bug，而它需要第二組憑證才驗得動。談憲章的時候問，比探索到一半才發現沒帳號好。填 `none` 也可以，但那等於明說這一輪不驗越權。

上游：人。下游：`explore`（吃 charter 自主跑）→ `structured-result` / `classify-anomaly`。
