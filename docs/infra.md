# infra/（顧好整條生產線）

`skills/infra/` 每支 skill 的設計理由。執行指令在各自的 `SKILL.md`，這裡只寫為什麼。

## ci-pipeline

把測試接進 GitHub Actions，並且**產出下游讀得懂的證據**。

### 設計理念
- **artifact 命名是 API，不是檔名。** `pipeline-read`、`failure-analysis`、`test-parallelize` 的 merge job 都靠固定名字找檔案。隨手改名，下游會在幾天後以「找不到 artifact」的形式安靜壞掉。所以命名表寫進 SKILL.md 正文，改名視同改介面。
- **trace 只留失敗。** trace 是最貴的 artifact（單檔可到數十 MB）。綠燈的 trace 沒有人會打開，卻會在 nightly 跑幾週後把 storage 吃爆，接著整個團隊開始「先關掉 trace 再說」。那才是真正的損失。留失敗的就夠了。
- **`if: always()` 是紀律不是細節。** 預設行為是「測試失敗 → 後續 step 跳過」，等於紅燈時反而不上傳報告。這是新手最常踩、也最傷的一個洞：最需要證據的那一次，證據沒了。
- **只留掛載點，不內建分片與環境。** 分片屬 `test-parallelize`、環境屬 `test-env`。若本 skill 自己長出一套 matrix 邏輯，那三支就會各有一套彼此不一致的規則。
- **風險閘在最前面。** 先問 `route-by-risk`「這輪值不值得跑這些」，再決定怎麼跑；把預算討論放在 pipeline 開頭，而不是事後看帳單。
- **改 workflow 先給 diff。** CI 設定壞掉的成本是「整個團隊被擋住」，屬於必須人看過的副作用。

### 為什麼 API 測試要獨立成 job

不是為了整齊，是為了**省掉裝瀏覽器那一步**。`npx playwright install --with-deps` 常常是整條 pipeline 最慢的一段，而 API 測試一個位元組都用不到它。把兩層混在同一個 job，等於讓後端規則的回饋時間被瀏覽器安裝綁架。

分開之後可以做一件更有價值的事：讓 API job 當 PR 的快 lane，UI job 掛在它後面。多數迴歸其實是後端規則壞掉，這種紅燈本來就該在幾十秒內亮，而不是等十分鐘的瀏覽器測試跑完。

代價是依賴關係會讓 API 一紅、UI 全部 skipped。這在 PR 上是想要的（先修再說），在 nightly 上是不想要的（要完整訊號），所以那條依賴只掛在 PR 觸發。

artifact 名稱也必須分開。混用同一個名字，`pipeline-read` 解析出來的失敗清單看不出是哪一層紅的，`pipeline-triage` 就沒辦法把「契約漂移」跟「定位器失效」分成兩群派給不同的人。

## test-parallelize

讓一大包測試在時限內跑完，前提是它們本來就跑得對。

### 設計理念
- **平行是放大鏡，不是加速鍵。** 序列執行會掩蓋很多依賴：共用帳號、共用資料、隱性順序依賴，在單執行緒下剛好都成立。一開平行，這些全部同時爆開，而且表現成「間歇性紅」，最貴的那種失敗。所以獨立性檢查是**前置閘門**而不是建議事項：沒過就擋下、先送去 `test-data` / `test-heal` / `test-env` 修，修好再回來。跳過這步，得到的不是快 4 倍的套件，是 flaky 產線。
- **驗數是為了防「靜默的綠」。** 分片最危險的失效模式不是紅燈，是某一片根本沒跑（matrix 設定錯、shard 表達式寫錯、runner 掛掉但 job 判 success），合併後看起來全綠、其實少跑 1/4 的測試。紅燈有人會查，假綠沒有。所以合併後 total 必須等於分片前 total，不等就擋下。
- **先 workers 後 shards。** workers 是同一台 runner 上的平行，成本為零；shards 是多開 runner，成本線性上升。把免費的用完再花錢，是最基本的順序。
- **快不等於免費，所以要把帳單攤開。** 分片省的是牆鐘時間，花的是 runner 分鐘數，而且每片都要付一次 checkout + install 的 overhead。輸出裡強制列出成本對比，是為了讓「再加兩片」變成一個有數字的決定，而不是反射動作。
- **合併報告是下游的生存條件。** 不合併的話，`pipeline-read`、`pipeline-triage`、`quality-gate` 全部只看得到片段。merge job 要 `if: always()`，紅燈時才最需要完整報告。
- **分桶平衡要有重算時機。** 依歷史 duration 分桶會隨測試增減而過時；不寫明何時重算，它就會在某次「加了 50 支測試」之後安靜地退化回不平衡。

## test-env

整套測試跑在哪、怎麼不互相踩、怎麼證明「環境活著」。

### 設計理念
- **禁止重置共享環境，沒有例外。** 這是全書少數幾條「連 override 都不給」的規則。共享 staging 上有別人的測試資料、有人正在手動驗一張 ticket、有 demo 排在明天早上。agent 一句「清乾淨比較好測」就 truncate，對它自己是合理的局部最佳解，對團隊是事故。所以做法反過來：**環境髒了就用唯一前綴繞開，不是清掉。**
- **只刪自己前綴的東西。** 全域刪除只是換個名字的重置，因此 teardown 的刪除條件必須綁 namespace 前綴。
- **seeding 走 API 而不是 DB。** 直插 DB 能繞過驗證，種出產品邏輯根本不承認的資料狀態（少了關聯、跳過狀態機）。這種資料製造出來的「bug」是假的，而查證它的成本比省下的 seeding 時間高一個數量級。
- **smoke check 是為了正確歸因，不是為了保險。** 沒有 smoke check 時，環境掛掉會表現成「幾百支測試同時紅」，然後有人花半天分析那幾百筆。先驗環境、fail fast、標 `environment`，是把幾小時的誤判壓成幾秒。
- **與 `test-data` 共用一套前綴慣例。** 兩支各發明一套，平行執行時就會出現「A 清掉了 B 的資料」這種最難查的失敗。
- **ephemeral 是理想，`shared-namespaced` 是現實。** 多數專案有起不動的依賴（SSO、第三方金流），所以策略表把代價寫清楚，讓人選了之後知道自己接受了什麼紀律。

## pipeline-read

把一個 CI run 讀成「下游吃得下的資料」，而且**只做這件事**。

### 設計理念
- **只讀不下結論。** 這支是感官不是大腦。它一旦開始判「這看起來像 flaky」，就會和 `failure-analysis`、`flaky-detect` 產生兩套彼此不一致的判斷邏輯，而且它手上的證據（log 片段）本來就比那兩支少。輸出事實、標好不確定的地方，讓下游判。
- **由粗到細是成本紀律。** `gh run view --log` 會把整包成功 log 拉進 context。幾萬行、幾乎全是雜訊、而且要價不菲。先看 jobs summary（通常就回答完「哪裡紅」），再 `--log-failed`，最後才下載 artifact。這條順序是本 skill 存在的主要理由之一。
- **error signature 正規化是為了下游能合併。** `pipeline-triage` 的核心動作是 fan-in 合併根因；能不能合併，取決於「同一個原因的兩筆失敗，字串長不長得一樣」。UUID、行號、timestamp 這些每次都不同的東西不抽掉，80 筆失敗就會變成 80 個獨立根因，合併失效、成本回到逐筆分析。
- **驗數防的是假綠。** `passed+failed+skipped != total` 代表有東西根本沒跑：collection error、shard 沒回報、報告被截斷。紅燈有人查，少跑沒人查，所以必須主動標成 warning。
- **輸出格式是契約。** `pipeline-triage`、`quality-gate`、`pipeline-observability` 都吃這份輸出。它跟 `ci-pipeline` 的 artifact 命名表是同一件事的兩端：一端寫、一端讀，改一邊要改兩邊。
- **建議下游、不強制下游。** 依失敗筆數建議轉 triage 或 failure-analysis，門檻讀 config，因為「幾筆算一批」是專案決定，不是本 skill 決定。

## pipeline-triage

一次 CI run 紅一片時，先合併根因、再分組派工開單。`failure-analysis` 的「一批」版。

### 設計理念
- **一筆 vs 一批。** 逐筆分析在 80 筆上是 80 倍成本，且看不出「其實只有 3 個根因」。先 fan-in 合併（signature + 共同前置 + 同時轉紅），再一群分析一次。
- **stack-wide 不分派個人。** 一個 infra 事件開 80 張分給 80 人是災難；合併成單一 infra issue。
- **讀 run 委給 `pipeline-read`。** 合併根因的成敗取決於 error signature 有沒有正規化（UUID、行號、timestamp 抽掉）；那件事屬於 `pipeline-read`。本 skill 若自己再刻一套讀法，兩邊的 signature 規則會漂移，合併就會安靜地失效。80 筆變成 80 個「獨立根因」。
- **後端可替換。** 讀 run 與開單都走 config（本 skill 是 `jenkins-failure-triage` / `pytest-failure-triage` 的 GitHub Actions 後裔）。
- **開單先確認、冪等。** 副作用先列清單確認；去重 + 重跑不重開。
- **只做 triage。** 分析交 `failure-analysis`、修測試交 `test-heal`、放行交 `quality-gate`、授權查 `governance`。

## flaky-manager

跨 run 的 flaky 名單、隔離政策，以及**退場機制**。

### 設計理念
- **quarantine 一定要有到期日。** 這是本 skill 最重要的一條。沒有退場機制的隔離，是把「刪掉測試」偽裝成「暫時關掉」：檔案還在 repo 裡、覆蓋率報表還算它、review 時看起來這塊有測，但它永遠不會再跑。半年後沒人記得為什麼關的，那塊功能實際上是裸奔的。所以 registry 每筆都有 `expires_at`，到期沒修就強制 escalate 到 `test-heal`（修）或 `test-prune`（明確地刪，並寫下失去什麼覆蓋）。要刪可以，但要**明著刪**。
- **`quarantined` 是欠債，不是結案。** 狀態機刻意讓 `quarantined` 走不到終點，只有 `resolved` 才是終點。這樣「隔離數」就自然變成會痛的指標，而不是可以無限增長的抽屜。
- **隔離不擋放行，但一定要列出來。** 讓隔離中的紅擋住 release，等於沒隔離；但不告訴放行的人「這版有 3 支測試是關掉的」，那是拿假的安全感換過關。所以 `quality-gate` 讀這份名單，並在報告裡明列。
- **禁止用 retry 當治理手段。** 加 retry 會讓 flake_rate 從報表上消失，但不穩定性還在，只是改成偶爾吃掉一次真實 bug。治理要處理的是 rate 本身。
- **一筆 vs 一批的分工。** `flaky-detect` 花錢重跑 N 次去定性**一支**；本 skill 只讀既有歷史、不重跑，管的是名單與政策。若本 skill 也去重跑，成本會隨名單長度線性爆炸。
- **隔離機制讀 config。** 用 `test.fixme`、tag + grep、還是 CI 層 exclude，是專案的測試框架決定；寫死在 skill 裡就綁死了一種專案。

## quality-gate

「這個 build 能不能放行」：逐條、附證據、留得住痕。

### 設計理念
- **三層閘門各管一層，不互相代做。** `issue-quality-gate`（一張單能不能開）→ 本 skill（一個 build 能不能放行）→ `release-signoff`（整個 release 對需求能不能簽）。上層吃下層的產物當證據。若每層都自己重新判一次「測試綠不綠」，就會出現三個彼此矛盾的答案，而人只會相信最寬鬆的那個。
- **`inconclusive` 不得當 PASS。** 拿不到 run、artifact 過期、`gh` 指令失敗。這些都很容易被當成「沒發現問題」而放行。但「查不到」和「沒問題」是兩件事。閘門的價值全在於它擋得住的那幾次，而那幾次往往正是證據殘缺的那幾次。
- **AND 而不是加權平均。** 加權平均會讓「四項優秀」洗掉「一項致命」。閘門要的是最低保證，不是總體印象分。
- **隔離中的紅不擋，但一定要列出來。** 讓被 quarantine 的測試擋住放行，等於隔離機制失效；但不告訴放行的人「這版有 3 支測試是關掉的」，就是拿假的安全感換過關。所以列出來是硬性欄位，不是選填。
- **只裁決，不執行。** `merge_pr` 在 governance 的 forbidden 名單。理由不是技術上做不到，而是：一個能自己判「可以放行」又能自己執行 merge 的 agent，錯誤成本沒有任何緩衝。留給人按下最後那顆按鈕。
- **override 必須留痕，而且不能事後補。** 現實中一定會有「今天非上不可」的時刻，堵死它只會逼人繞過整個閘門。所以給出口，但出口有代價：誰、何時、硬推了哪幾條、為什麼。這份紀錄之後會變成 `pipeline-observability` 的 override 次數指標。override 變多本身就是訊號。
- **`output/pipeline-gate.yaml` 不是 `output/sessions/<date>_<slug>/gate.yaml`。** 兩支 skill、兩個層級、兩個檔案。共用檔名會讓兩邊互相覆寫，而且覆寫的當下不會有人發現。

## pipeline-observability

把跨 run 的資料變成趨勢，再把趨勢變成**下一步該找誰**。

### 設計理念
- **每個指標都要綁行動，否則不要量。** 測試健康度儀表板的典型下場是：做得很漂亮、每週貼在頻道裡、沒有人因為它做過任何事。所以本 skill 的輸出格式強制每個 alert 附一個 `route`（哪支 skill）＋ 一句 `why`。指標的價值不在數字本身，在它縮短了「發現問題 → 知道該做什麼」的距離。
- **這是 infra 迴圈的回饋邊。** `ci-pipeline` 產 run → `pipeline-read` 讀 → `pipeline-triage` 分派 → `flaky-manager` / `quality-gate` 治理 → 本 skill 觀測，然後把結論送回 `flaky-manager` / `test-parallelize` / `test-prune`。沒有這條回饋邊，前面幾支就只是各自處理眼前那批紅，整條產線不會隨時間變好。
- **不重算，只引用。** flaky rate 的真相在 `output/flaky-registry.yaml`、放行的真相在 `output/pipeline-gate.yaml`。本 skill 若自己重算一遍，團隊就會有兩個數字，接著開始爭論哪個對。單一真相比精確更重要。
- **`no-data` 不是 0。** 這條和 `route-by-risk`「資料源缺不等於低風險」是同一條紀律的兩個化身。用 0 填補缺失資料，會讓「沒人量過」在報表上長得像「表現完美」。
- **趨勢優先於絕對值。** flaky rate 5% 在某些專案是常態；從 1% 漲到 5% 則在任何專案都是事件。閾值告訴你「現在痛不痛」，趨勢告訴你「要不要現在動手」。
- **中位數優於平均。** 一次拖了三天的紅燈會把 MTTR 平均值毀掉，讓指標失去可比性。
- **override 變多是閘門的問題，不是人的問題。** 直覺反應是「收緊管制」，但真實原因通常是準則與現實脫節（例如把不穩定套件列進必跑）。所以這個 alert 刻意路由給人去檢視 config，而不是路由去加強阻擋。
