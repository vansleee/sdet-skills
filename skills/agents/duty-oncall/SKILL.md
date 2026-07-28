---
name: duty-oncall
description: 排程或使用者觸發的「獨立值班」總編排：bug-hunter 找 → bug-verifier 獨立重現 → issue-quality-gate 把關 → 過關的交 triage 開單、可修的交 bug-fixer 開 PR（不 merge），全程受 governance 與預算管制，最後寫 runs/<date>.yaml 與五分鐘可複核的摘要。使用者說「值一班」「跑一輪完整流程」「oncall」時使用。關鍵詞：值班、oncall、排班、流水線、獨立值勤。
disable-model-invocation: true
---

# Duty Oncall (v0.1)

輸入一份 charter（`charters/<slug>.yaml`），輸出一輪完整值勤 ＋ `runs/<date>.yaml` ＋ 值班摘要。設計理念見 `docs/agents/duty-oncall.md`。

> **它不發明能力，它把第四週所有代理人排成一次可重複、可稽核的值班。** 授權不是放手：發起交給排程，**不可逆的最後一下（merge、拍板）永遠留給人**。

## 前置（缺了就停手回報，不硬跑）
- 第四週全套就緒：`bug-hunter` / `bug-verifier` / `issue-quality-gate` / `triage` / `bug-fixer`。
- `config/governance.yaml`、`config/sdet-config.yaml`（預算與門檻）、charter 檔可讀。
- `gh auth status` 已登入（triage / fixer 會用到）。

## 執行順序（逐站接力，站與站之間交的是檔案，不是對話記憶）

1. **獵** — `bug-hunter` 依 charter 跑一輪（四道守門在它體內），交回候選清單。
2. **驗** — 每個候選交 `bug-verifier` 獨立重現，得 `verdicts/`。
3. **把關** — 全數過 `issue-quality-gate`，得 `gate.yaml`（pass / hold / block）。
4. **分派** — 只動 pass 的：
   - 一律交 `triage` 開單（開單前確認規則依 triage 自己的鐵則）。
   - **範圍清楚、可修**的再交 `bug-fixer` 開 PR（標 ready-for-review，**不 merge**）。
   - hold → 人工佇列；block → 待規格／待人判。**不替人拍板。**
5. **記帳** — 寫 `runs/<date>.yaml`（格式見下）。**當下埋、不能事後補**：今天不記 tokens 與 gate_passed，之後就算不出 ROI 與校準。
6. **留摘要** — 一份五分鐘能複核完的值班摘要（開了什麼、待判什麼、花了多少、forbidden 動作幾次）。

## 輸出
```yaml
# runs/<date>.yaml
date: <date>
charter: charters/<slug>.yaml
tokens: { input: <n>, output: <n> }
duration_min: <n>
model_mix: { hunt: <model>, verify: <model> }
findings: <n>                # hunter 候選數
gate_passed: <n>
issues_opened: <n>
prs_opened: <n>
held_for_human: <n>
forbidden_attempts: 0        # 不為 0 就是事故,要報
confirmed_by_human: null     # 待回填
```

## 鐵則
- **編排不越權。** 各站自己的鐵則與確認規則原封生效；oncall 不代跳任何一道門、不代任何人確認。
- **絕不 merge、絕不碰 `governance.yaml` forbidden 清單**（`merge_pr` / `reset_shared_env` / `truncate_shared_db`）。
- 守 `budget.max_tokens_per_run`；超了就地收班、如實記錄，**不是缺點**。
- 任何一站失敗 → 記進 run log、往下能走多遠走多遠，**不得無聲吞掉**。
- 摘要要讓人**五分鐘複核完**，不是要人重跑一遍。

## 驗收（跑完自己對一次）
- 每一道門都有生效嗎（誤報擋了、重複併了、needs-spec 沒硬開、PR 沒被 merge）？
- `runs/<date>.yaml` 是**當下**寫的、量都在嗎？
- hold / block 的都進了看得到的佇列嗎？
