// @ts-check
const { defineConfig } = require('@playwright/test')

// End-to-end suite for the Admin Dashboard (React + Vite on :3006) against the
// live FastAPI/Strawberry GraphQL backend (Caddy on :80).
//
// Uses the system-installed Chrome (`channel: 'chrome'`) so no browser download
// is required on Windows dev machines. For a CI runner, either install Chrome
// or run `npx playwright install chromium` and remove `channel` below.
module.exports = defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  timeout: 60_000,
  expect: { timeout: 15_000 },
  retries: process.env.CI ? 1 : 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://localhost:3006',
    channel: 'chrome',
    headless: true,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3006',
    reuseExistingServer: true,
    timeout: 120_000,
  },
  projects: [{ name: 'chromium' }],
})
