# Pipeline Triage
一次 CI run 紅一片時，先合併根因、再分組派工開單。`failure-analysis` 的「一批」版。

## 設計理念
- **一筆 vs 一批。** 逐筆分析在 80 筆上是 80 倍成本，且看不出「其實只有 3 個根因」。先 fan-in 合併（signature + 共同前置 + 同時轉紅），再一群分析一次。
- **stack-wide 不分派個人。** 一個 infra 事件開 80 張分給 80 人是災難；合併成單一 infra issue。
- **讀 run 委給 `pipeline-read`。** 合併根因的成敗取決於 error signature 有沒有正規化（UUID、行號、timestamp 抽掉）；那件事屬於 `pipeline-read`。本 skill 若自己再刻一套讀法，兩邊的 signature 規則會漂移，合併就會安靜地失效——80 筆變成 80 個「獨立根因」。
- **後端可替換。** 讀 run 與開單都走 config（本 skill 是 `jenkins-failure-triage` / `pytest-failure-triage` 的 GitHub Actions 後裔）。
- **開單先確認、冪等。** 副作用先列清單確認；去重 + 重跑不重開。
- **只做 triage。** 分析交 `failure-analysis`、修測試交 `test-heal`、放行交 `quality-gate`、授權查 `governance`。
