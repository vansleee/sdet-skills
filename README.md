# sdet-skills

可重用的 Agentic SDET 技能組:**GitHub Actions · Playwright (TypeScript) · GitHub Issues**。

## 安裝
```bash
bash scripts/link-skills.sh      # 把 skill link 進 ~/.claude/skills
```
或當 Claude Code 外掛安裝(見 `.claude-plugin/`)。

## 第一步
```
/setup-sdet
```

## Skill 目錄(依 bucket)

**foundation/** setup-sdet(user) · product-context(ref)
**observe/** evidence-package · structured-result · classify-anomaly
**explore/** exploration-charter(user) · explore · test-oracle
**agents/** bug-hunter · bug-verifier · issue-quality-gate · triage · bug-fixer · duty-oncall(user)
**maintain/**(顧好每一支測試) test-author(user) · test-design(ref) · test-data · failure-analysis · flaky-detect · test-heal · re-run-gate · test-prune
**infra/**(顧好整條生產線) ci-pipeline(user) · test-parallelize · test-env · pipeline-read · pipeline-triage(user) · flaky-manager · quality-gate(user) · pipeline-observability · governance(config)
**economics/** route-by-risk · sdet-economics(ref)
**workflow/**(把 SDET 接進團隊/SDLC) test-planning · traceability · status-report · release-signoff(user)
**meta/** ask-sdet(user)

## 四層：能力 / 事實 / 流程 / 設定
- `skills/` — **能力**（產品無關、可重用）
- `knowledge/` — **產品事實**（產品專屬,是 test-oracle 的規格判準;真檔 gitignore,只留 `*.example.md`）
- `skills/workflow/` — **專案流程**（讀 knowledge + 專案設定）
- `config/` — **設定**（後端/授權,祕密走 env）

完整說明見 `architecture/sdet-skills-architecture.md`。

## 其他
- `config/` — 後端設定(CI / issue-tracker / product / governance),祕密走 env
- `knowledge/` — 受測產品的事實(依規模:單檔 → domains/ 多檔 → RAG/MCP)
- `references/` — test-design / tours / heuristics / confidence / bug-fingerprint / test-health-metrics / traceability-mapping 等參考文件(**演算法放這裡**)
- 根目錄 `*.example.yaml` — 狀態檔範本(calibration / known-false-positives / issues-index / flaky-registry / pipeline-gate / traceability / signoff),複製成同名真檔使用
- `docs/` — 每支 skill 的設計理念說明頁 + `state-files.md`(資料流)

**「一筆 vs 一批」:** maintain/ 修一支測試,infra/ 顧整批 pipeline。

## 兩條迴圈

**infra(生產線)**
`route-by-risk` → `ci-pipeline`(掛 `test-env` / `test-parallelize`)→ run → `pipeline-read` → `pipeline-triage` → `failure-analysis` / `test-heal` / `flaky-manager` → `quality-gate` → `pipeline-observability` —(超標指標路由回上游)→

**workflow(團隊/SDLC)**
`test-planning` →(charter / 自動化)→ 執行 → `traceability` —(gap 回饋)→ `test-planning`;`status-report` 彙整 → `release-signoff` 裁決

**三層閘門:** `issue-quality-gate`(一張單)→ `quality-gate`(一個 build)→ `release-signoff`(一版 release)。上層吃下層產物當證據,不重跑下層;三個獨立狀態檔,見 `docs/state-files.md`。
