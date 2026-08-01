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

/**
 * 從畫面點進購物車，不要用 page.goto 直達 /checkout。
 *
 * 為什麼：直接導向深層路由會觸發受測站的 bot 防護（Cloudflare 驗證頁），
 * 在 GitHub Actions 上穩定重現，本機住宅 IP 不會。證據見
 * output/sessions/2026-08-02_ci-e2e-first-run/failure-analysis.yaml。
 * 一般使用者不會把 /checkout 貼進網址列，測試也不該。
 */
export async function gotoCart(page: Page) {
  await page.click('[data-test="nav-cart"]')
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
  // 等導覽列的數量徽章出現，才算真的加進去了。
  // 這裡不准吞例外：加不進去就該當場紅，而不是拖到下一步變成看不懂的逾時。
  await page.waitForSelector('[data-test="cart-quantity"]', { timeout: 20_000 })
}

export const money = (s: string) => Number(s.replace(/[^\d.]/g, ''))
