const fs = require('fs')
const path = require('path')

// Minimal `.env` loader so app.config.js has no runtime dependency on dotenv.
// Values already present in the environment (CI/EAS build profiles) win.
function loadEnvFile (filePath) {
  if (!fs.existsSync(filePath)) return
  const lines = fs.readFileSync(filePath, 'utf8').split(/\r?\n/)
  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('#')) continue
    const eqIndex = trimmed.indexOf('=')
    if (eqIndex === -1) continue
    const key = trimmed.slice(0, eqIndex).trim()
    let value = trimmed.slice(eqIndex + 1).trim()
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1)
    }
    if (!(key in process.env)) process.env[key] = value
  }
}

loadEnvFile(path.join(__dirname, '.env'))

module.exports = ({ config }) => {
  config.extra = {
    ...config.extra,
    GRAPHQL_URL: process.env.GRAPHQL_URL,
    WS_GRAPHQL_URL: process.env.WS_GRAPHQL_URL,
    SERVER_URL: process.env.SERVER_URL,
    EXPO_CLIENT_ID_GOOGLE: process.env.EXPO_CLIENT_ID_GOOGLE,
    IOS_CLIENT_ID_GOOGLE: process.env.IOS_CLIENT_ID_GOOGLE,
    ANDROID_CLIENT_ID_GOOGLE: process.env.ANDROID_CLIENT_ID_GOOGLE,
    AMPLITUDE_API_KEY: process.env.AMPLITUDE_API_KEY,
    STRIPE_PUBLIC_KEY: process.env.STRIPE_PUBLIC_KEY,
    STRIPE_IMAGE_URL: process.env.STRIPE_IMAGE_URL,
    STRIPE_STORE_NAME: process.env.STRIPE_STORE_NAME
  }

  // Account-specific values are sourced from the environment (set per EAS
  // build profile) so no owner id, EAS project id, or updates URL is
  // hardcoded in the repo.
  if (process.env.EAS_PROJECT_ID) {
    config.extra.eas = { projectId: process.env.EAS_PROJECT_ID }
  }
  if (process.env.EXPO_OWNER) {
    config.owner = process.env.EXPO_OWNER
  }
  if (process.env.EXPO_UPDATES_URL) {
    config.updates = {
      ...(config.updates || {}),
      url: process.env.EXPO_UPDATES_URL
    }
  }

  // Reference the Android Google services file only when it is present so
  // builds without it (CI/local) still work; the file itself is git-ignored.
  const googleServicesFile = './google-services-prod.json'
  if (fs.existsSync(path.join(__dirname, googleServicesFile))) {
    config.android = config.android || {}
    config.android.googleServicesFile = googleServicesFile
  }

  return config
}
