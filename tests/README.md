# tests/ — maintain/ 這一層的教材與實測基準

這個目錄不是產品的測試套件，是 `maintain/` 那批 skill（`test-author`、`failure-analysis`、
`flaky-detect`、`test-heal`、`re-run-gate`、`test-prune`）的**實測基準**。

每一支測試都對應一種「紅燈的成因」，而且都經過實跑驗證，不是寫給人看的示意。

## 受測產品

Toolshop（practicesoftwaretesting.com），同一套程式碼有兩個環境：

| `SUT` | 網址 | 說明 |
| --- | --- | --- |
| `clean`（預設） | `https://practicesoftwaretesting.com` | 沒有植入 bug |
| `with-bugs` | `https://with-bugs.practicesoftwaretesting.com` | 植入 bug |

兩邊的 `data-test` 屬性一致，差別在路由（`clean` 走一般路徑，`with-bugs` 走 hash 路由），
這件事包在 `fixtures/sut.ts` 裡，測試碼看不到。

**同一份測試碼跑兩個環境，是「測試的錯 vs 產品的錯」最乾淨的證明手法。**
測試沒改、機器沒換、時間點相同，只換環境就翻紅 —— 那就不是測試的問題。

## 四類測試

| 目錄 | 應有狀態 | 演什麼 |
| --- | --- | --- |
| `e2e/login.spec.ts` | 兩個環境都綠 | 對照組。連它都紅，代表問題在環境或整站，不在個別測試 |
| `e2e/cart-line-total.spec.ts` | `clean` 綠、`with-bugs` 紅 | **產品的錯**（產品迴歸） |
| `broken/` | 穩定紅 | **測試的錯**（脆弱選擇器、固定等待） |
| `flaky/` | 時紅時綠 | **flaky**（競態） |

`broken/` 與 `flaky/` 的差別是刻意的：**穩定壞掉不是 flaky**。
兩者都紅，但處置完全不同 —— 前者修測試，後者要先量重現率再決定隔離或修。

## 實測數字

以下都是實跑結果，不是預期值。

### e2e（2026-08-02）

```
SUT=clean        4 passed
SUT=with-bugs    2 passed, 2 failed
```

紅的訊息：

```
Error: 列總計相加 0 應該等於頁尾 14.15（SUT=with-bugs）
Expected: 14.15
Received: 0
```

對應的人工發現與盲驗紀錄在 `output/reports/issues/2026-07-30-cart-line-total-zero.md`。

### CI（GitHub Actions，2026-08-02）

Workflow：`.github/workflows/e2e.yml`，matrix 同時跑兩個環境。

| run | `e2e (clean)` | `e2e (with-bugs)` |
| --- | --- | --- |
| `30710272941` | ✗ 紅 | ✗ 紅 |
| `30710272941`（rerun --failed） | ✗ 紅 | ✗ 紅 |
| `30710677728` | ✓ 3 passed | ✗ 紅 |
| `30710750654` | ✓ | — |
| `30710799963` | ✓ | — |

`with-bugs` 一路紅是設計，它紅在斷言（`Received: 0`），不是紅在別的地方。
`clean` 前兩次紅**不是**設計，那是真的踩到坑，過程見下面一節。

CI 上 `login.spec.ts` 的成功登入那支會 skip，因為 repo 沒設
`TOOLSHOP_TEST_USER` / `TOOLSHOP_TEST_PASS` secrets，所以 `clean` 是 3 passed 不是 4。

### `clean` 那兩次紅是怎麼回事（Day 35–36 的完整案例）

這一段是實際發生的過程，不是編的教案。

1. **看 traceback 就下結論。** 錯誤停在 `gotoCart` 的 `waitForSelector`，
   我認定是 `addToCart` 把等待失敗 `.catch` 吞掉、購物車根本是空的。**猜錯了。**
2. **拉 evidence。** `error-context.md` 的 page snapshot 顯示畫面根本不是應用程式，
   而是 Cloudflare 的 `Performing security verification`。判 `environment`。
3. **重跑確認。** `gh run rerun --failed` 症狀一模一樣，不是間歇。
4. **比對同一個 job 內部。** `gotoHome`、商品頁、`login.spec` 都在同一個 runner、
   同一個出口 IP、同一分鐘內成功載入，只有 `gotoCart` 的
   `page.goto('/checkout')` 被擋。**所以基礎設施沒壞、產品沒壞。**
   第 2 步的分類是錯的，這是 test-defect。
5. **修。** `gotoCart` 改成點 `[data-test="nav-cart"]`；
   順手把 `addToCart` 的 `.catch(() => {})` 拿掉 ——
   吞例外把「東西沒加進去」變成兩步之後看不懂的逾時，正是它害第 1 步猜錯方向。
6. **驗穩。** 連續 3 次 CI 全綠才算過，1 次不算。

兩個要點：

- **「紅了先別修」不是格言。** 這裡判錯兩次，兩次都是證據把方向拉回來的。
- **測試抄捷徑會被當成機器人。** 使用者不會把 `/checkout` 貼進網址列，
  測試也不該。這條後來寫進 `config/test-style.example.md` 的「導頁方式」。

完整紀錄：`output/sessions/2026-08-02_ci-e2e-first-run/`
（`failure-analysis.yaml` 含被推翻的初判與 revision、`runs/reruns-2026-08-02.yaml` 含裁決）。

### broken（2026-08-02，連跑三次）

```
run 1  3 failed
run 2  3 failed
run 3  3 failed
```

穩定紅。附帶一提，這個檔案第一版有一支綁死顯示文字的測試，
它自己就會飄（第一次紅、第二次綠）—— 示範用的壞測試自己也是 flaky，
可見 flaky 有多容易不小心種進去。已換成綁死不存在的 CSS class，改成確定性失敗。

### flaky（2026-08-02，每格 20 次，workers=4）

```
FLAKY_WAIT_MS   紅 / 20        判定
─────────────   ──────────     ────────────────────
       700       20            穩定壞掉（等待永遠不夠）
      1000       20            穩定壞掉
      1200       18            幾乎穩定壞掉
      1300       18            幾乎穩定壞掉
      1350       7 / 12        flaky ← 預設值
      1400       2 / 5         flaky
```

兩個要點：

1. **700ms 和 1350ms 是同一個根因（固定等待），症狀完全不同。**
   一個穩定紅、一個時紅時綠。根因相同不代表處置相同。
2. **同一個等待值量兩次，結果差 25 個百分點。**
   1350ms 量到 35% 和 60%，1400ms 量到 10% 和 25%。
   flaky 率不是常數，是帶誤差的估計值。所以要問的不是「它 flaky 嗎」，
   是「跑 N 次紅幾次，這個 N 夠不夠大」。

## 怎麼跑

```bash
npm install
npx playwright install chromium

npm run test:clean        # 應該全綠
npm run test:with-bugs    # cart 兩支應該紅
npm run test:flaky        # 跑 20 次，看紅幾次

# 單獨跑某一類
npx playwright test --config tests/playwright.config.ts tests/broken
```

登入測試需要環境變數，沒設就自動 skip（祕密不落地，見 `setup-sdet`）：

```bash
export TOOLSHOP_TEST_USER=customer@practicesoftwaretesting.com
export TOOLSHOP_TEST_PASS=...
```

## 幾個刻意的設定

- **`retries: 0`。** 重試會把 flaky 蓋掉，而這裡就是要看見它。
  正式產品線要不要開重試是另一個題目，判準交給 `re-run-gate`。
- **`trace` / `screenshot` / `video` 只在失敗時保留。** 綠燈不留證，省時間也省空間。
- **產物寫到 repo 根的 `output/`**，不留在 `tests/`（見 `CLAUDE.md`）。
- **`tools/probe-selectors.ts` 不是測試**，是寫測試前先探 `data-test` 用的。
  先探再寫，不要用猜的。

## 目錄

```
tests/
  playwright.config.ts       SUT 環境切換、retries 0、產物路徑
  fixtures/sut.ts            兩環境的路由差異、共用操作
  e2e/                       正常的測試
  broken/                    測試的錯（穩定紅）
  flaky/                     flaky（時紅時綠）
  tools/                     探選擇器的一次性工具
```
