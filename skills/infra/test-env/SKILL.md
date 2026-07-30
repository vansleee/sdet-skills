---
name: test-env
description: 決定整套測試的環境策略：ephemeral 還是共享+namespace、怎麼 seeding、怎麼隔離狀態，並產出掛進 CI 的前置/收尾步驟。禁止重置共享環境。要決定測試跑在哪、環境髒了、要判斷是不是環境壞掉時使用；`ci-pipeline` 要掛環境步驟、`test-parallelize` 要確認隔離可行時也用。
---

# Test Env（一批）

輸入一套測試的環境需求，輸出環境策略 + seeding/teardown 步驟 + smoke check。設計理念見 `docs/infra/test-env.md`。

> 一支 vs 整環境：`test-data` 管**一支測試**自備自清它要的資料；本 skill 管**整套測試**跑在哪、怎麼隔離。兩者共用同一套唯一標記慣例（見下）。

## 輸入 / 輸出
- **輸入**：套件規模、是否要平行（問 `test-parallelize`）、前置資料規模、環境清單（讀 `config/sdet-config.yaml` 的 `env`，URL/帳密走 env var）。
- **輸出**：策略決定（`ephemeral` / `shared-namespaced`）＋ seeding 與 teardown 步驟（掛給 `ci-pipeline`）＋ smoke check 指令與判準。

## 步驟
1. **盤點環境**：從 `config/` 讀環境清單與各自用途；祕密只從 env var 取（`BASE_URL`、`TEST_USER` …），一律不落地。
2. **選策略**（見下表）。
3. **定 seeding**：走 **API**（或 CLI / factory），**不走 UI**（慢又脆）、**不直插 DB**（繞過驗證，種出產品自己不接受的資料）。seeding 失敗要讓 pipeline 直接紅，不要帶著半套資料往下跑。
4. **定隔離慣例**：每個 run（或每個 worker）配一個唯一前綴 `t-<run_id>-<worker>-`，所有測試建立的資料都帶這個前綴，與 `test-data` 用同一套，不要各發明各的。
5. **定 teardown**：依前綴刪除自己建的資料，`if: always()` 跑。**只刪自己前綴的東西**。
6. **產 smoke check**：跑測試前先驗環境活著（首頁 200、登入 API 200、關鍵依賴可達）。不過就直接 fail fast，標記 `environment`，別讓幾百支測試紅一片後再回頭猜。
7. **交出去**：把 seeding / teardown / smoke 三段步驟交給 `ci-pipeline` 掛進 workflow。

## 策略選擇

| 策略 | 適用 | 代價 |
|---|---|---|
| `ephemeral`（每 run 起一套） | 資料破壞性強、要平行、環境可容器化 | 起環境的時間與成本 |
| `shared-namespaced`（共享環境 + 唯一前綴隔離） | 環境昂貴或起不動（第三方依賴、SSO） | 要嚴守前綴紀律，且**永遠不能整個重置** |

> 大多數專案落在 `shared-namespaced`。選它就等於接受下面那條鐵則。

## 鐵則
- **禁止重置共享環境。** `reset_shared_env`、`truncate_shared_db` 在 `config/governance.yaml` 的 `forbidden` 名單，**沒有任何 override 路徑**。理由：共享環境上有別人的資料與正在跑的驗證；「清乾淨比較好測」對你成立，對隔壁那位不成立。環境髒了就用唯一前綴繞開它，不是清掉它。
- **只刪自己前綴的資料。** teardown 的刪除條件必須帶 run 前綴；沒有前綴的全域刪除等同重置，同樣禁止。
- **seeding 走 API，不直插 DB。** 直插 DB 種出的資料常常是產品邏輯不承認的狀態，會製造假 bug。
- **環境問題交 infra 修環境。** smoke check 不過 → 分類 `environment` → 修環境（`failure-analysis` 也是這樣分流的）；測試維持原樣，放寬它只是把壞環境藏起來。

## 輸出（格式，非某次執行結果）
```yaml
strategy: shared-namespaced
base_url_source: env:BASE_URL          # 祕密走 env,不落地
namespace_prefix: "t-${{ github.run_id }}-"
smoke_check:
  - "curl -fsS $BASE_URL/health"
  - "api login as $TEST_USER -> expect 200"
  on_fail: "標記 environment、fail fast,不跑測試套件"
seeding:
  method: api
  steps: ["POST /api/accounts (帶前綴)", "POST /api/products x3"]
teardown:
  when: always
  scope: "只刪 name/email 前綴符合 namespace_prefix 者"
forbidden_here: [reset_shared_env, truncate_shared_db]
```

## 上下游
上游：`ci-pipeline`（要掛環境步驟時呼叫）、`test-parallelize`（平行前要先確認隔離可行）。下游：smoke check 結果供 `failure-analysis` / `pipeline-triage` 判 `environment` 類根因；隔離慣例供 `test-data` 沿用。
