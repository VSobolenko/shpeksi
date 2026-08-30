import Constants from 'expo-constants'

// Values are injected at config time (see app.config.js) into `extra` and
// read back here so no secret is hardcoded in source.
const getEnvVars = () => {
  const extra = Constants.manifest?.extra ?? Constants.expoConfig?.extra ?? {}
  return {
    GRAPHQL_URL: extra.GRAPHQL_URL,
    WS_GRAPHQL_URL: extra.WS_GRAPHQL_URL,
    SERVER_URL: extra.SERVER_URL,
    EXPO_CLIENT_ID_GOOGLE: extra.EXPO_CLIENT_ID_GOOGLE,
    IOS_CLIENT_ID_GOOGLE: extra.IOS_CLIENT_ID_GOOGLE,
    ANDROID_CLIENT_ID_GOOGLE: extra.ANDROID_CLIENT_ID_GOOGLE,
    AMPLITUDE_API_KEY: extra.AMPLITUDE_API_KEY,
    STRIPE_PUBLIC_KEY: extra.STRIPE_PUBLIC_KEY,
    STRIPE_IMAGE_URL: extra.STRIPE_IMAGE_URL,
    STRIPE_STORE_NAME: extra.STRIPE_STORE_NAME
  }
}

export default getEnvVars
