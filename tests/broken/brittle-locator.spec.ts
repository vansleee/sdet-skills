import { test, expect } from '@playwright/test'
import { gotoHome } from '../fixtures/sut'

/**
 * 教材：測試的錯（第一種）—— 脆弱選擇器。
 *
 * 這支測的東西沒有錯，錯在它怎麼找元素：
 *   - 綁 DOM 結構（nth-child、父層路徑）
 *   - 綁畫面上的排序
 *   - 綁會被翻譯的文字
 *
 * 產品只要換個排版、加一個 wrapper、改一次預設排序，它就紅。
 * 但產品本身沒有壞。這種紅燈要修的是測試，不是產品。
 *
 * 對照組：tests/e2e/cart-line-total.spec.ts 用的是 data-test，不吃這一套。
 */
test.describe('脆弱選擇器（示範用，不要照抄）', () => {
  test('第一張商品卡的價格應該大於 0', async ({ page }) => {
    await gotoHome(page)

    // 反例：綁死 DOM 路徑與排序位置
    const price = await page
      .locator('div.container div.row > div:nth-child(1) .card-body h5')
      .innerText()

    expect(Number(price.replace(/[^\d.]/g, ''))).toBeGreaterThan(0)
  })

  test('首頁應該看得到 Combination Pliers', async ({ page }) => {
    await gotoHome(page)

    // 反例：綁死顯示文字。切成德文、改商品名、換頁都會紅
    await expect(page.locator('text=Combination Pliers')).toBeVisible()
  })
})
