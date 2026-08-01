/**
 * 探選擇器用的一次性工具，不是測試。
 * 寫測試之前先跑它，把頁面上有哪些 data-test 印出來，避免用猜的。
 *
 *   npx tsx tests/tools/probe-selectors.ts
 *   npx tsx tests/tools/probe-selectors.ts https://with-bugs.practicesoftwaretesting.com
 */
import { chromium } from '@playwright/test'

const BASE = process.argv[2] ?? 'https://practicesoftwaretesting.com'
const isWithBugs = BASE.includes('with-bugs')
const noise = /^(nav-|lang-|category-|language|notification)/

async function main() {
  const browser = await chromium.launch()
  const page = await browser.newPage()

  const dump = async (label: string) => {
    const ids = await page.$$eval('[data-test]', els =>
      [...new Set(els.map(e => e.getAttribute('data-test') ?? ''))],
    )
    console.log(`\n--- ${label} (${page.url()}) ---`)
    console.log(ids.filter(x => x && !noise.test(x)).join(' | '))
  }

  await page.goto(BASE)
  await page.waitForSelector('[data-test^="product-"]', { timeout: 30_000 })
  await dump('home')

  await page.locator('[data-test^="product-"]').first().click()
  await page.waitForSelector('[data-test="add-to-cart"]', { timeout: 30_000 })
  await dump('product detail')

  await page.click('[data-test="add-to-cart"]')
  await page.waitForTimeout(2_000)

  await page.goto(`${BASE}${isWithBugs ? '/#' : ''}/checkout`)
  await page.waitForSelector('[data-test="cart-total"]', { timeout: 30_000 })
  await dump('cart')
  console.log('\n--- cart table ---')
  console.log(await page.locator('table').first().innerText())

  await browser.close()
}

main().catch(err => {
  console.error(err)
  process.exit(1)
})
