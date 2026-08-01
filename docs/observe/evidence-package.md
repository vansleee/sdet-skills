# Evidence Package

跑一段 Playwright 操作，把截圖 / trace / console / network 蒐集成一份可攜的證據包。

---

## 如何測試這支 skill

測 skill 分四層，由淺到深。前兩層有指令、可自動化；後兩層要實際叫起來跑。

### 1. 驗證格式（檔案對不對）

確認每支 skill 的 `SKILL.md` 與 `agents/openai.yaml` 格式正確：

```bash
# 若已將 repo 當成 Claude Code 外掛
claude plugin validate . --strict
```

### 2. 掛載，讓 Claude 讀得到

```bash
# 把 skills/ 底下每支 skill 連進 ~/.claude/skills
bash scripts/link-skills.sh
```

掛好後**開新對話**讓 Claude 重新載入，打 `/` 應該看得到 `evidence-package`。

### 3. 裝 playwright-cli（evidence-package 需要）

本 skill 走 `playwright-cli`，不走 Playwright MCP：

```bash
brew install playwright-cli
playwright-cli --version      # 0.1.8 驗過，需要有 tracing-start / tracing-stop
playwright-cli install-browser
```

選 CLI 不選 MCP 的理由：權限用一條 `Bash(playwright-cli:*)` 就收斂得掉，不必整包放行 `mcp__playwright`；輸出路徑寫在指令參數裡，不會藏在 `~/.claude.json` 的 `--output-dir`；也省下每個 session 灌 30 幾個工具 schema 的 context。

`tracing-start` / `tracing-stop` 的原始 trace 落在**工作目錄下**的 `.playwright-cli/traces/`，snapshot 落在 `.playwright-cli/`。這個暫存跟 `evidence-package` 自己組的 `output/evidence/<YYYYMMDD>-<任務代號>/` 是兩回事：前者由 `scripts/pack-trace.sh` 打包成 `trace.zip` 搬進後者（見 `docs/state-files.md`）。暫存區位置可用 `PW_TRACE_DIR` 覆寫。

### 4. 行為測試（真的跑一次、檢查產物）

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

## 開啟 trace.zip 的兩種方式

```bash
# 方式一：指令，開本機 Trace Viewer
npx playwright show-trace path/to/trace.zip
```

方式二：打開 [trace.playwright.dev](https://trace.playwright.dev)，把 `trace.zip` 拖進去即可（檔案在瀏覽器本機處理，不會上傳，內網 trace 也安心）。

---

## 設計理念（為什麼這樣設計）

- **Playwright 產生、skill 只組裝。** 截圖 / trace / HAR / console 都是 Playwright 原生能力，skill 不重做，只負責「組裝成一份可攜證據包 + manifest」。舊 Jenkins 時代要逆向解析 HTML 的苦工，換成 Playwright 後直接消失。
- **形狀固定，是為了交棒。** 每包長得一樣，下游的 `bug-verifier`、`triage` 才能不看說明直接讀。尤其 verifier 是獨立 agent，沒有你的對話記憶，只能靠這包自己站得住。
- **network 獨立存一份，不只靠 trace。** 「UI↔API 對照」需要一份能快速掃、標出非 2xx 的清單；叫人每次去 Trace Viewer 一格格翻太慢。
- **缺 trace 的降級規則。** 煙霧測試可用截圖+console+network 頂替；要開 bug 單則 trace 為必要條件，缺就停手回報。用機制擋掉「證據不足卻硬報」。
- **UI 是最會騙人的一層。** 樂觀更新會讓畫面顯示成功、後端其實失敗，所以「畫面說成功」一律要 API 狀態碼佐證。

