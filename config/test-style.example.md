# 測試碼風格（範本 — 複製成 test-style.md 後填寫；真檔已 gitignore）

`test-author`、`api-test-author`、`test-heal` 動筆前讀這份。沒有這份檔就沿用
`references/test-design.md` 的預設，不要自己猜一套。

**這裡只放需要判斷的規則。** 縮排、引號、分號、import 順序、尾逗號交給 eslint／prettier，
寫進受測 repo 的 pre-commit —— 確定性的事情不要花 token 叫模型記。

## 結構

- Page Object：<用 / 不用>；放在 <path>（不用就寫「不用，直接在 spec 裡操作」）
- fixture 放在 <path>，命名 <規則>
- 一個檔案幾支測試：<上限或原則>
- `describe` 怎麼分：<依功能 / 依頁面 / 不分>
- 共用操作放哪：<helper 路徑>（不要散在各 spec 裡複製）

## 選擇器

- 測試專屬屬性名稱：<data-test / data-testid / …>（要與 Playwright config 的 `testIdAttribute` 一致）
- 優先序：<測試專屬屬性 ＞ role ＞ 可見文字>（照抄 `references/test-design.md` 就寫「同預設」）
- 禁用：<xpath / nth-child / 綁 CSS class / 自動產生的 ID>
- 導頁方式：<用畫面點擊 / 允許 page.goto 直達深層路由>
  （受測站有 bot 防護時，直達深層路由會被擋 —— 這不是假設，見
  `output/sessions/2026-08-02_ci-e2e-first-run/failure-analysis.yaml`）

## 斷言

- 一律 web-first assertion：<是 / 否>
- `waitForTimeout`：<禁用 / 例外情況>
- 每個斷言要不要帶訊息：<要 / 不要>；訊息語言 <中文 / 英文>
- 金額、日期這類的比對精度：<toBeCloseTo(2) / 字串完全相等 / …>

## 命名

- test 標題語言：<中文 / 英文>
- test 標題寫法：<使用者看到什麼 / given-when-then / …>
- 檔名規則：<kebab-case.spec.ts / …>
- 測試目錄怎麼分：<e2e / api / smoke，各自路徑>

## 測資

- 測試自備自清：<是 / 否>；建立方式 <走 API / UI / seed script>
- 唯一標記規則：<前綴 + 時間戳 / uuid / …>（防併行撞資料）
- 允許共用的既有帳號：<有哪些 / 一律自建>

## 語言與工具

- TypeScript：<strict / 寬鬆>；`any` <禁用 / 允許>
- 匯出方式：<named / default>
- 註解語言：<中文 / 英文>
- linter／formatter：<eslint config 路徑 / prettier config 路徑 / 無>

## 這個專案的例外

<有哪些規則因為現況暫時不遵守，為什麼，什麼時候要收掉。沒有就寫「無」。>
