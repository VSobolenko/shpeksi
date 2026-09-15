// Generated at build time by vite.config.js — do not edit directly.
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js')
importScripts(
  'https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js'
)

firebase.initializeApp({
  messagingSenderId: ''
})

const messaging = firebase.messaging()

messaging.onBackgroundMessage(function (payload) {
  var notificationTitle = 'New Order on Forkly'
  var notificationOptions = {
    body: payload.data.orderid,
    icon: '/favicon.png'
  }

  return self.registration.showNotification(
    notificationTitle,
    notificationOptions
  )
})
