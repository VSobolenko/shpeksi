const { test } = require('@playwright/test')
const {
  authenticate,
  trackConsoleErrors,
  expectNoUnhandledErrors,
  waitForScreenLoaded,
} = require('./utils')

// Every admin sidebar tab, with a marker string that is unique to the screen's
// *content* (not the navbar title, which repeats the tab name). The marker only
// renders once the screen's GraphQL query has resolved without error, so its
// presence proves the screen rendered with data (not blank / error / spinner).
const SCREENS = [
  { name: 'Dashboard', path: '/admin/dashboard', marker: 'Total Orders' },
  { name: 'Category', path: '/admin/category', marker: 'Add Category' },
  { name: 'Food', path: '/admin/food', marker: 'Add Food' },
  { name: 'Addons', path: '/admin/addons', marker: 'Addons' },
  { name: 'Option', path: '/admin/option', marker: 'Option' },
  { name: 'Coupons', path: '/admin/coupons', marker: 'Add Coupon' },
  { name: 'Orders', path: '/admin/orders', marker: 'Orders' },
  { name: 'Users', path: '/admin/users', marker: 'Users' },
  { name: 'Ratings', path: '/admin/ratings', marker: 'Ratings' },
  { name: 'Configuration', path: '/admin/configuration', marker: 'OrderID prefix' },
  { name: 'Notifications', path: '/admin/notifications', marker: 'Send' },
]

async function waitForDashboardLoaded (page) {
  await page.getByText(/Total Orders/).first().waitFor({ timeout: 25_000 })
  // The stat cards render '...' while loading; wait until every card holds a
  // real value (proves getDashboardTotal resolved).
  await page.waitForFunction(() => {
    const cards = [...document.querySelectorAll('.card-stats')]
    return cards.length >= 4 && cards.every(c => !c.textContent.includes('...'))
  }, { timeout: 25_000 })
}

async function openViaSidebar (page, screen) {
  await page.locator(`#sidenav-main a[href="#${screen.path}"]`).click()
}

for (const screen of SCREENS) {
  test(`renders and navigates: ${screen.name}`, async ({ page, request }) => {
    const getErrors = trackConsoleErrors(page)

    await authenticate(page, request)
    await page.goto('/#/admin/dashboard')
    await waitForDashboardLoaded(page)

    if (screen.name !== 'Dashboard') {
      await openViaSidebar(page, screen)
      await page.waitForURL(`**/#${screen.path}`)
      await waitForScreenLoaded(page, screen.marker)
    }

    await expectNoUnhandledErrors(getErrors())
  })
}
