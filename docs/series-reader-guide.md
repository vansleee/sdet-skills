# 系列讀者入口

[鐵人賽系列](https://ithelp.ithome.com.tw/users/20169442/ironman/9416) 的逐篇內容與本 repo 的對照仍待文章審查確認。以下依本 repo 的架構、專案規則與測試教材提供入口，尚未宣稱各篇文章已驗證。

## Day 03 新讀者流程

先完成掛載，再從 `/ask-sdet` 說明需求。舊文章的 `/setup-sdet` 直接入口保留。以下以 Claude Code 與本 repo 的 symlink 安裝為例；終端指令與 Claude 對話指令分開執行。需要 Git、Claude Code、Node.js 20 以上，以及檢查腳本使用的 Python 3 與 Bash。

### 1. 取得 repo 並記錄版本

新讀者在終端執行：

```bash
mkdir -p ~/workspace
cd ~/workspace
git clone https://github.com/vansleee/sdet-skills.git
cd sdet-skills
git rev-parse HEAD
git status --short
```

已有 checkout 時，直接 `cd ~/workspace/sdet-skills` 後核對版本與修改，不再 clone。記下 commit，後續遇到文章與檔案不一致時，才能區分版本差異。這次整理尚未發布；新 clone 取得的是 GitHub 當下版本，不會取得本機未提交文件。Day 27 的版本落差見下方「已核對的跟做紀錄」。

### 2. 掛載 SDET skills，再確認 Claude 載入

`link-skills.sh` 會把掃描到的 skill 連到 `~/.claude/skills/<name>`，並更新同名連結。若該位置已有要保留的個人 skill，先處理名稱衝突，再執行：

```bash
bash scripts/link-skills.sh
test -f ~/.claude/skills/ask-sdet/SKILL.md
test -f ~/.claude/skills/setup-sdet/SKILL.md
claude
```

腳本應印出 `linked setup-sdet` 等訊息，`test` 應成功退出。在 repo 根目錄啟動 Claude，讓共用文件與後續 config 路徑有明確的工作目錄。在 Claude 對話輸入 `/skills`，確認 `ask-sdet` 與 `setup-sdet` 可見。

[Claude 官方文件](https://code.claude.com/docs/en/skills#edit-a-skill-during-a-session) 說明目前版本會在 session 內偵測個人與專案 skill 變更；不用一律重啟。若頂層 skills 目錄在 session 開始時不存在，執行 `/reload-skills` 再確認。官方也支援個人 skill 目錄中的 symlink；若仍未載入，核對連結目標與實際 Claude 版本，不把 `/clear` 當成安裝驗收。

若改用 README 的外掛安裝方式，省略 symlink 步驟，從 `/skills` 查找外掛提供的 setup 入口；不要同時照兩條路安裝。

### 3. 選擇 Playwright 用途並準備工具

| 用途 | 工具與前置條件 | 驗收 |
| --- | --- | --- |
| 執行 repo 的 TypeScript 測試 | repo 的 `@playwright/test`；先 `npm ci`，真正跑瀏覽器前再 `npx playwright install chromium` | `npx playwright test --config tests/playwright.config.ts --list --reporter=line` 可列出測試 |
| 讓 agent 即時操作瀏覽器探索 | 額外的 `@playwright/cli`；只有選這條探索路徑才需安裝 | `playwright-cli --version` 與 `playwright-cli --help` 能執行 |

測試 runner 的設定放在 `tests/`，所以要帶 `--config tests/playwright.config.ts`；不要照抄沒有設定路徑的裸 `npx playwright test`。列出測試不代表測試已通過，也不需要先安裝瀏覽器。真正執行教材時用 [測試指南](../tests/README.md) 的 `npm run test:clean` 等指令。

若選擇 `playwright-cli` 做即時探索，在終端依 [Microsoft 安裝說明](https://github.com/microsoft/playwright-cli) 執行：

```bash
npm install -g @playwright/cli@latest
playwright-cli --version
playwright-cli install --skills
playwright-cli --help
```

最後兩個安裝步驟的作用不同：npm 安裝可執行程式，`install --skills` 安裝它自己的操作 skill。依 [Playwright skill 文件](https://playwright.dev/agent-cli/skills)，預設寫進目前工作目錄的 `.claude/skills/playwright-cli`；它不會掛載本 repo 的 SDET skills，也不會取代 `npm ci`。選擇 Playwright MCP 時則提供該工具，於 setup 記錄實際 trace 來源，不必另裝 CLI。

### 4. 從共同入口接入 setup，讀回設定產物

在 Claude 對話執行：

```text
/ask-sdet 我要設定這個專案，之後探索找 bug
```

ask-sdet 會讀取 setup-sdet，接入同一份訪談；完成後回到原任務，不要求重述需求。只想設定時，仍可直接用 `/setup-sdet`。

依訪談指定產品、環境、issue tracker 與前一步選擇的 Playwright 工具。GitHub 流程需要 `gh auth status` 成功；沒有 GitHub issue repo 時可選本地 Markdown tracker。祕密只提供環境變數名稱，值留在環境中。

完成後要求 agent 依 [setup 契約](../skills/foundation/setup-sdet/SKILL.md) 重新讀回產物，核對工作目錄、專案 slug、base URL、Playwright config 與 trace 來源。單一既有預設專案沿用 `config/`，多專案使用 `config/<project>/`：

- `product-context.md`
- `ci-backend-github-actions.md`
- `issue-tracker-github.md` 或 `issue-tracker-local-md.md`
- `sdet-config.yaml`
- `test-style.md`

`governance.yaml` 不是 setup 的訪談產物，`knowledge/<project>/` 由人工維護。必要設定缺漏或讀不回產物時，補齊後重跑，不能只憑對話摘要宣稱完成。

### 5. 驗收安裝與 repo 檢查

在 repo 根目錄的終端執行既有檢查：

```bash
bash scripts/check-manifest.sh
python3 scripts/check-de-ai-tone.py
npm ci
npx playwright test --config tests/playwright.config.ts --list --reporter=line
```

manifest 應與檔案一致，文風檢查應通過，runner 應能列出測試。含本次整理的版本另可用 `npm run check` 與 `npm run test:list`。這些是安裝與設定檢查；探索尚未執行，不應期待此時已有 evidence 或 finding。

之後執行 `/exploration-charter` 定義範圍，再交給 `/bug-hunter`。實際產物依 [狀態檔契約](state-files.md) 放在 `output/`，不把刻意植入 bug 的練習站當成正式環境。

## 從案例找到實作

| 想跟做的工作 | Repo 入口 |
| --- | --- |
| 安裝與設定受測產品 | [README](../README.md)、[setup-sdet](../skills/foundation/setup-sdet/SKILL.md) |
| 定探索範圍並找 bug | [exploration-charter](../skills/explore/exploration-charter/SKILL.md)、[bug-hunter](../skills/agents/bug-hunter/SKILL.md) |
| 獨立重現與建單判斷 | [bug-verifier](../skills/agents/bug-verifier/SKILL.md)、[issue-quality-gate](../skills/agents/issue-quality-gate/SKILL.md) |
| 分辨產品錯誤、測試錯誤與 flaky | [測試教材與歷史實測](../tests/README.md) |
| 看整條 CI 與放行判準 | [文件索引](README.md)、[架構文件](../architecture/sdet-skills-architecture.md) |

## 書稿與執行產物

依 [AGENTS.md](../AGENTS.md)，書稿維護於獨立 private repo `vansleee/agentic-sdet-book`，不在本 repo 發布。公開讀者從上方系列連結閱讀文章。

文章或測試教材引用的 `output/` 是作者本地證據，受 gitignore 保護，clone 後不會取得。請用 [測試指南](../tests/README.md) 與 [狀態範本](../state-templates/README.md) 重跑自己的案例；文中的歷史實測日期與結果不保證公開練習站今日仍有相同行為。

既有 `skills/`、`tests/`、`references/` 與架構文件路徑維持原位。後續文章審查若發現舊連結或名稱差異，先補對照，再評估改名。

## 已核對的跟做紀錄

本次核對 GitHub 後，確認以下關聯：

- [PR #19](https://github.com/vansleee/sdet-skills/pull/19) 已合併，加入 Playwright 教材與 CI。
- [PR #20](https://github.com/vansleee/sdet-skills/pull/20) 已於 2026-09-25 合併，說明標示為 iThome Day 27 跟做案例。它補上結構化結果與含環境、嘗試編號的 artifact 名稱。
- [Issue #17 的修復留言](https://github.com/vansleee/sdet-skills/issues/17#issuecomment-5241139335) 說明 IDOR 缺陷是 `sprint5-with-bugs` 刻意植入的教材；修復在作者 fork 的 [PR #1](https://github.com/vansleee/practice-software-testing/pull/1)，本次核對仍未合併，等待人類 review。這是練習修復紀錄，不能當成正式環境事故或已發布修復。

本次整理的本機起點為 `e5b5f5c`，尚未包含 PR #20。若跟做 Day 27，先確認 checkout 已含該 PR，再依新版 artifact 契約操作；不要把遠端已合併與本機已更新視為同一件事。
