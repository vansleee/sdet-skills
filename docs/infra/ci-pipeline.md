# CI Pipeline
把測試接進 GitHub Actions，並且**產出下游讀得懂的證據**。

## 設計理念
- **artifact 命名是 API，不是檔名。** `pipeline-read`、`failure-analysis`、`test-parallelize` 的 merge job 都靠固定名字找檔案。隨手改名，下游會在幾天後以「找不到 artifact」的形式安靜壞掉。所以命名表寫進 SKILL.md 正文，改名視同改介面。
- **trace 只留失敗。** trace 是最貴的 artifact（單檔可到數十 MB）。綠燈的 trace 沒有人會打開，卻會在 nightly 跑幾週後把 storage 吃爆，接著整個團隊開始「先關掉 trace 再說」。那才是真正的損失。留失敗的就夠了。
- **`if: always()` 是紀律不是細節。** 預設行為是「測試失敗 → 後續 step 跳過」，等於紅燈時反而不上傳報告。這是新手最常踩、也最傷的一個洞：最需要證據的那一次，證據沒了。
- **只留掛載點，不內建分片與環境。** 分片屬 `test-parallelize`、環境屬 `test-env`。若本 skill 自己長出一套 matrix 邏輯，那三支就會各有一套彼此不一致的規則。
- **風險閘在最前面。** 先問 `route-by-risk`「這輪值不值得跑這些」，再決定怎麼跑；把預算討論放在 pipeline 開頭，而不是事後看帳單。
- **改 workflow 先給 diff。** CI 設定壞掉的成本是「整個團隊被擋住」，屬於必須人看過的副作用。

## 為什麼 API 測試要獨立成 job

不是為了整齊，是為了**省掉裝瀏覽器那一步**。`npx playwright install --with-deps` 常常是整條 pipeline 最慢的一段，而 API 測試一個位元組都用不到它。把兩層混在同一個 job，等於讓後端規則的回饋時間被瀏覽器安裝綁架。

分開之後可以做一件更有價值的事：讓 API job 當 PR 的快 lane，UI job 掛在它後面。多數迴歸其實是後端規則壞掉，這種紅燈本來就該在幾十秒內亮，而不是等十分鐘的瀏覽器測試跑完。

代價是依賴關係會讓 API 一紅、UI 全部 skipped。這在 PR 上是想要的（先修再說），在 nightly 上是不想要的（要完整訊號），所以那條依賴只掛在 PR 觸發。

artifact 名稱也必須分開。混用同一個名字，`pipeline-read` 解析出來的失敗清單看不出是哪一層紅的，`pipeline-triage` 就沒辦法把「契約漂移」跟「定位器失效」分成兩群派給不同的人。
