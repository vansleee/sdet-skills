# Agent 交接契約

`agents/` 各站交接前讀本文件。共用 Claude Code、Codex 與 ChatGPT 的資料契約；建立獨立 context、操作產品與讀寫檔案時，使用當前平台實際提供的工具。

## 識別與設定

- 每筆交接帶 `project`、`session`、`finding_id`、`level`。`project: null` 明確表示預設專案；`level` 只用 `ui` 或 `api`，同時需要兩者時填 `evidence_levels: [ui, api]`。
- `session` 是 `output/sessions/<date>_<slug>/` 的目錄名，同一工作目錄內不得重複；同日重跑加序號。`finding_id` 對到該輪的 finding 檔，跨輪不得沿用同一組識別。
- 設定依 `references/config-resolution.md` 解析。交接欄位與 charter 不一致就退回修正，不把同一 finding 改掛到另一個專案。缺識別的舊資料先查來源，無法確認時不得猜成預設專案。
- 指紋用於同專案去重，校準用 `(project, session, finding_id)` 精確回填；兩者不可互代。

## 盲驗輸入

由 hunter 或呼叫 verifier 的編排者，從完整證據包另外建立 `output/evidence/<YYYYMMDD>-<任務代號>/blind/`。保留原包給 gate 與人複核，verifier 只收到 `blind/manifest.yaml`，不收到原包路徑或候選清單。

```yaml
project: null
session: "<date>_<slug>"
finding_id: F-001
level: api
evidence_levels: [api]
target: "<受測網址，不含憑證>"
preconditions: ["<必要資料與身分，只寫憑證環境變數名>"]
steps: ["<可從零重現的操作>"]
observed: "<待重現的客觀現象，不含缺陷裁定>"
constraints:
  out_of_bounds: ["<從 charter 原樣傳入的限制>"]
  budget: {}                 # 實際剩餘預算，取自解析後設定與本輪用量
raw_evidence: [raw/01-response.body.json]
repro: repro.sh              # 純 UI 可為 null
```

- 複製必要的原始證據進 `blind/`，所有證據路徑以該目錄為準。保留可重現內容並遮蔽祕密；不複製 `notes.md`、原 manifest、`results.yaml`、finding／gate／calibration、oracle 判定、confidence、推理或跨輪複現次數。
- `repro.sh` 必須用本輪憑證與新的輸出目錄，不能覆寫 hunter 證據。執行前檢查每個請求的目標、前置與副作用，再交 `api-evidence` 執行。
- verifier 可讀自身 skill、必要的共用規則、全域 governance 與該 project 的執行設定。charter 的操作限制由編排者傳入；不把 charter 裡的假設或 oracle 內容混進盲驗輸入。
- 編排者用平台支援的獨立 subagent／session 啟動驗證，明確關閉對話繼承。無法建立乾淨 context 就保留待驗紀錄，不得在 hunter 原 context 自稱獨立驗證。不得在缺乏工具時聲稱已操作產品。
- 發現推理或結論混入就中止本次盲驗，重新整理輸入並啟動新的乾淨 context；污染過的 context 不再交 verdict。
- verifier 的產物寫到另一個 `output/evidence/<YYYYMMDD>-<任務代號>-verifier/`，不得覆寫原包。只回報本次重現結果；跨輪合併與 calibration 回填由呼叫端或 gate 處理。

## 證據驗收

先驗 manifest、重現步驟與佐證檔是否齊全且可攜，再依 `evidence_levels` 檢查。未填時沿用 `level`；混合候選兩列都要過。hunter 與 verifier 各自留證，不能互相代替。

| 介面 | 必要證據 | Trace |
|---|---|---|
| `ui` | 關鍵操作前後截圖、console、network、實際步驟 | 依 evidence-package；要開單必須有 trace，煙霧降級不代表可開單 |
| `api` | requests.jsonl、原始回應 headers／body、包含前置的可重現請求 | 不要求瀏覽器截圖或 trace；填 `trace: null` 與 `trace_reason: API 驗證不經瀏覽器` |

verdict 的 `independent_evidence` 必須指向 verifier 本輪產物。缺證據時填 `inconclusive`；只有文字結論不得通過 gate。沒有 UI trace 的可重現觀察仍可記錄，但 gate 的 `has_evidence` 必須失敗。
