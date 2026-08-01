import { test, expect } from '@playwright/test'

/**
 * 教材：真正的 flaky —— 競態。
 *
 * 跟 broken/hard-wait 的差別很重要：
 *   hard-wait   幾乎每次都紅，那不是 flaky，是「穩定壞掉」。
 *   render-race 有時綠有時紅，重現率取決於當下的 API 延遲。
 *
 * flaky-detect 要做的就是把「有時候」變成一個數字：
 * 同一份程式碼、同一個環境，連續跑 N 次，紅了幾次。
 *
 * 跑法：
 *   npx playwright test tests/flaky --repeat-each=20
 */
test('搜尋結果應該在送出後立刻可讀', async ({ page }) => {
  await page.goto('/')
  await page.waitForSelector('[data-test^="product-"]')

  await page.fill('[data-test="search-query"]', 'pliers')
  await page.click('[data-test="search-submit"]')

  // 競態點：送出之後沒有等結果回來，直接讀畫面。
  // API 快的時候讀得到新結果，慢的時候讀到的還是舊清單或空清單。
  const names = await page.locator('[data-test="product-name"]').allInnerTexts()

  expect(names.length, '搜尋結果不該是空的').toBeGreaterThan(0)
  expect(
    names.every(n => /pliers/i.test(n)),
    `搜尋 pliers 卻拿到：${names.join(', ')}`,
  ).toBe(true)
})
