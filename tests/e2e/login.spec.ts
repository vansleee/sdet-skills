import { test, expect } from '@playwright/test'
import { path } from '../fixtures/sut'

/**
 * 第一支自動化測試（test-author）。
 * 這支的功能是當「對照組」：它應該在兩個環境都穩定綠。
 * 之後任何一批紅燈裡，如果連它也紅了，代表問題不在個別測試，而在環境或整站。
 */

const USER = process.env.TOOLSHOP_TEST_USER
const PASS = process.env.TOOLSHOP_TEST_PASS

test.describe('登入', () => {
  test('用正確帳密登入後，會離開登入頁', async ({ page }) => {
    test.skip(!USER || !PASS, '未設定 TOOLSHOP_TEST_USER / TOOLSHOP_TEST_PASS')

    await page.goto(path('/auth/login'))
    await page.fill('[data-test="email"]', USER!)
    await page.fill('[data-test="password"]', PASS!)
    await page.click('[data-test="login-submit"]')

    // 判準：登入成功會導離登入頁，而不是「有沒有看到某個字串」
    await expect(page).not.toHaveURL(/login/, { timeout: 20_000 })
  })

  test('用錯誤密碼登入，會留在登入頁並顯示錯誤', async ({ page }) => {
    await page.goto(path('/auth/login'))
    await page.fill('[data-test="email"]', 'customer@practicesoftwaretesting.com')
    await page.fill('[data-test="password"]', 'definitely-wrong-password')
    await page.click('[data-test="login-submit"]')

    await expect(page).toHaveURL(/login/)
    await expect(page.locator('[data-test="login-error"]')).toBeVisible()
  })
})
