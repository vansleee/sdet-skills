# 文件索引

使用入口在 [README](../README.md)，修改流程在 [維護指南](../CONTRIBUTING.md)。

## 架構與共用契約

- [架構與 bucket 邊界](../architecture/sdet-skills-architecture.md)
- [狀態檔與資料流](state-files.md)
- [Agent 交接](../references/agent-handoff.md)
- [Agent 授權](../references/agent-governance.md)
- [產物契約](../references/artifact-contract.md)
- [設定解析](../references/config-resolution.md)
- [系列讀者入口](series-reader-guide.md)

## 依工作找設計說明

| 工作 | 文件入口 |
| --- | --- |
| 建立受測專案設定 | [setup-sdet](meta/setup-sdet.md) |
| 探索與判定異常 | [explore](explore/explore.md)、[test-oracle](explore/test-oracle.md) |
| 封裝證據 | [evidence-package](observe/evidence-package.md)、[api-evidence](observe/api-evidence.md) |
| 找 bug、驗證、開單與修復 | [bug-hunter](agents/bug-hunter.md)、[bug-verifier](agents/bug-verifier.md)、[issue-quality-gate](agents/issue-quality-gate.md)、[triage](agents/triage.md)、[bug-fixer](agents/bug-fixer.md) |
| 維護一支測試 | [failure-analysis](maintain/failure-analysis.md)、[test-heal](maintain/test-heal.md)、[flaky-detect](maintain/flaky-detect.md) |
| 維護整批 CI | [ci-pipeline](infra/ci-pipeline.md)、[pipeline-triage](infra/pipeline-triage.md)、[quality-gate](infra/quality-gate.md) |
| 規劃、追蹤與放行 | [test-planning](workflow/test-planning.md)、[traceability](workflow/traceability.md)、[release-signoff](workflow/release-signoff.md) |
| 成本與模型選擇 | [route-by-risk](economics/route-by-risk.md)、[sdet-economics](economics/sdet-economics.md) |
| 不確定入口 | [ask-sdet](meta/ask-sdet.md) |

`skills/` 是執行指令，這裡是設計理由。測試教材與歷史實測在 [tests/README.md](../tests/README.md)，狀態範本用法在 [state-templates/README.md](../state-templates/README.md)。
