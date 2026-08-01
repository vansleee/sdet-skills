import { test, expect } from '@playwright/test'
import { openFirstProduct, addToCart, gotoCart, money, SUT } from '../fixtures/sut'

/**
 * 「測試的錯 vs 產品的錯」的教材主角。
 *
 *   SUT=clean      → 綠
 *   SUT=with-bugs  → 紅
 *
 * 同一份測試碼、同一台機器、同一個時間點，只換受測環境就翻紅。
 * 這是判定「產品迴歸」最乾淨的證據：測試沒改，產品改了。
 *
 * 對應的人工發現與盲驗紀錄：
 *   output/reports/issues/2026-07-30-cart-line-total-zero.md
 */
test('購物車每一列的 Total 應該等於單價乘以數量', async ({ page }) => {
  const { name, price } = await openFirstProduct(page)
  await addToCart(page)
  await gotoCart(page)

  const row = page.locator('tbody tr').filter({ hasText: name }).first()
  const qty = Number(await row.locator('[data-test="product-quantity"]').inputValue())
  const unit = money(await row.locator('[data-test="product-price"]').innerText())
  const line = money(await row.locator('[data-test="line-price"]').innerText())

  expect.soft(unit, '商品頁與購物車的單價應該一致').toBeCloseTo(price, 2)
  expect(line, `${name}：${unit} × ${qty} 應該等於列總計（SUT=${SUT}）`).toBeCloseTo(unit * qty, 2)
})

test('每一列 Total 相加，應該等於頁尾的 Total', async ({ page }) => {
  await openFirstProduct(page)
  await addToCart(page)
  await gotoCart(page)

  const lines = await page.locator('[data-test="line-price"]').allInnerTexts()
  const sum = lines.map(money).reduce((a, b) => a + b, 0)
  const total = money(await page.locator('[data-test="cart-total"]').innerText())

  expect(sum, `列總計相加 ${sum} 應該等於頁尾 ${total}（SUT=${SUT}）`).toBeCloseTo(total, 2)
})
