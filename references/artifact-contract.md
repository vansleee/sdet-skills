# Artifact 命名契約（reference，被 ci-pipeline / pipeline-read / test-parallelize 讀）

下游一切分析都靠這幾個名字找檔案。**改名等於改 API**。改一處就要同步這張表與三支 skill。

| artifact 名 | 內容 | 上傳條件 | 誰讀 |
|---|---|---|---|
| `playwright-report` | HTML report | `if: always()` | `pipeline-read` / 人 |
| `test-results-json` | JSON / junit reporter 輸出 | `if: always()` | `pipeline-read`（解析失敗清單）|
| `traces` | `test-results/**/trace.zip` | `if: failure()` | `failure-analysis` / `evidence-package` |
| `blob-report-<shard>` | 分片的 blob report | `if: always()` | `test-parallelize` 的 merge job |
| `api-test-results-json` | API 測試 job 的 JSON / junit 輸出 | `if: always()` | `pipeline-read`（與 UI 失敗清單分開解析）|
| `api-evidence-<slug>` | `requests.jsonl` / `repro.sh` / `raw/`（憑證已遮蔽）| `if: failure()` | `failure-analysis` / `bug-verifier` |

保留天數讀 `config/sdet-config.yaml` 的 `ci.artifact_retention_days`（預設 7；trace 佔空間，別無腦設 90）。

## `if: always()` 不能省

測試紅了才最需要報告。紅了就不上傳，等於在最需要證據的時候把證據丟掉。
`traces` 與 `api-evidence-<slug>` 是例外，只在失敗時留。全留很快就把 storage 吃爆，且沒人看綠燈的 trace。

`api-evidence-<slug>` 上傳前必須確認憑證已遮蔽（`Authorization`、`Set-Cookie` 換成 `<redacted>`）。CI artifact 的可見範圍比本機大得多，遮蔽是上傳的前置條件，不是事後補救。

## 靜默失蹤（驗數要擋的東西）

**「全綠但少跑」比紅燈危險得多。** 紅燈會叫，少跑不會。它看起來就是一片乾淨的綠。

判準一條：`passed + failed + skipped == total`；分片時另加 `合併後 total == 分片前 total`。

不相等代表其中之一發生了：collection error、某片 shard 整個沒跑或沒回報、報告被截斷。
一律標 `count-mismatch` WARNING 並擋下，**不當成通過**。

讀它的地方：`pipeline-read`（步驟：驗數）、`test-parallelize`（合併報告後）、`quality-gate`（準則 `no_count_mismatch`）。
