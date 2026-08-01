# sdet-skills

可重用的 Agentic SDET 技能組：**GitHub Actions · Playwright (TypeScript) · GitHub Issues**。

## 安裝

在 Claude Code 裡加入這個 marketplace，然後安裝外掛：

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

各 bucket 負責什麼、為什麼這樣切，見 `architecture/sdet-skills-architecture.md`。

## 設計原則

三條原則決定了東西該放哪、什麼時候該開新 skill，完整說明都在
[`architecture/sdet-skills-architecture.md`](architecture/sdet-skills-architecture.md)：

- **四層分工** —— `skills/` 能力、`knowledge/` 產品事實、`skills/workflow/` 專案流程、`config/` 設定。skill 讀後三者，不內嵌。
- **一筆 vs 一批** —— `maintain/` 修一支測試，`infra/` 顧整批 pipeline。
- **畫面 vs 端點** —— 手段不同才成對開 skill，判準不同只加一張表。

三層閘門 `issue-quality-gate`（一張單）→ `quality-gate`（一個 build）→ `release-signoff`（一版 release），上層吃下層產物當證據，不重跑下層。

## 兩條迴圈

**infra（生產線）**
`route-by-risk` → `ci-pipeline`（掛 `test-env` / `test-parallelize`）→ run → `pipeline-read` → `pipeline-triage` → `failure-analysis` / `test-heal` / `flaky-manager` → `quality-gate` → `pipeline-observability` —（超標指標路由回上游）→

**workflow（團隊/SDLC）**
`test-planning` →（charter / 自動化）→ 執行 → `traceability` —（gap 回饋）→ `test-planning`；`status-report` 彙整 → `release-signoff` 裁決

## 目錄

| 路徑 | 放什麼 |
| --- | --- |
| `config/` | 後端設定（CI / issue-tracker / product / governance / test-style），祕密走 env |
| `knowledge/` | 受測產品的事實 |
| `references/` | test-design / tours / heuristics / confidence / bug-fingerprint / test-health-metrics 等參考文件（**演算法放這裡**）|
| `state-templates/` | 狀態檔範本，複製到 repo 根成同名真檔使用 |
| `tests/` | Playwright 測試與 `maintain/` 的實測基準（見 `tests/README.md`）|
| `docs/` | 每支 skill 的設計理念 + `state-files.md`（跨 skill 資料流）|
| `output/` | 所有執行期產物，不進版控 |

`config/test-style.md` 是這個專案的測試碼風格，`test-author` / `api-test-author` / `test-heal` 動筆前讀它；機械性規則（縮排、引號、import 順序）交 eslint／prettier，不寫在這裡。
