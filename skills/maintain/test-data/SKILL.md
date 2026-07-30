---
name: test-data
description: 讓一支測試自己準備、自己清掉它要的資料：fixture 走 API 建立、唯一標記防撞、teardown 保證清理。測試需要前置資料時使用；根因是測資污染或搶資源時由 `failure-analysis` / `flaky-detect` 轉過來。
---

# Test Data（一支）

輸入一支測試對資料的需求（或一筆被 `failure-analysis` 判為 `test-data` 的失敗），輸出 fixture（建立＋清理）與一份「這支測試建立了什麼」的 annotation。設計理念見 `docs/maintain/test-data.md`。

> 原則：**測試要用的資料，測試自己生、自己收。** 「環境裡本來就有那筆資料」是 flaky 的主要來源之一。

## 前置（缺了就停手回報，不要自己編）
- 建資料的 API 端點、測試帳號來源讀 `config/product-context.md`；憑證只走環境變數，**不寫進 fixture、也不寫進本文件**。
- `reset_shared_env`、`truncate_shared_db` 在 `config/governance.yaml` 屬 **forbidden**：任何情況都不做，即使有人開口要求。清理只清自己建的東西。

## 五條紀律
1. **走 API 不走 UI 建資料。** 快、穩，而且不會讓「前置操作」污染被測行為本身。
2. **每筆資料帶唯一標記**（時間戳＋亂數，如 `sdet-<ts>-<rand>`），平行執行才不會互撞、事後也追得回來。
3. **清理放 teardown，且失敗時也要跑到。** 用 fixture teardown／`finally`，不要放在測試最後一行，測試紅了就跑不到。
4. **清理失敗要讓測試明確報錯**，不得靜默吞掉。沒清掉的資料就是下一支測試的 flaky。
5. **不依賴既有資料、不共用狀態。** 不用「環境裡那個固定帳號」；每支測試的世界自己搭、自己拆。

## 輸出（格式，非某次執行結果）
fixture 檔一份，加上附在測試上的 annotation：
```yaml
nodeid: "<file> > <test name>"
created:
  - kind: <資源型別>
    id: "sdet-<ts>-<rand>"
    via: api
cleanup: teardown            # 保證執行
cleanup_on_failure: true
cleanup_error_policy: fail-loud
```

## 規則
- **只碰自己這支測試的資料**：產品碼、斷言、別支測試的資料都不動。
- 隔離慣例（唯一前綴）沿用 `test-env` 那一套，不各發明各的。

## 上下游
上游：`test-author`（新測試要前置資料）、`failure-analysis`（判 `test-data`）、`flaky-detect`（`data-pollution` / `parallel-race`）、`test-env`（提供前綴慣例與環境策略）。下游：`test-heal`（測試碼本身要修）、`test-parallelize`（測資唯一是平行的前置檢查之一）。
