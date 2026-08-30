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

  const mapsKey = process.env.GOOGLE_MAPS_API_KEY
  if (mapsKey) {
    config.ios = config.ios || {}
    config.ios.config = config.ios.config || {}
    config.ios.config.googleMapsApiKey = mapsKey
    config.android = config.android || {}
    config.android.config = config.android.config || {}
    config.android.config.googleMaps = config.android.config.googleMaps || {}
    config.android.config.googleMaps.apiKey = mapsKey
  }

  return config
}
