# 維護 sdet-skills

先讀 [AGENTS.md](AGENTS.md) 與 [架構文件](docs/architecture.md)。現有 skill 路徑是外掛清單與文章引用的入口；改名或搬移前，先列出受影響的引用與相容方案。

## 準備本地環境

需要 Node.js 20 以上、npm、Python 3 與 Bash。在 repo 根目錄執行：

```bash
npm ci
npm run check
npm run test:list
```

`check` 檢查 skill 登錄、入口檔案、維護 skill 的設定契約與中文文風；文風檢查目前只掃版控中的文件，新文件加入版控後再檢查一次。`test:list` 只確認 Playwright 能載入設定並列出測試，不會連線到受測產品。

## 修改 skill

1. 確認能力屬於哪個 bucket。手段相同、判準不同時，擴充既有 skill 的判準表。
2. 維護 `SKILL.md` 與 `agents/openai.yaml`。使用者呼叫的 skill 要同時設定 `disable-model-invocation: true` 與 `policy.allow_implicit_invocation: false`。
3. 新增、改名或改行為時，同步 [.claude-plugin/plugin.json](.claude-plugin/plugin.json)、[README](README.md) 與 [ask-sdet](skills/meta/ask-sdet/SKILL.md)。
4. 設計理由放 `docs/<bucket>.md`，一支 skill 一節；共用判準與演算法放 `references/`。產品事實與設定只提交範本。
5. 執行 `npm run check`。涉及測試行為時，再依 [測試指南](tests/README.md) 選受影響的測試。

設定與路由入口放 `skills/meta/`，文字工具放 `skills/writing/`。每支 skill 只登錄正式路徑，不要複製成另一支同名 skill。

## 選擇驗證範圍

| 改動 | 驗證 |
| --- | --- |
| 文件、skill 登錄 | `npm run check`，檢查相對連結 |
| Playwright 設定、測試碼 | `npm run test:list`，再跑受影響測試 |
| 正常回歸測試 | `npm run test:clean` |
| 產品 bug 示範 | `npm run test:with-bugs`，核對失敗斷言 |
| flaky 量測 | `npm run test:flaky`，記錄樣本數與失敗率 |

`npm test` 會包含刻意失敗的 `broken/` 與 `flaky/`，不能把全綠當成這個 repo 的驗收門檻。公開練習站可能變動或阻擋自動化，歷史結果見測試指南；新結果需附當次證據。

## 保護本地資料

修改前看 `git status --short` 與 `git diff`，保留別人的未提交修改。不要提交 `.env`、真實 config、產品知識或 `output/`。書稿在獨立 private repo；本 repo 的 `book/` 若有本地殘留，先查來源，不直接刪除或搬移。

副作用與授權規則見 AGENTS.md 和受測專案的 governance。提交、發布與 PR 依當次使用者授權處理。

## 比對遠端與本機版本

GitHub 顯示 PR 已合併，不代表本機 checkout 已包含它。先記錄 `git rev-parse HEAD` 與未提交修改，再比對合併 commit。若有本地修改，先保存修改，再選擇 merge 或 rebase；不要用強制重設覆蓋工作目錄。
