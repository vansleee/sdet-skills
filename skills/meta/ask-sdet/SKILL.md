---
name: ask-sdet
description: SDET 共同入口。辨識需求與目標專案，推薦流程；需要設定時接入 setup-sdet，設定完成後回到原任務。純諮詢不改設定。
disable-model-invocation: true
---

# Ask SDET

先辨識使用者想諮詢、設定專案，還是執行具體任務。設定訪談與寫檔契約只維護在 setup-sdet，本 skill 負責接入與返回原任務。設計理念見 `docs/meta/ask-sdet.md`。

> 只列「你要自己打」的 user-invoked 入口。其餘 model-invoked skill（evidence-package、explore、bug-hunter、triage、failure-analysis…）agent 遇到對的任務會自己觸發，不用你記；你想手動指定時照樣可以直接打名字。

下表用 Claude Code 的 `/名稱` 示意。Codex 以 `$名稱` 指定，ChatGPT 從 `@` 選取已安裝 skill；流程與授權契約相同。平台缺獨立 context 或操作工具時如實回報，不模擬完成。

## 先辨識需求與設定狀態

1. 純諮詢（例如「有哪些 skill」「該用哪支」）：直接回答或推薦入口，不要求先設定、不啟動訪談、不寫 config。
2. 明確要初次設定、換工具或改門檻：讀取 setup-sdet 的完整指令後，直接依它的流程訪談，不要求使用者再打一遍指令。
3. 要執行具體任務：先選下表的流程，再讀該 skill 的前置要求。依 `references/config-resolution.md` 確認目標 project；不明或交接衝突時先核對，不猜專案。只檢查任務需要的設定，不因無關欄位缺漏擋住任務。
4. 設定足夠：推薦或接入所選流程。使用者只問建議時，不擅自執行；已明確要求執行時沿用該授權，仍遵守所選 skill 與 governance 的界線。
5. 必要設定缺漏：列出缺漏與影響。使用者已要求設定時接入 setup-sdet；否則先確認是否要補設定，再進訪談。具名專案缺檔不得回退到平面預設專案，尚未支援多專案的流程先停手核對。

## 接入 setup-sdet 後返回

- 保留原任務與目標 project，讀取 setup-sdet 後按它的規則執行。先讀既有設定、只問缺漏或明確要求變更的項目，一次一個主題；不要在這裡複製一份訪談清單。
- 寫檔前列出具體路徑與內容供確認；祕密只記環境變數名稱。沿用 setup-sdet 的寫入與讀回驗收，不把呼叫 ask-sdet 當成改設定的概括授權。
- 讀回驗收成功後，回到原任務並沿用已確認的 project。原任務已獲執行授權就接續處理；僅諮詢就交付推薦入口。沒有原任務時提供下一步。
- 設定仍缺必填項、讀回失敗或平台缺工具時，列出阻礙，不宣稱完成、不啟動依賴該設定的工作。
- 保留 setup-sdet 作為直接設定入口。直接呼叫它會執行同一份設定流程，不會另建一套設定邏輯。

## 你想做什麼 → 用哪支
| 你的情境 | 打這個 |
|---|---|
| 新 repo 還沒設定 / 要換工具、改門檻 | 在此接入 setup-sdet；也可直接打 `/setup-sdet` |
| 要讓同事自主探索找 bug：先定目標與邊界 | `/exploration-charter` |
| 要牠排程獨立值班（獵→驗→閘→開單→開 PR 跑一輪） | `/duty-oncall` |
| 把一次成功探索固化成自動化測試（畫面）| `/test-author` |
| 要把一條後端規則、驗證或權限固化成 API 測試 | `/api-test-author` |
| 要判「這個 build 能不能 merge / 放行」 | `/quality-gate` |
| 要判「這一版能不能出」並留簽核紀錄 | `/release-signoff` |
| 寫技術文件、README 或 RFC，需要選擇文件結構與寫作規則 | `/technical-writing` |
| 不知道用哪個 | `/ask-sdet`（就是我） |
| 寫文件/PR 說明想去掉 AI 腔調（跟 SDET 流程無關的通用工具） | `/unslop` |

## 主要流程（誰接誰）
**找新 bug**：`/exploration-charter` 定目標 → bug-hunter 打獵（自動用 explore／evidence-package／test-oracle）→ bug-verifier 獨立重現 → issue-quality-gate 把關 → triage 開單 → bug-fixer 開 PR（人 merge）。整條要一次跑完，打 `/duty-oncall`。

verifier 的 confirmed 是「問題重現」，修復後的先紅後綠由 fixer 驗證。全鏈沿用 project、session、finding_id；盲驗只收原始證據與操作限制，UI／API 各驗必要證據。重複候選擋下並連結舊單；開單、留言、改碼、push、開 PR 各查治理權限。交接與授權規則見 `references/agent-handoff.md`、`references/agent-governance.md`。

**顧測試**：`/test-author`（畫面）或 `/api-test-author`（端點）寫測試 → 進 CI 跑 → 紅了 failure-analysis 分析 → test-heal 修測試 → re-run-gate 重跑到綠

**該用哪一層**：規則、計算、驗證、權限 → API；呈現、互動、可及性 → UI；不確定就先問 `route-by-risk`，判準見 `references/test-design.md` 第 0 節。留證同理：經畫面走 evidence-package，直接打端點走 api-evidence。

**顧產線**：route-by-risk 決定跑什麼 → ci-pipeline 建 pipeline（掛 test-env／test-parallelize）→ pipeline-read 讀 run → pipeline-triage 合併根因+派工 → flaky-manager 治理 flaky → `/quality-gate` 判放行 → pipeline-observability 算指標，把超標的路由回上游

**接團隊**：test-planning 圈範圍+排風險 →（`/exploration-charter` 探索／`/test-author` 固化）→ traceability 對覆蓋、把 gap 回饋下一輪 → status-report 回報 → `/release-signoff` 判這版能不能出

**三層閘門**（各管一層，上層吃下層產物）：issue-quality-gate（一張單能不能開）→ `/quality-gate`（一個 build 能不能放行）→ `/release-signoff`（一版 release 能不能簽）

**串起來**：`/duty-oncall` 在授權（`config/governance.yaml`）內把上面整條排程跑完。

**看校準**：sdet-economics 分開讀人工 precision 與 verifier 重現率；未裁定、驗不完與來源不明的舊資料不算成人工否定。現有 token-ledger 的 Claude 格式限制見 README，不能把其他平台缺用量的結果填成零成本。

## 維護規則
新增／改名／移除任一 user-invoked skill，或改了它在流程裡的位置，就要回來更新這張表。過時的路由器會騙人。


## 設定範圍

多專案接線範圍見 `references/config-resolution.md`。`maintain/` 仍讀扁平預設專案；`test-author`、`api-test-author` 與 `test-heal` 的產品設定與風格檔使用同一個 `config/` 根目錄。具名 project 的請求先停手核對，不路由成已支援的多專案操作。
