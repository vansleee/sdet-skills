import { defineConfig, devices } from '@playwright/test'

/**
 * 受測環境切換：
 *   SUT=clean      → https://practicesoftwaretesting.com          （沒有植入 bug）
 *   SUT=with-bugs  → https://with-bugs.practicesoftwaretesting.com（植入 bug）
 * 同一份測試碼跑兩個環境，是「測試的錯 vs 產品的錯」那一課的核心手法。
 */
const SUT = process.env.SUT ?? 'clean'
const BASE_URL =
  SUT === 'with-bugs'
    ? 'https://with-bugs.practicesoftwaretesting.com'
    : 'https://practicesoftwaretesting.com'

export default defineConfig({
  // 這份 config 放在 tests/ 底下，所以相對路徑都以 tests/ 為基準
  testDir: '.',
  // 教材用途：本機不重試，才看得到真實的 flaky 率。CI 也不重試，理由見 tests/README.md。
  retries: 0,
  fullyParallel: true,
  workers: process.env.CI ? 2 : 4,
  timeout: 60_000,
  expect: { timeout: 10_000 },

  // 所有執行期產物集中在 repo 根的 output/（見 CLAUDE.md）
  outputDir: '../output/runs/playwright-artifacts',
  reporter: [
    ['list'],
    ['html', { outputFolder: '../output/reports/playwright', open: 'never' }],
    ['json', { outputFile: '../output/runs/playwright-results.json' }],
  ],

  use: {
    baseURL: BASE_URL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
  },

  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
})

export { SUT, BASE_URL }
