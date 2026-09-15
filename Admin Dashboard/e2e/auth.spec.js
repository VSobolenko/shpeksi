const { test, expect } = require('@playwright/test')
const {
  ADMIN_EMAIL,
  ADMIN_PASSWORD,
  trackConsoleErrors,
  expectNoUnhandledErrors,
} = require('./utils')

test.describe('Authentication flow', () => {
  test('redirects unauthenticated users to the login screen', async ({ page }) => {
    const getErrors = trackConsoleErrors(page)

    await page.goto('/#/admin/dashboard')
    await page.waitForURL('**/#/auth/login')

    await expect(page.getByText('Sign in credentials')).toBeVisible()
    await expect(page.getByPlaceholder('Email')).toBeVisible()
    await expect(page.getByPlaceholder('Password')).toBeVisible()

    expectNoUnhandledErrors(getErrors())
  })

  test('logs in and logs out', async ({ page }) => {
    const getErrors = trackConsoleErrors(page)

    // Login via the real UI form.
    await page.goto('/#/auth/login')
    await page.fill('input[placeholder="Email"]', ADMIN_EMAIL)
    await page.fill('input[placeholder="Password"]', ADMIN_PASSWORD)
    await page.getByRole('button', { name: 'Sign in' }).click()

    // After login the app stores the token and lands on the dashboard.
    await page.waitForURL('**/#/admin/dashboard')
    await expect(page.getByText(/Total Orders/)).toBeVisible()
    const stored = await page.evaluate(() => localStorage.getItem('user-forkly'))
    expect(stored, 'token should be persisted after login').toBeTruthy()

    // Logout via the navbar user dropdown (toggle is the avatar link).
    await page.locator('#navbar-main a[aria-haspopup="true"]').click()
    await page.locator('#navbar-main .dropdown-item', { hasText: 'Logout' }).click()
    await page.waitForURL('**/#/auth/login')
    await expect(page.getByText('Sign in credentials')).toBeVisible()
    const cleared = await page.evaluate(() => localStorage.getItem('user-forkly'))
    expect(cleared, 'token should be cleared after logout').toBeNull()

    expectNoUnhandledErrors(getErrors())
  })
})
