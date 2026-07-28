---
name: release-signoff
description: 彙整測試結果、未解 issue、覆蓋與風險，做「這一版能不能出」的專案層級放行判斷。要 release 前簽核 / 品質把關時使用。關鍵詞：放行、sign-off、release、能不能出、上線把關、release gate。
---

# Release Sign-off

> 狀態：骨架（預留，TODO 待實作）

release 前的專案層級品質閘：彙整覆蓋（traceability）、未解 issue、風險，回答「這版能不能出、還缺什麼」，並留下可稽核的放行紀錄。

> 定位（與其他閘門區分）：`agents/issue-quality-gate` 管「單張 issue 能不能開」、`infra/quality-gate` 管「pipeline 能不能放行」、本 skill 管「整個 release 對需求/風險能不能簽出去」——一層比一層高。

## TODO
- [ ] 定義輸入（traceability 覆蓋 + 未解 issue + 風險）/ 輸出（go / no-go + 理由 + 待辦）
- [ ] 寫執行步驟；放行/擋下都要留痕（誰、何時、理由），受 `config/governance.yaml` 分級管制
- [ ] 讀 `knowledge/`（風險基準）與 `traceability` 產物
- [ ] 補 `agents/openai.yaml` 與 `docs/workflow/release-signoff.md`
