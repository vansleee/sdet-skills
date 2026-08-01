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
 *   npm run test:flaky          # --repeat-each=20
 *
 * 等待值掃過一輪的實測（2026-08-02，每格 20 次，workers=4）：
 *
 *   FLAKY_WAIT_MS   紅 / 20    判定
 *   ─────────────   ────────   ────────────────────────
 *          700       20        穩定壞掉（等待永遠不夠）
 *         1000       20        穩定壞掉
 *         1200       18        幾乎穩定壞掉
 *         1300       18        幾乎穩定壞掉
 *         1350     7 / 12      flaky ← 預設值
 *         1400     2 / 5       flaky
 *
 * 最後兩列才是重點：同一個等待值，各量兩次。
 * 1350ms 量到 35% 和 60%，1400ms 量到 10% 和 25%。
 * flaky 率不是一個常數，是一個帶誤差的估計值 —— 所以 flaky-detect
 * 要問的不是「它 flaky 嗎」，是「跑 N 次紅幾次，這個 N 夠不夠大」。
 */
test('搜尋結果應該在送出後立刻可讀', async ({ page }) => {
  await page.goto('/')
  await page.waitForSelector('[data-test^="product-"]')

  await page.fill('[data-test="search-query"]', 'pliers')
  await page.click('[data-test="search-submit"]')

  // 競態點：等一個「通常夠、偶爾不夠」的固定時間，然後直接讀畫面。
  // 搜尋 API 的往返時間會浮動，等待值剛好卡在它的分布中間，
  // 所以這支有時候綠、有時候紅 —— 這才是 flaky。
  // 對照 broken/hard-wait.spec.ts：那支等 500ms，永遠不夠，是穩定壞掉。
  await page.waitForTimeout(Number(process.env.FLAKY_WAIT_MS ?? 1350))

  const names = await page.locator('[data-test="product-name"]').allInnerTexts()

  expect(names.length, '搜尋結果不該是空的').toBeGreaterThan(0)
  expect(
    names.every(n => /pliers/i.test(n)),
    `搜尋 pliers 卻拿到：${names.join(', ')}`,
  ).toBe(true)
})
