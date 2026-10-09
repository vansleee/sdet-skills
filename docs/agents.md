# agents/

`skills/agents/` 每支 skill 的設計理由。執行指令在各自的 `SKILL.md`，這裡只寫為什麼。

## bug-hunter

依一份 charter 自主獵一輪，交回「已判定、已去重、已濾誤報、標好信心」的候選 issue 清單。

### 設計理念

- **它不發明能力，它的價值是編排。** 探索、標狀態、分類、判定、打分、去重、濾誤報，這七件事前面都各自有 skill；Hunter 做的是把它們接成一條線，並**保證順序**（先判定再打分、先去重再濾誤報），讓使用者一句話就能拿到乾淨結果。
- **「找的人」不能當「判的人」。** Hunter 對自己找到的東西有確認偏誤，所以它的權力被刻意切窄：只輸出「候選」。獨立蓋章交 `bug-verifier`（沒有 Hunter 記憶的 subagent），能不能開單交 `issue-quality-gate`。這是 `agents/` 最重要的治理設計。
- **model-invoked。** `duty-oncall` 得在值班中直接調用它，user-invoked 會讓整條編排叫不到它。「會消耗預算、會操作產品」不靠 invocation mode 擋，靠 charter 的 `out_of_bounds`、`config/sdet-config.yaml` 的 `budget`，以及「不開單、不碰 tracker」的鐵則。真正不可逆的那一下留在 `triage` / `bug-fixer` 的確認步驟與 `governance.yaml`。
- **四道守門缺一不可。** oracle 擋「把怪當成錯」、confidence 擋「沒把握的自動往下」、dedup 擋「同一個報十次」、known-FP 擋「判過的再報一次」。前三週教的規矩，在這裡第一次被強制執行而不只是好習慣。
- **證據必須可攜。** UI 與 API 各依留證 skill 封裝完整包，再另建只含步驟、原始證據與限制的盲驗包。完整包有結論，不能直接交給 verifier；兩者共用同一組 project、session、finding_id。

### 上下游

上游：`exploration-charter`（給目標與邊界）。
內部依序：`explore` → `structured-result` → `classify-anomaly` → `test-oracle` → confidence（`references/confidence.md`）→ dedup（`references/bug-fingerprint.md`）→ known-FP → UI／API 封裝與盲驗輸入。
下游：`bug-verifier` → `issue-quality-gate` → `triage` / `bug-fixer`。
編排它的：`duty-oncall`（排班值勤時的第一站）。

### 狀態檔

讀：`output/known-false-positives.yaml`、`output/issues-index.yaml`、`config/sdet-config.yaml`。
寫：`output/calibration.yaml`（以 project + session + finding_id 記 predicted）、evidence 目錄、候選清單；已知指紋只在同 project 的本地 index 合併觀察。
**不寫** issue tracker。

## bug-verifier

以不繼承對話的獨立 subagent／session 重現候選，輸出 confirmed / not-reproduced / inconclusive。Claude Code、Codex 與 ChatGPT 共用 `references/agent-handoff.md` 的契約，依實際平台建立乾淨 context。

### 設計理念
- **找的人不能當判的人。** 作者對自己的發現有確認偏誤；複核照搬人類團隊的 code review：找第二雙眼睛從零重現。
- **不共享記憶是刻意設計。** 它只收盲驗包，允許另讀必要執行設定。完整 Evidence Package 的 notes 與 manifest 含結論，留給 gate 與人，不交 verifier。
- **兌現 Day 11 的可攜性。** 證據站不站得住，在沒有本次記憶的 verifier 面前現形；不可攜就退回，不硬驗。
- **not-reproduced 是價值，不是失敗。** 每一筆攔下的 not-reproduced，都是一次沒發生的誤報、一分沒被消耗的信任。
- **verdict 要能複核。** UI 留本輪 trace、前後截圖與步驟；API 留本輪請求／回應、body 與可重現請求。產物寫獨立 evidence 目錄。API 沒有畫面，不能用截圖缺失否定其證據。
- **確認的是問題重現。** confirmed 表示同一現象再次出現，不表示修復成功。這一站在 gate 與修復之前；修復後的先紅後綠由 bug-fixer 負責。

### 上下游
上游：hunter 或呼叫端提供盲驗輸入。下游：issue-quality-gate。verifier 不讀 calibration；呼叫端或 gate 依完整識別回填 verifier 欄位，人工裁定另存 human 欄位。

### 成長路徑
v0.1：單一候選、單輪重現。之後：多輪 / 跨環境重現、自動重試策略。

## issue-quality-gate

開單前的硬閘門：六條 AND 條件全過才放行，輸出 `output/sessions/<date>_<slug>/gate.yaml` 分流 pass / hold / block。

### 設計理念
- **把好習慣變成硬條件。** 證據（Day 11）、oracle（Day 20）、confidence（Day 22）、非 FP（Day 23）、去重（Day 24）、獨立重現（Day 26）單獨看都是好習慣，但好習慣會被跳過；閘門讓「最好有」變成「沒有就開不了」。
- **AND，不是加權平均。** 五條滿分救不了一條 fail；第一條（可獨立重現）最硬，接的是 Day 14 那句「無法重現就不開單」。
- **被擋下的比放行的更有價值。** 每筆 hold / block 都寫 `blocked_on`，把「agent 判不了、要人來」變成看得到的佇列。
- **透明才能校準。** gate_result、verifier_verdict 與 human_verdict 分開回填同筆預測；被擋不等於誤報，尚未人判的保留 null。
- **重複項不再開單。** 即使已併入舊單，not_duplicate 仍失敗，結果為 block 並指向 existing_issue；更新舊單另走 triage 授權。
- **證據依介面驗收。** UI 與 API 使用同一個 gate，各按交接契約驗證完整性；混合候選兩側都要過。

### 上下游
上游：`bug-verifier`（verdict）＋ hunter 的 confidence / 指紋 / FP 結果。下游：pass → `triage`（開單）／`bug-fixer`（可修的）；hold / block → 人工佇列。編排它的：`duty-oncall`。

### 成長路徑
v0.1：六條固定檢查。之後：條件可配置化、override 稽核報表。

## triage

把通過分類的 product-bug 寫成可重現報告、開成 GitHub Issue。

### 設計理念
- **只吃 product-bug。** 非 product-bug（環境／測資／flaky…）在 `classify-anomaly` 就被擋掉，triage 不重判。
- **報告寫行為、不寫實作。** agent 從外部操作產品，被迫用使用者語言描述，報告天生耐久、跨得過重構。
- **重現步驟必填。** 湊不齊就不開單（更嚴的把關見 `issue-quality-gate`）。
- **後端隨 project。** 指令與 labels 讀解析後的專案設定，GitHub 明確指定 repository。本地 Issue 也保留 project 與 finding 識別；登入失敗不能偷偷換後端。
- **每個動作各有授權。** create_issue、comment_issue、update_issue 各自檢查全域 governance；沿用涵蓋範圍的既有授權，forbidden 優先。
- **送出前再去重。** gate pass 之後可能已有新單；最後再讀 index，命中就停止新單流程。舊單補證需要留言授權，不因禁止開新單就一併禁止準備補充資料。

### 成長路徑
v0.1：一張報告、手動開一張。之後：去重、委派 `bug-verifier`/`bug-fixer`、批次見 `pipeline-triage`。
前身：`jenkins-failure-triage` / `pytest-failure-triage`（JIRA 版）。

## bug-fixer

只需要修復可以被重現的問題：照著先試著重現 → 寫會紅的回歸測試 → 最小修改轉綠 → 開 PR，絕不自行 merge。

### 設計理念
- **無法重現，就不能修。** 與 triage 的「無法重現不開單」同一條線；拿到 issue 第一件事是自己重現，跑不出來就退回。
- **先紅後綠。** 改碼前先寫一個現在就會紅的測試證明「bug 存在且被抓到」；修完轉綠才算修好。沒紅過證明不了存在，沒轉綠證明不了修好。
- **防綠色作弊。** 最陰險的失敗是為了讓測試通過而弱化斷言、加 sleep、mock 掉真實呼叫。測試綠了、bug 還在。守則明列不准。
- **有自知之明。** 範圍清楚的才動手（如 qty=-5 缺前端驗證）；根因牽涉廣、影響面不明的（如元件狀態糾纏的 TypeError）只報不修，交回人判。
- **開 PR 是上限。** merge 由 `governance.yaml` 的 forbidden 釘死，不是靠自律，是根本沒有權力（Day 29）。
- **授權分動作。** 改測試、改產品、留言、更新標籤、推送、開 PR 各查對應權限；開 PR 的同意不能追認先前未授權的修改。資料與產品 repo 沿用交接 project，PR 目標不從 Issue tracker repo 猜。
- **修復驗證在本 skill。** 先確認原問題存在，再驗修復後轉綠。bug-verifier 在上游確認缺陷可重現，其 confirmed 不代表修復驗收通過。

### 上下游
上游：`issue-quality-gate` pass 且範圍清楚的 issue。下游：人 review / merge。編排它的：`duty-oncall`。

### 成長路徑
v0.1：單一 issue、單一 PR。之後：修復模式庫、與 test-heal 的分工釐清。

## duty-oncall

排程下把整條 pipeline 跑完一輪的「獨立值班」總編排：hunter → verifier → gate → triage / fixer，最後寫 run log。

### 設計理念
- **它不發明能力，它排班。** 每一站都是既有 skill；oncall 的價值是讓它們自己接力跑完，而不是人逐站點名。
- **敢放手，是因為門都建好了。** 值班 = 自動化的觸發 + 前面所有治理，一個都不少；編排不越權，各站鐵則原封生效。
- **發起交給排程，拍板留給人。** merge 是人按、PO 問題是人去問、hold 是人來判；它值的是「探索、驗證、把關、備好」，人值的是「不可逆的那幾下」。
- **run log 是寫給未來的自己。** ROI 與校準的原始資料只能當下埋、不能事後補；今天不記 tokens 和 gate_passed，之後就算不出一個 bug 花多少錢。
- **摘要要五分鐘能複核完**，不是要人重跑一遍。

### 上下游
輸入：charter ＋ 排程／使用者觸發。內部依序：`bug-hunter` → `bug-verifier` → `issue-quality-gate` → `triage` / `bug-fixer`。輸出：`output/sessions/<date>_<slug>/runs/<date>.yaml`、值班摘要、人工佇列。

先獨立確認問題，再判能否開單，接著開 Issue 與修復。bug-verifier 的 confirmed 表示問題重現，不能移到 fixer 後當成修好了；修復的先紅後綠驗證由 fixer 執行。

各站沿用 project、session、finding_id。編排者只把盲驗包交給不繼承對話的獨立 context，收到 verdict 才回填 calibration。無法隔離就保留待驗；重複項記 block 並連結舊單。留言、改碼與開單各自受 governance 管制。

### 成長路徑
v0.1：單 charter 單班。之後：多 charter 排班、與 route-by-risk 決定值什麼、餵 sdet-economics 算帳。
