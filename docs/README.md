# 文件索引

使用入口在 [README](../README.md)，修改流程在 [維護指南](../CONTRIBUTING.md)。

## 架構與共用契約

- [架構與 bucket 邊界](architecture.md)
- [共享詞彙](glossary.md)
- [狀態檔與資料流](state-files.md)
- [Agent 交接](../references/agent-handoff.md)
- [Agent 授權](../references/agent-governance.md)
- [產物契約](../references/artifact-contract.md)
- [設定解析](../references/config-resolution.md)
- [系列讀者入口](series-reader-guide.md)

## 依工作找設計說明

| 工作 | 文件入口 |
| --- | --- |
| 建立受測專案設定 | [setup-sdet](meta.md#setup-sdet) |
| 探索與判定異常 | [explore](explore.md#explore)、[test-oracle](explore.md#test-oracle) |
| 封裝證據 | [evidence-package](observe.md#evidence-package)、[api-evidence](observe.md#api-evidence) |
| 找 bug、驗證、開單與修復 | [bug-hunter](agents.md#bug-hunter)、[bug-verifier](agents.md#bug-verifier)、[issue-quality-gate](agents.md#issue-quality-gate)、[triage](agents.md#triage)、[bug-fixer](agents.md#bug-fixer) |
| 維護一支測試 | [failure-analysis](maintain.md#failure-analysis)、[test-heal](maintain.md#test-heal)、[flaky-detect](maintain.md#flaky-detect) |
| 維護整批 CI | [ci-pipeline](infra.md#ci-pipeline)、[pipeline-triage](infra.md#pipeline-triage)、[quality-gate](infra.md#quality-gate) |
| 規劃、追蹤與放行 | [test-planning](workflow.md#test-planning)、[traceability](workflow.md#traceability)、[release-signoff](workflow.md#release-signoff) |
| 成本與模型選擇 | [route-by-risk](economics.md#route-by-risk)、[sdet-economics](economics.md#sdet-economics) |
| 不確定入口 | [ask-sdet](meta.md#ask-sdet) |

`skills/` 是執行指令，這裡是設計理由。測試教材與歷史實測在 [tests/README.md](../tests/README.md)，狀態範本用法在 [state-templates/README.md](../state-templates/README.md)。
