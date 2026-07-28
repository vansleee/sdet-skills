---
name: traceability
description: 維護「需求 ↔ 測試 ↔ finding」的覆蓋對照，指出哪些需求還沒被覆蓋、哪些 finding 沒對應到需求。要看覆蓋率、追溯、什麼還沒測時使用。關鍵詞：覆蓋、追溯、traceability、需求對照、gap、還沒測。
---

# Traceability

> 狀態：骨架（預留，TODO 待實作）

把 `knowledge/` 的需求 / 業務規則，對照既有測試與 findings，產出一份覆蓋對照表：哪些需求已覆蓋、哪些是 gap、哪些 finding 是需求外的意外收穫。

## TODO
- [ ] 定義輸入（需求清單 + 測試清單 + findings）/ 輸出（覆蓋對照表 + gap 清單）
- [ ] 寫執行步驟：建立需求 ↔ 測試 ↔ finding 的對應，標出未覆蓋
- [ ] 讀 `knowledge/`（需求來源）；狀態檔沿用 `docs/state-files.md` 慣例
- [ ] 補 `agents/openai.yaml` 與 `docs/workflow/traceability.md`
