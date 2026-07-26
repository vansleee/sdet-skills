# Exploration Charter

把探索目標談成一份憲章（目標/範圍/oracle/邊界），給 explore 用。

## 設計理念
- **從指揮轉成 Mentor 的第一步。** 不再寫「怎麼做」的逐步腳本，改寫「要達成什麼、界線在哪」，路徑留給 agent。
- **user-invoked：動手前先談。** 探索的品質八成取決於憲章好壞，所以由人先把任務談清楚，不讓 agent 自己亂定目標。
- **oracle + out_of_bounds 是讓「放手」安全的關鍵。** oracle 給判斷力、邊界給護欄；兩者缺一，自主探索就會失控或亂喊。
- **甜蜜點：目標明確、路徑開放、界線清楚。** 太細退化成 test case、太空會亂跑。
- **一份憲章一個任務。** 存 `charters/`，可重跑、可人審。

上游：人。下游：`explore`（吃 charter 自主跑）→ `structured-result` / `classify-anomaly`。
