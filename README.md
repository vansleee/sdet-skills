# sdet-skills

一組 Claude Code skill，把測試工程師的判斷寫成 agent 讀得懂的流程：**自己探索找 bug、判定它是不是真的 bug、開單、修產品、顧測試、顧整條 CI 生產線**。

> A reusable Agentic SDET skill set for Claude Code — exploratory testing, bug triage, and CI pipeline care, built on Playwright and GitHub Actions. Documentation is in Traditional Chinese.

技術面固定在 **GitHub Actions · Playwright（TypeScript）· GitHub Issues**，其餘都是設定。

## 這東西想解決什麼

叫模型「幫我寫測試」很容易，它會生出跑得動的程式碼。難的是後面幾件事：

- 看到一個異常，它憑什麼說那是 bug，而不是環境壞了或測資髒了？
- 沒有腳本的時候，它怎麼決定下一步點哪裡，又怎麼避免鬼打牆？
- 它說找到 bug 了，你要不要信？誰來獨立驗一次？
- 一次 CI 紅了三十支，哪幾支是同一個根因，該找誰修？
- 哪些事它可以自己做，哪些要你點頭，哪些永遠不准？

這個 repo 把上面每一題做成一支 skill，彼此用名稱互相呼叫（`bug-hunter` 交給 `issue-quality-gate`，過了才輪到 `triage` 開單）。**產品知識與專案設定是輸入，不寫死在 skill 裡**，所以換一個受測產品只換 `knowledge/` 與 `config/`，能力本身帶著走。

## 需要什麼

- [Claude Code](https://code.claude.com)
- Node.js 20 以上（Playwright 用）
- `gh` CLI 並已登入，如果要用 GitHub Issues 那條路
- 一個受測產品。想先試跑的話，`charters/` 裡有幾份現成的 charter，打的是公開練習站（Toolshop、SauceDemo、TodoMVC）

## 安裝

```
/plugin marketplace add vansleee/sdet-skills
/plugin install sdet-skills@sdet-skills
```

37 支 skill 一次到位，`git pull` 之後跟著更新。清單見 `.claude-plugin/plugin.json`。

<details>
<summary>備用：symlink 到 <code>~/.claude/skills</code></summary>

不走外掛機制時用這個，效果一樣，但要自己 clone 這個 repo，而且新增 skill 之後得重跑一次。

```bash
bash scripts/link-skills.sh
```
</details>

## 第一步

```
/setup-sdet
```

它會一次問一個主題（受測產品、登入、CI、issue tracker、Playwright、門檻），把答案寫進 `config/`。**帳密只記變數名（`env:VAR`），不記值**，祕密走環境變數。跑完之後其他 skill 才知道要對誰工作。

`config/` 與 `knowledge/` 的真檔都不進版控，repo 裡只有 `*.example.md` 與 `*.example.yaml` 範本。

跑完可以從這裡開始：

```
/exploration-charter          # 把一個目標談成有邊界的探索章程
/bug-hunter                   # 照章程獵一輪，交回已判定、已去重的候選
/ask-sdet 我這個情況該用哪支    # 不確定用哪支的時候問它
```

## Skill 目錄（依 bucket）

**foundation/** setup-sdet(user) · product-context(ref)
**observe/** evidence-package · api-evidence · structured-result · classify-anomaly
**explore/** exploration-charter(user) · explore · test-oracle
**agents/** bug-hunter · bug-verifier · issue-quality-gate · triage · bug-fixer · duty-oncall(user)
**maintain/**（顧好每一支測試） test-author(user) · api-test-author(user) · test-design(ref) · test-data · failure-analysis · flaky-detect · test-heal · re-run-gate · test-prune
**infra/**（顧好整條生產線） ci-pipeline · test-parallelize · test-env · pipeline-read · pipeline-triage · flaky-manager · quality-gate(user) · pipeline-observability · governance(config)
**economics/** route-by-risk · sdet-economics(ref)
**workflow/**（把 SDET 接進團隊/SDLC） test-planning · traceability · status-report · release-signoff(user)
**meta/** ask-sdet(user)

標 `(user)` 的只在你叫它的時候才動，其餘由模型視情況自己呼叫；`(ref)` 是給其他 skill 讀的參考文件，不是流程。各 bucket 負責什麼、為什麼這樣切，見 [`architecture/sdet-skills-architecture.md`](architecture/sdet-skills-architecture.md)。

## 設計原則

三條原則決定了東西該放哪、什麼時候該開新 skill，完整說明都在架構文件：

- **四層分工** —— `skills/` 能力、`knowledge/` 產品事實、`skills/workflow/` 專案流程、`config/` 設定。skill 讀後三者，不內嵌。
- **一筆 vs 一批** —— `maintain/` 修一支測試，`infra/` 顧整批 pipeline。一批必須先合併根因再分析。
- **畫面 vs 端點** —— 手段不同才成對開 skill，判準不同只加一張表。不為 API 另立一套平行體系。

三層閘門 `issue-quality-gate`（一張單）→ `quality-gate`（一個 build）→ `release-signoff`（一版 release），上層吃下層產物當證據，不重跑下層。

會產生副作用的動作（開 issue、開 PR、改測試、重置環境、放行 release）一律先確認，並受 `config/governance.yaml` 的授權分級管制：可自主、要人審、永遠禁止。**合併 PR 不在任何 agent 的權限內。**

## 兩條迴圈

**infra（生產線）**
`route-by-risk` → `ci-pipeline`（掛 `test-env` / `test-parallelize`）→ run → `pipeline-read` → `pipeline-triage` → `failure-analysis` / `test-heal` / `flaky-manager` → `quality-gate` → `pipeline-observability` —（超標指標路由回上游）→

**workflow（團隊/SDLC）**
`test-planning` →（charter / 自動化）→ 執行 → `traceability` —（gap 回饋）→ `test-planning`；`status-report` 彙整 → `release-signoff` 裁決

## 目錄

| 路徑 | 放什麼 |
| --- | --- |
| `skills/` | 37 支 skill，每支有 `SKILL.md` 與 `agents/openai.yaml` |
| `config/` | 後端設定（CI / issue-tracker / product / governance / test-style），只 commit 範本，祕密走 env |
| `knowledge/` | 受測產品的事實，只 commit 範本 |
| `charters/` | 探索章程，一份一個任務，可重跑、可人審 |
| `references/` | test-design / tours / heuristics / confidence / bug-fingerprint / test-health-metrics（**演算法放這裡**）|
| `state-templates/` | 狀態檔範本，複製到 `output/` 成同名真檔使用 |
| `tests/` | Playwright 測試與 `maintain/` 的實測基準（見 [`tests/README.md`](tests/README.md)）|
| `docs/` | 每支 skill 的設計理念，加上 `state-files.md` 這份跨 skill 資料流 |
| `output/` | 所有執行期產物，不進版控 |

`tests/` 底下 `e2e/` 是正常測試、`broken/` 是穩定紅的反例、`flaky/` 是時紅時綠的。後兩者刻意留著，用來校準 `failure-analysis` 分不分得出「測試的錯」與「產品的錯」；`retries: 0` 也是刻意的，重試會把 flaky 蓋掉。

## 狀態

這是我自己在用的東西，還在長。介面可能會改，skill 的邊界也還在調整。拿去用、拿去改都可以，遇到判斷不合理的地方歡迎開 issue 討論。

MIT License。
