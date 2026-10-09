# observe/

`skills/observe/` 每支 skill 的設計理由。執行指令在各自的 `SKILL.md`，這裡只寫為什麼。

## evidence-package

跑一段 Playwright 操作，把截圖 / trace / console / network 蒐集成一份可攜的證據包。

---

### 如何測試這支 skill

測 skill 分四層，由淺到深。前兩層有指令、可自動化；後兩層要實際叫起來跑。

#### 1. 驗證格式（檔案對不對）

確認每支 skill 的 `SKILL.md` 與 `agents/openai.yaml` 格式正確：

```bash
# 若已將 repo 當成 Claude Code 外掛
claude plugin validate . --strict
```

#### 2. 掛載，讓 Claude 讀得到

```bash
# 把 skills/ 底下每支 skill 連進 ~/.claude/skills
bash scripts/link-skills.sh
```

掛好後**開新對話**讓 Claude 重新載入，打 `/` 應該看得到 `evidence-package`。

#### 3. 裝 playwright-cli（evidence-package 需要）

本 skill 走 `playwright-cli`，不走 Playwright MCP：

```bash
brew install playwright-cli
playwright-cli --version      # 0.1.8 驗過，需要有 tracing-start / tracing-stop
playwright-cli install-browser
```

選 CLI 不選 MCP 的理由：權限用一條 `Bash(playwright-cli:*)` 就收斂得掉，不必整包放行 `mcp__playwright`；輸出路徑寫在指令參數裡，不會藏在 `~/.claude.json` 的 `--output-dir`；也省下每個 session 灌 30 幾個工具 schema 的 context。

`tracing-start` / `tracing-stop` 的原始 trace 落在**工作目錄下**的 `.playwright-cli/traces/`，snapshot 落在 `.playwright-cli/`。這個暫存跟 `evidence-package` 自己組的 `output/evidence/<YYYYMMDD>-<任務代號>/` 是兩回事：前者由 `scripts/pack-trace.sh` 打包成 `trace.zip` 搬進後者（見 `docs/state-files.md`）。暫存區位置可用 `PW_TRACE_DIR` 覆寫。

#### 4. 行為測試（真的跑一次、檢查產物）

在對話裡給它一個真實任務，例如：

> 幫我驗證 https://example.com 能不能正常開啟

跑完回終端機檢查它產出的證據包：

```bash
# 有沒有產生 output/evidence/<日期>-<任務>/ 資料夾
ls -R output/evidence/

# manifest 有沒有寫、Trace 狀態欄有沒有填
cat output/evidence/*/manifest.md

# 開啟 trace 逐步回放（截圖 / network / console 都在裡面）
npx playwright show-trace output/evidence/*/trace.zip
```

> 判準：打開這包 evidence，一個沒看過操作的人，能不能只靠裡面的證據重現你的結論。能，就算過。

---

### 開啟 trace.zip 的兩種方式

```bash
# 方式一：指令，開本機 Trace Viewer
npx playwright show-trace path/to/trace.zip
```

方式二：打開 [trace.playwright.dev](https://trace.playwright.dev)，把 `trace.zip` 拖進去即可（檔案在瀏覽器本機處理，不會上傳，內網 trace 也安心）。

---

### 設計理念（為什麼這樣設計）

- **Playwright 產生、skill 只組裝。** 截圖 / trace / HAR / console 都是 Playwright 原生能力，skill 不重做，只負責「組裝成一份可攜證據包 + manifest」。舊 Jenkins 時代要逆向解析 HTML 的苦工，換成 Playwright 後直接消失。
- **形狀固定，是為了交棒。** 每包長得一樣，下游的 `bug-verifier`、`triage` 才能不看說明直接讀。尤其 verifier 是獨立 agent，沒有你的對話記憶，只能靠這包自己站得住。
- **network 獨立存一份，不只靠 trace。** 「UI↔API 對照」需要一份能快速掃、標出非 2xx 的清單；叫人每次去 Trace Viewer 一格格翻太慢。
- **缺 trace 的降級規則。** 煙霧測試可用截圖+console+network 頂替；要開 bug 單則 trace 為必要條件，缺就停手回報。用機制擋掉「證據不足卻硬報」。
- **UI 是最會騙人的一層。** 樂觀更新會讓畫面顯示成功、後端其實失敗，所以「畫面說成功」一律要 API 狀態碼佐證。

## api-evidence

`evidence-package` 的姊妹 skill。同一件事（留下能重現、能被別人獨立檢驗的證據），換一個介面層做。

### 為什麼不是把 API 模式塞進 evidence-package

`evidence-package` 從第一步就綁瀏覽器 session：開瀏覽器、開 trace、`snapshot` 取 ref、關鍵操作前後截圖、收工打包 trace。純 API 任務裡這些步驟**一個都不成立**，硬塞會讓那支 skill 每一段都要先問「這次有沒有畫面」，讀起來變成兩支 skill 擠在一份文件裡，兩邊的鐵則也會互相稀釋。

分開之後，兩支各自的鐵則都能寫死：`evidence-package` 可以繼續說「缺 trace 要開 bug 單就停手」，本 skill 可以說「回應 body 沒留就不算留證」。混在一起就只能寫成「視情況」。

### 為什麼證據單位是「請求與回應對」

畫面證據的問題是它只記錄結果的樣子，API 證據可以記錄**完整的因與果**：送了什麼、換回什麼、花多久。所以這裡不做「截圖等價物」，而是把每個請求存成一行結構化紀錄，加一份原始回應，讓下游能用 grep 找非 2xx、能用 schema 驗契約、能照序號重講一遍故事。

`requests.jsonl` 選 JSON Lines 而不是一個大 JSON，理由是它是**追加寫**的：探索途中隨時可能中斷，追加寫的檔案中斷了仍然可讀，一個要收尾才閉合的 JSON 陣列中斷了就整份壞掉。

### repro.sh 為什麼是必要產物而不是加分項

`bug-verifier` 的設計前提是**盲驗**：拿不到 hunter 的推理，只吃證據包從零重現。UI 情境下它至少還能照著截圖自己點一遍；API 情境下沒有 `repro.sh`，它得從 `requests.jsonl` 反推指令、猜 header、猜請求順序，那已經不是重現而是重寫。所以這份檔案是產出物的一部分，不是方便性工具。

### 憑證不落地為什麼要寫成鐵則

證據包會被貼進 issue、上傳成 CI artifact、留在磁碟很久。UI 證據裡的 token 藏在 trace 深處，API 證據裡的 token 就明擺在指令第二行。這是本 skill 相對高的風險，所以規範寫成「指令裡一律寫 `$VAR`」加「收工前把 `raw/*.headers` 的 `Authorization` 與 `Set-Cookie` 改成 `<redacted>`」兩道，而不是靠當下的記憶。

### 不省略前置請求

拿 token、建前置資料這些步驟很容易被當成雜訊而不被記。但 API bug 常常就藏在順序與狀態裡：同一個請求，帶新 token 過、帶舊 token 不過；先建再刪跟先刪再建結果不同。把前置請求刪掉的證據包，看起來乾淨，但重現不出來。

## structured-result

把測試到的觀察或觀察結果，從 pass 和 fail 的二分法，擴充成六種狀態，而且每一筆都需要附上證據。

### 設計理念

- 因為測試案例失敗，有非常多的原因：有時候可能是環境有問題，有時候可能是這個測試案例的結果時好時壞，那也有時候是證據上可能不足。

  如果我們把真的 bug 和這些測試全部都放在 fail 裡面的話，等於我們沒辦法分清楚哪些是真的 bug，哪些是因為其他原因所導致的 fail。
- 我們必須要把非 pass 的狀態再細切分為 blocked、inconclusive、anomaly 或是 flaky，這樣我們才可以更精確地判斷這些失敗的測試案例。
- 如果今天非預期的情境被測試案例擋下來，這樣的情況我們會視為 PASS。我們會去對應說它符不符合預期，而不是單看 console 上面有沒有錯誤，就判斷它是 FAIL。
- 有的時候，我們必須要承認我們不知道，所以誠實地 blocked 或是 inconclusive，比假想或是推理出一個自己懷疑的答案會更有用。
- 通常 False Positive 是第一道閘門，只有 fail 或是經過我們分類確定的 anomaly，我們才可以繼續往下一步，例如：為這個問題開一張單子。

搭配 `evidence-package`；是 `classify-anomaly`、`test-oracle`、`bug-verifier` 的共同詞彙。

## classify-anomaly

看到異常，先分類是哪一種原因，再決定是否往下，而不是每看到紅字就當 bug。

### 設計理念
- **一個異常有很多種原因，只有一種是產品 bug。** 環境、測資、操作錯、flaky、已知問題。不分類就報，等於開一間誤報工廠。
- **依證據判類，不靠猜。** 每次判類都要指出依據哪條 evidence。
- **跨 finding 檢查。** 多筆共用同一錯誤簽章，通常是 environment 或 stack-wide 事件，歸一類。
- **只有 product-bug 能往下。** 其餘不直接變 Issue，控制 False Positive 的源頭（把關見 `issue-quality-gate`）。

上游：`structured-result`。下游：`test-oracle` → `bug-verifier` → `triage`。
