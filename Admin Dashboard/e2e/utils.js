const { expect } = require('@playwright/test')

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost/graphql'
const ADMIN_EMAIL = process.env.ADMIN_EMAIL || 'admin@example.com'
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'change-me'

// React 18 logs its dev-mode deprecation warnings via console.error with a
// "Warning: " prefix. The legacy libraries pinned by this app (reactstrap v7,
// styled-components v5 via react-data-table-component, react-i18next v10) all
// trigger them (defaultProps, childContextTypes, Invalid hook call, ...).
// They are benign — rendering is unaffected — and are not unhandled errors.
// Real failures surface via pageerror (uncaught exceptions) or a non-"Warning:"
// console.error (network errors, 500s, etc.).
function isBenignConsoleError (text) {
  return /^Warning:/.test(text.trim())
}

async function getAdminToken (request) {
  const res = await request.post(BACKEND_URL, {
    data: {
      query: `mutation AdminLogin($email: String!, $password: String!) {
        adminLogin(email: $email, password: $password) { token }
      }`,
      variables: { email: ADMIN_EMAIL, password: ADMIN_PASSWORD },
    },
  })
  const json = await res.json()
  if (json.errors) {
    throw new Error('adminLogin failed: ' + JSON.stringify(json.errors))
  }
  return json.data.adminLogin.token
}

// Inject a valid admin token into localStorage (matching what the app stores
// after a real login). Keeps the per-screen tests fast and deterministic; the
// real login/logout UI flow is covered separately in auth.spec.js.
async function authenticate (page, request) {
  const token = await getAdminToken(request)
  await page.addInitScript(tokenValue => {
    localStorage.setItem(
      'user-pickup',
      JSON.stringify({ token: tokenValue })
    )
  }, token)
}

// Collect uncaught exceptions (pageerror) and unexpected console.error output
// while ignoring the documented benign styled-components warning.
function trackConsoleErrors (page) {
  const consoleErrors = []
  const pageErrors = []
  page.on('console', msg => {
    if (msg.type() === 'error' && !isBenignConsoleError(msg.text())) {
      consoleErrors.push(msg.text())
    }
  })
  page.on('pageerror', err => pageErrors.push(String(err)))
  return () => ({ consoleErrors, pageErrors })
}

function expectNoUnhandledErrors ({ consoleErrors, pageErrors }) {
  expect(pageErrors, 'uncaught JS exceptions (pageerror)').toEqual([])
  expect(consoleErrors, 'unhandled console.error messages').toEqual([])
}

// Wait for a screen's unique content marker to appear (proves it rendered, not
// a blank screen or error state) and for the react-loader-spinner TailSpin
// (viewBox "0 0 38 38") to disappear (proves data settled, not an eternal
// spinner).
async function waitForScreenLoaded (page, marker) {
  // Scope to `.card` so screen content markers never collide with the sidebar
  // links (which share the tab name, e.g. "Users"/"Ratings"/"Addons").
  await page
    .locator('.card')
    .getByText(marker, { exact: false })
    .first()
    .waitFor({ timeout: 25_000 })
  await page.waitForFunction(
    () => !document.querySelector('svg[viewBox="0 0 38 38"]'),
    { timeout: 25_000 }
  )
}

module.exports = {
  BACKEND_URL,
  ADMIN_EMAIL,
  ADMIN_PASSWORD,
  getAdminToken,
  authenticate,
  trackConsoleErrors,
  expectNoUnhandledErrors,
  waitForScreenLoaded,
}
