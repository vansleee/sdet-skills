import type { Page } from '@playwright/test'

export const SUT = process.env.SUT ?? 'clean'
export const isWithBugs = SUT === 'with-bugs'

/**
 * 兩個環境的路由方式不同：
 *   clean      走一般路徑  /checkout
 *   with-bugs  走 hash 路由 /#/checkout
 * 測試碼不該知道這件事，所以包成一個函式。
 */
export function path(p: string): string {
  return isWithBugs ? `/#${p}` : p
}

export async function gotoHome(page: Page) {
  await page.goto('/')
  await page.waitForSelector('[data-test^="product-"]')
}

export async function gotoCart(page: Page) {
  await page.goto(path('/checkout'))
  await page.waitForSelector('[data-test="cart-total"]')
}

/** 點進第一項商品，回傳它的名稱與單價（單價取自商品頁，是這一輪的事實來源）。 */
export async function openFirstProduct(page: Page) {
  await gotoHome(page)
  await page.locator('[data-test^="product-"]').first().click()
  await page.waitForSelector('[data-test="add-to-cart"]')
  const name = (await page.locator('[data-test="product-name"]').innerText()).trim()
  const price = Number((await page.locator('[data-test="unit-price"]').innerText()).replace(/[^\d.]/g, ''))
  return { name, price }
}

export async function addToCart(page: Page) {
  await page.click('[data-test="add-to-cart"]')
  // 加入購物車會跳一個 toast，等它出現才算真的加進去了
  await page.waitForSelector('[data-test="cart-quantity"]', { timeout: 15_000 }).catch(() => {})
}

export const money = (s: string) => Number(s.replace(/[^\d.]/g, ''))
