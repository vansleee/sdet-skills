# CI Pipeline
把測試接進 GitHub Actions，並且**產出下游讀得懂的證據**。

## 設計理念
- **artifact 命名是 API，不是檔名。** `pipeline-read`、`failure-analysis`、`test-parallelize` 的 merge job 都靠固定名字找檔案。隨手改名，下游會在幾天後以「找不到 artifact」的形式安靜壞掉。所以命名表寫進 SKILL.md 正文，改名視同改介面。
- **trace 只留失敗。** trace 是最貴的 artifact（單檔可到數十 MB）。綠燈的 trace 沒有人會打開，卻會在 nightly 跑幾週後把 storage 吃爆，接著整個團隊開始「先關掉 trace 再說」。那才是真正的損失。留失敗的就夠了。
- **`if: always()` 是紀律不是細節。** 預設行為是「測試失敗 → 後續 step 跳過」，等於紅燈時反而不上傳報告。這是新手最常踩、也最傷的一個洞：最需要證據的那一次，證據沒了。
- **只留掛載點，不內建分片與環境。** 分片屬 `test-parallelize`、環境屬 `test-env`。若本 skill 自己長出一套 matrix 邏輯，那三支就會各有一套彼此不一致的規則。
- **風險閘在最前面。** 先問 `route-by-risk`「這輪值不值得跑這些」，再決定怎麼跑；把預算討論放在 pipeline 開頭，而不是事後看帳單。
- **改 workflow 先給 diff。** CI 設定壞掉的成本是「整個團隊被擋住」，屬於必須人看過的副作用。
