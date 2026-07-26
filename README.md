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
**agents/** bug-hunter(user) · bug-verifier · issue-quality-gate · triage(user) · bug-fixer · duty-oncall(user)
**maintain/**(顧好每一支測試) test-author(user) · test-design(ref) · test-data · failure-analysis · flaky-detect · test-heal · re-run-gate · test-prune
**infra/**(顧好整條生產線) ci-pipeline · test-parallelize · test-env · pipeline-read · pipeline-triage(user) · flaky-manager · quality-gate · pipeline-observability · governance(config)
**economics/** route-by-risk · sdet-economics(ref)
**meta/** ask-sdet(user)

## 其他
- `config/` — 後端設定(CI / issue-tracker / product / governance),祕密走 env
- `references/` — test-design / tours / heuristics 等參考文件
- `docs/` — 每支 skill 的設計理念說明頁 + `state-files.md`(資料流)

**「一筆 vs 一批」:** maintain/ 修一支測試,infra/ 顧整批 pipeline。
