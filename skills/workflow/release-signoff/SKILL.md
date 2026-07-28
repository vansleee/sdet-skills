---
name: release-signoff
description: 彙整測試結果、未解 issue、覆蓋與風險，做「這一版能不能出」的專案層級放行判斷。要 release 前簽核 / 品質把關時使用。關鍵詞：放行、sign-off、release、能不能出、上線把關、release gate。
disable-model-invocation: true
---

# Release Sign-off（專案層級）

輸入一個候選版本，輸出 `go` / `no-go` / `conditional-go` + 逐條證據 + 可稽核的簽核紀錄。設計理念見 `docs/workflow/release-signoff.md`。

> **三層閘門分工**：`issue-quality-gate`（一張單能不能開）→ `infra/quality-gate`（一個 build 能不能放行）→ **本 skill**（整個 release 對需求與風險能不能簽出去）。本層**吃下層產物當證據，不重跑下層**。
> 狀態檔：`signoffs/<version>.yaml`（範本 `signoff.example.yaml`）。

## 輸入 / 輸出
- **輸入**：版本識別（tag / milestone）＋ `traceability.yaml`（覆蓋）＋ open issue（`gh issue list --milestone <m>`，分 blocker / 非 blocker）＋ `pipeline-gate.yaml`（build 層裁決）＋ `flaky-registry.yaml`（關掉的覆蓋）＋ `knowledge/`（風險基準）＋ 準則（`config/sdet-config.yaml` 的 `signoff`）。
- **輸出**：裁決 ＋ 逐條評估表 ＋ no-go 時的最短補完清單 ＋ 寫入 `signoffs/<version>.yaml`。

## 準則（門檻讀 config，不寫死）

| # | 條件 | 判準 | 證據來源 |
|---|---|---|---|
| 1 | `high_risk_covered` | `risk_score ≥ signoff.high_risk_threshold` 的需求全部 `covered` | `traceability.yaml` |
| 2 | `no_open_blocker` | 此 milestone 無 open blocker | `gh issue list` + `issues-index.yaml` |
| 3 | `build_gate_passed` | 最新 `pipeline-gate.yaml` 為 `PASS`（`OVERRIDE` → 見下）| `quality-gate` |
| 4 | `known_issues_registered` | 非 blocker 的已知問題全部列冊、有 owner | `issues-index.yaml` |
| 5 | `quarantine_disclosed` | 隔離中的測試已列出，逾期數 ≤ `signoff.max_expired` | `flaky-registry.yaml` |

**下層是 `OVERRIDE` 時，第 3 條不自動算 pass**：把 override 的理由原文抄進本層報告，標 `conditional-go` 交人判。下層硬推過的東西，不該在上層安靜地變成綠燈。

## 步驟
1. **收證據**：讀上表來源。可先叫 `status-report` 產 `release-readiness` 當素材。
2. **逐條評估**：`pass` / `fail` / `inconclusive`，每條寫 `basis` 指向具體出處。
3. **缺證據標 `inconclusive`**，**不得當 pass**。整體降為 `no-go` 或 `conditional-go`。
4. **裁決**：
   - 全 `pass` → `go`
   - 任一 `fail` → `no-go`
   - 有 `inconclusive`、或下層 `OVERRIDE`、或人願意承擔特定已知風險 → `conditional-go`（**條件要寫成可檢查的句子**，如「上線後 24h 內監控 X，超標即回滾」）
5. **產補完清單**（`no-go` 必附）：缺什麼、誰補、預估多久——讓「不能出」變成可執行的待辦，而不是一句否決。
6. **確認再寫**：把裁決表列給使用者，得同意才寫 `signoffs/<version>.yaml`。
7. **標記 AI 身分**：報告開頭加 `> *This assessment was compiled by AI. The sign-off decision belongs to a human.*`

## 鐵則
- **只裁決與留痕，不執行 release。** 不打 tag、不 deploy、不 merge（`merge_pr` 在 `config/governance.yaml` 的 `forbidden` 名單）。
- **`inconclusive` 不得當 pass。** 「查不到」和「沒問題」是兩件事。
- **簽核人是人。** 本 skill 產的是評估與紀錄；`signed_by` 一欄由人填，agent 不代簽。
- **不重跑下層。** build 綠不綠問 `pipeline-gate.yaml`，不自己再跑一次測試——重跑會得到不同結果，然後沒人知道該信哪個。
- **`conditional-go` 的條件必須可檢查。** 「小心一點」不是條件；「24h 內錯誤率 > 1% 即回滾，由 X 監控」才是。
- **關掉的覆蓋一定要揭露。** 隔離中的測試數要出現在報告正文，不是附註。

## 輸出（格式，非某次執行結果）
```yaml
# signoffs/v2.4.0.yaml
version: v2.4.0
evaluated_at: 2026-07-29T14:00:00Z
checks:
  high_risk_covered:       { result: fail, basis: "REQ-CHECKOUT-006 risk 0.71 為 gap(traceability.yaml)" }
  no_open_blocker:         { result: pass, basis: "milestone v2.4.0 無 open blocker" }
  build_gate_passed:       { result: pass, basis: "pipeline-gate.yaml 2026-07-29 PASS @ abc1234" }
  known_issues_registered: { result: pass, basis: "3 筆已知問題皆列冊且有 owner" }
  quarantine_disclosed:    { result: pass, basis: "隔離 9 支,逾期 2 ≤ max 3" }
verdict: no-go               # go | no-go | conditional-go
quarantine_note: "本版有 9 支測試被隔離(其中 checkout/coupon、cart/remove、login/sso),該區覆蓋為關閉狀態。"
completion_plan:             # no-go 必附
  - what: "補 REQ-CHECKOUT-006（折扣碼 × 點數）的測試"
    who: "<github handle>"
    eta: "2 天"
    next: "交 test-planning → test-author"
conditions: []               # conditional-go 時填,每條要可檢查
signed_by: null              # 由人填,agent 不代簽
note: "This assessment was compiled by AI. The sign-off decision belongs to a human."
```

## 上下游
上游：`traceability`（覆蓋）、`quality-gate`（build 裁決）、`flaky-manager`（隔離名單）、`status-report`（release-readiness 素材）、`triage`（issue 現況）。下游：人（簽核）；`no-go` 的補完清單回 `test-planning` 排下輪。
