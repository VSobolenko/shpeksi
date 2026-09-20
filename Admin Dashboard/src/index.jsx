/* eslint-disable camelcase */
import React from 'react'
import { createRoot } from 'react-dom/client'
import {
  ApolloClient,
  InMemoryCache,
  ApolloLink,
  split,
  concat,
  Observable,
  ApolloProvider,
  HttpLink,
  gql
} from '@apollo/client'
import { WebSocketLink } from '@apollo/client/link/ws'
import { getMainDefinition } from '@apollo/client/utilities'
import { initializeApp } from 'firebase/app'
import { getMessaging, getToken, onMessage } from 'firebase/messaging'
import 'assets/vendor/nucleo/css/nucleo.css'
import 'assets/vendor/@fortawesome/fontawesome-free/css/all.min.css'
import 'assets/scss/argon-dashboard-react.scss'
import { getOrders, uploadToken } from './apollo/server'

import { ws_server_url, server_url } from './config/config'
import App from './app.jsx'
const GET_ORDERS = gql`
  ${getOrders}
`
const UPLOAD_TOKEN = gql`
  ${uploadToken}
`

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  databaseURL: import.meta.env.VITE_FIREBASE_DATABASE_URL,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
}

const cache = new InMemoryCache()
const httpLink = new HttpLink({
  uri: `${server_url}graphql`
})
const wsLink = new WebSocketLink({
  uri: `${ws_server_url}graphql`,
  options: {
    reconnect: true
  }
})

const request = async operation => {
  const data = localStorage.getItem('user-pikupo')
  let token = null
  if (data) {
    token = JSON.parse(data).token
  }
  operation.setContext({
    headers: {
      authorization: token ? `Bearer ${token}` : ''
    }
  })
}

const requestLink = new ApolloLink(
  (operation, forward) =>
    new Observable(observer => {
      let handle
      Promise.resolve(operation)
        .then(oper => request(oper))
        .then(() => {
          handle = forward(operation).subscribe({
            next: observer.next.bind(observer),
            error: observer.error.bind(observer),
            complete: observer.complete.bind(observer)
          })
        })
        .catch(observer.error.bind(observer))

      return () => {
        if (handle) handle.unsubscribe()
      }
    })
)

const terminatingLink = split(
  ({ query }) => {
    const { kind, operation } = getMainDefinition(query)
    return kind === 'OperationDefinition' && operation === 'subscription'
  },
  wsLink
)

const client = new ApolloClient({
  link: concat(ApolloLink.from([terminatingLink, requestLink]), httpLink),
  cache
})

// Initialize Firebase only when a real API key is provided (push notifications
// are optional; the admin panel still works without Firebase config).
const firebaseApiKey = import.meta.env.VITE_FIREBASE_API_KEY

if (firebaseApiKey) {
  const firebaseApp = initializeApp(firebaseConfig)
  const messaging = getMessaging(firebaseApp)

  const registerPushToken = async () => {
    try {
      const currentToken = await getToken(messaging, {
        vapidKey: import.meta.env.VITE_FIREBASE_VAPID_KEY
      })
      if (currentToken) {
        client
          .mutate({
            mutation: UPLOAD_TOKEN,
            variables: { pushToken: currentToken }
          })
          .catch(() => {})
      }
    } catch (e) {}
  }
  registerPushToken()

  onMessage(messaging, function (payload) {
    var notificationTitle = 'New Order on Pikupo'
    var notificationOptions = {
      body: payload.data.orderid,
      icon: '/favicon.png'
    }
    const nt = new Notification(notificationTitle, notificationOptions)
    nt.onclick = function (event) {
      event.preventDefault()
      window.open('/')
      nt.close()
    }
    client.query({ query: GET_ORDERS, fetchPolicy: 'network-only' })
  })
}

const container = document.getElementById('root')
const root = createRoot(container)
root.render(
  <ApolloProvider client={client}>
    <App />
  </ApolloProvider>
)
