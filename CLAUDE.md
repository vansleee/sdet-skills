# sdet-skills — 專案規則

Agentic SDET 技能組：GitHub Actions · Playwright (TypeScript) · GitHub Issues。
一套可重用的 skill，讓 agent 探索找 bug、驗證回報、修產品、顧測試與整條 CI 生產線。

**架構、bucket 分層、心智模型的完整說明在 `architecture/sdet-skills-architecture.md`，這份只寫動手時要遵守的規則。**

## 鐵則
- **產品知識與專案設定是「輸入」，skill 讀它、不內嵌**，否則 reuse 就死了。四層分工（`skills/` 能力、`knowledge/` 事實、`skills/workflow/` 流程、`config/` 設定）見架構文件的「心智模型」。
- **新增 skill 的門檻：手段不同才開新的，判準不同只加一張表。** 依據見架構文件的「介面層：畫面與端點」。不准為 API 另立一套平行體系。
- **一筆 vs 一批不要混。** `maintain/` 一支測試、`infra/` 一整批；一批必須先 fan-in 合併根因再分析。對照表見架構文件的「一筆 vs 一批」。

## 每支 skill 的規範
- 一定要有 `SKILL.md` 與 `agents/openai.yaml`。
- 宣告 invocation：user-invoked（`disable-model-invocation: true` + openai.yaml `policy.allow_implicit_invocation: false`）或 model-invoked（兩者都省略）。
- 後端相依（GitHub / 網址 / 帳密）不寫死在 SKILL.md，放 `config/`；產品知識放 `knowledge/`；祕密只用環境變數。
- SKILL.md 保持短（祈使句），rationale 放 `docs/`。
- 副作用動作（開 issue/PR、改測試、reset env、release 放行）一律先確認，並受 `config/governance.yaml` 授權分級管制。
- skill 之間用「skill 名稱」互相指涉（如「交給 test-oracle」），不要用外部章節/週次。
- 新增/改名/改行為的 skill，要同步更新 `README.md`、`.claude-plugin/plugin.json`、`meta/ask-sdet`。
- 中文行文照 de-ai-tone：標點全形、破折號只當插入語、不用中國用語與空轉話語標記。CI 跑 `scripts/check-de-ai-tone.py` 擋，本機可先跑一次。

## 產品知識與設定
- `knowledge/`、`config/` 的真檔一律 gitignore，**只 commit 範本**（`*.example.md`、`*.example.yaml`）。`knowledge/` 依規模分層的做法見架構文件的「`knowledge/`」。
- `config/test-style.md` — 這個專案的測試碼風格，由 `setup-sdet` 訪談產出，`test-author` / `api-test-author` / `test-heal` 動筆前讀它。**只收需要判斷的規則**（Page Object、選擇器優先序、導頁方式、斷言與命名慣例）；縮排、引號、import 順序交 eslint／prettier。風格是設定不是能力，不准為它另開 skill。

## 執行期產物
- **除了 `charters/` 與 `tests/` 之外，所有執行期產物一律寫在 `output/` 底下。** 不准在 repo 根目錄留 `findings/`、`evidence/`、截圖或 JSON。
- 單輪產物進 `output/sessions/<date>_<slug>/`，跨輪累積的登錄簿留 `output/` 根，證據走 `output/evidence/<YYYYMMDD>-<slug>/`。**切進單輪就失去去重與校準的能力。**
- 完整檔案清單與欄位規範見 `docs/state-files.md`；不可以自創狀態詞彙。

## 測試碼（`tests/`）
- **跟測試有關的檔案全部放 `tests/` 底下，一律 `.ts`**，包含 `playwright.config.ts`（不放 repo 根）與過程中寫的臨時探測腳本（放 `tests/tools/`，用完刪掉）。repo 根目錄不准留 `.mjs`、`probe*`、一次性腳本。
- 目錄語意固定：`e2e/` 正常測試、`broken/` 穩定紅的反例、`flaky/` 時紅時綠、`fixtures/` 共用操作、`tools/` 非測試工具。`broken/` 與 `flaky/` 是 `maintain/` 的實測基準，**穩定壞掉不是 flaky**，兩者不准混。
- 受測環境用 `SUT` 環境變數切換（`clean` / `with-bugs`）。**同一份測試碼跑兩個環境**是判「測試的錯 vs 產品的錯」的手段，不要為單一環境寫死。
- `retries: 0`。重試會蓋掉 flaky，而這裡就是要看見它。
- 寫測試前先跑 `tests/tools/probe-selectors.ts` 探 `data-test`，不要用猜的。
- 產物（report、trace、screenshot）寫到 repo 根的 `output/`，不留在 `tests/`。
- 這批測試各自演什麼、實測數字多少，見 `tests/README.md`。
