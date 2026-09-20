import { fileURLToPath, URL } from 'node:url'
import { writeFileSync, mkdirSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// Firebase Messaging requires a service worker at the app root scope. Vite
// copies `public/` files verbatim (no env substitution), so generate it here at
// build time and inject the (non-secret) messaging sender id from env.
function firebaseMessagingSwPlugin (senderId) {
  const swSource = `// Generated at build time by vite.config.js — do not edit directly.
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js')
importScripts(
  'https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js'
)

firebase.initializeApp({
  messagingSenderId: '${senderId}'
})

const messaging = firebase.messaging()

messaging.onBackgroundMessage(function (payload) {
  var notificationTitle = 'New Order on Pikupo'
  var notificationOptions = {
    body: payload.data.orderid,
    icon: '/favicon.png'
  }

  return self.registration.showNotification(
    notificationTitle,
    notificationOptions
  )
})
`
  return {
    name: 'firebase-messaging-sw',
    closeBundle () {
      const outFile = resolve(process.cwd(), 'dist', 'firebase-messaging-sw.js')
      mkdirSync(dirname(outFile), { recursive: true })
      writeFileSync(outFile, swSource)
    }
  }
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    plugins: [react(), firebaseMessagingSwPlugin(env.VITE_FIREBASE_MESSAGING_SENDER_ID || '')],
    resolve: {
      alias: {
        layouts: fileURLToPath(new URL('./src/layouts', import.meta.url)),
        views: fileURLToPath(new URL('./src/views', import.meta.url)),
        components: fileURLToPath(new URL('./src/components', import.meta.url)),
        assets: fileURLToPath(new URL('./src/assets', import.meta.url)),
        variables: fileURLToPath(new URL('./src/variables', import.meta.url)),
        constraints: fileURLToPath(new URL('./src/constraints', import.meta.url)),
        config: fileURLToPath(new URL('./src/config', import.meta.url)),
        apollo: fileURLToPath(new URL('./src/apollo', import.meta.url)),
        utils: fileURLToPath(new URL('./src/utils', import.meta.url)),
        translations: fileURLToPath(new URL('./src/translations', import.meta.url))
      }
    },
    server: {
      port: 3006
    }
  }
})
