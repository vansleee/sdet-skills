# Pipeline Read
把一個 CI run 讀成「下游吃得下的資料」，而且**只做這件事**。

## 設計理念
- **只讀不下結論。** 這支是感官不是大腦。它一旦開始判「這看起來像 flaky」，就會和 `failure-analysis`、`flaky-detect` 產生兩套彼此不一致的判斷邏輯，而且它手上的證據（log 片段）本來就比那兩支少。輸出事實、標好不確定的地方，讓下游判。
- **由粗到細是成本紀律。** `gh run view --log` 會把整包成功 log 拉進 context——幾萬行、幾乎全是雜訊、而且要價不菲。先看 jobs summary（通常就回答完「哪裡紅」），再 `--log-failed`，最後才下載 artifact。這條順序是本 skill 存在的主要理由之一。
- **error signature 正規化是為了下游能合併。** `pipeline-triage` 的核心動作是 fan-in 合併根因；能不能合併，取決於「同一個原因的兩筆失敗，字串長不長得一樣」。UUID、行號、timestamp 這些每次都不同的東西不抽掉，80 筆失敗就會變成 80 個獨立根因，合併失效、成本回到逐筆分析。
- **驗數防的是假綠。** `passed+failed+skipped != total` 代表有東西根本沒跑：collection error、shard 沒回報、報告被截斷。紅燈有人查，少跑沒人查——所以必須主動標成 warning。
- **輸出格式是契約。** `pipeline-triage`、`quality-gate`、`pipeline-observability` 都吃這份輸出。它跟 `ci-pipeline` 的 artifact 命名表是同一件事的兩端：一端寫、一端讀，改一邊要改兩邊。
- **建議下游、不強制下游。** 依失敗筆數建議轉 triage 或 failure-analysis，門檻讀 config——因為「幾筆算一批」是專案決定，不是本 skill 決定。
