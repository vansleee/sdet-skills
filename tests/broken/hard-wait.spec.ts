import { test, expect } from '@playwright/test'

/**
 * 教材：測試的錯（第二種）—— 固定等待。
 *
 * waitForTimeout 是在賭網路速度。
 * 賭贏：綠，而且每一次都白等一段時間。
 * 賭輸：紅，但產品沒有壞。
 *
 * 這支刻意把等待設成 500ms，而首頁的商品清單要打一次 API 才畫得出來，
 * 實測往返約 1 秒，所以它會紅（或者偶爾僥倖過，那更糟）。
 *
 * 正解在 tests/fixtures/sut.ts：等「條件成立」，不等「時間到」。
 */
test('等 500ms 之後，首頁應該已經畫出商品', async ({ page }) => {
  await page.goto('/')

  // 反例：用時間賭渲染完成
  await page.waitForTimeout(500)

  const count = await page.locator('[data-test^="product-"]').count()
  expect(count, '等固定時間就斷言，等於在賭網路速度').toBeGreaterThan(0)
})
