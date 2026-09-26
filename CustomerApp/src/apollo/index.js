import AsyncStorage from '@react-native-async-storage/async-storage'
import {
  ApolloClient,
  InMemoryCache,
  ApolloLink,
  concat,
  Observable,
  split,
  HttpLink,
  defaultDataIdFromObject
} from '@apollo/client'
import { WebSocketLink } from '@apollo/client/link/ws'
import { getMainDefinition } from '@apollo/client/utilities'
import { persistCache } from 'apollo3-cache-persist'
import getEnvVars from '../../environment'

const { GRAPHQL_URL, WS_GRAPHQL_URL, RESTAURANT_SLUG } = getEnvVars()

const cache = new InMemoryCache({
  dataIdFromObject: object => {
    switch (object.__typename) {
      case 'CartItem':
        return object.key // use `key` as the primary key
      default:
        return defaultDataIdFromObject(object) // fall back to default handling
    }
  }
})

// The backend is multi-tenant: it resolves the restaurant from this header for
// anything not authenticated yet (catalog, login, registration). Each
// white-label APK is built with its own RESTAURANT_SLUG, so the value is baked
// into the bundle at build time.
const tenantHeaders = RESTAURANT_SLUG
  ? { 'x-restaurant-id': RESTAURANT_SLUG }
  : {}

const httpLink = new HttpLink({
  uri: GRAPHQL_URL,
  headers: tenantHeaders
})

const wsLink = new WebSocketLink({
  uri: WS_GRAPHQL_URL,
  options: {
    reconnect: true,
    // Subscriptions open their own connection, so the tenant — and the token
    // once the customer is signed in — travel in the `connection_init` payload
    // instead of headers. A function is required because when this link is
    // built the token is not known yet.
    connectionParams: async () => {
      const token = await AsyncStorage.getItem('token')
      return {
        ...tenantHeaders,
        authorization: token ? `Bearer ${token}` : ''
      }
    }
  }
})

const request = async operation => {
  const token = await AsyncStorage.getItem('token')
  operation.setContext({
    // get the authentication token from local storage if it exists
    // return the headers to the context so httpLink can read them
    headers: {
      ...tenantHeaders,
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

const setupApollo = async () => {
  await persistCache({
    cache,
    storage: AsyncStorage
  })
  const client = new ApolloClient({
    link: concat(ApolloLink.from([terminatingLink, requestLink]), httpLink),
    cache
  })

  return client
}

export default setupApollo
