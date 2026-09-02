import { ApolloProvider } from '@apollo/client'
import * as Font from 'expo-font'
import * as Notifications from 'expo-notifications'
import * as SplashScreen from 'expo-splash-screen'
import React, { useEffect, useRef, useState } from 'react'
import {
  ActivityIndicator,
  BackHandler,
  LogBox,
  Platform,
  StatusBar,
  StyleSheet,
  useColorScheme,
  View
} from 'react-native'
import FlashMessage from 'react-native-flash-message'
import i18n from './i18n'
import setupApolloClient from './src/apollo/index'
import { ConfigurationProvider } from './src/context/Configuration'
import { UserProvider } from './src/context/User'
import AppContainer from './src/routes'
import { AnimatedSplash } from './src/screens'
import { COLORS, THEME } from './src/Theme'
import { exitAlert } from './src/utils/androidBackButton'
import { requestTrackingPermissions } from './src/utils/useAppTrackingTransparency'

SplashScreen.preventAutoHideAsync().catch(() => {})

LogBox.ignoreLogs([
  'InteractionManager has been deprecated',
  'Bridgeless doesn\'t support CatalystInstance'
])

export default function App() {
  const colorScheme = useColorScheme()
  const isDark = colorScheme === 'dark'
  const [fontLoaded, setFontLoaded] = useState(false)
  const [client, setupClient] = useState(null)
  const backHandlerRef = useRef(null)

  useEffect(() => {
    requestTrackingPermissions()
  }, [])
  useEffect(() => {
    loadAppData()
    return () => {
      if (backHandlerRef.current) {
        backHandlerRef.current.remove()
      }
    }
  }, [])

  async function loadAppData() {
    const client = await setupApolloClient()

    setupClient(client)
    await i18n.initAsync()
    // load fonts
    await Font.loadAsync({
      Poppin300: require('./src/assets/font/Poppin/Poppins-Light.ttf'),
      Poppin400: require('./src/assets/font/Poppin/Poppins-Regular.ttf'),
      Poppin500: require('./src/assets/font/Poppin/Poppins-Medium.ttf'),
      Poppin600: require('./src/assets/font/Poppin/Poppins-SemiBold.ttf'),
      Poppin700: require('./src/assets/font/Poppin/Poppins-Bold.ttf'),
      icomoon: require('./src/assets/font/icomoon.ttf')
    })

    await permissionForPushNotificationsAsync()

    backHandlerRef.current = BackHandler.addEventListener(
      'hardwareBackPress',
      exitAlert
    )
    setFontLoaded(true)
  }

  async function permissionForPushNotificationsAsync() {
    const { status: existingStatus } = await Notifications.getPermissionsAsync()
    let finalStatus = existingStatus
    // only ask if permissions have not already been determined, because
    // iOS won't necessarily prompt the user a second time.
    if (existingStatus !== 'granted') {
      // Android remote notification permissions are granted during the app
      // install, so this will only ask on iOS
      const { status } = await Notifications.requestPermissionsAsync()
      finalStatus = status
    }

    // Stop here if the user did not grant permissions
    if (finalStatus !== 'granted') {
      return
    }

    if (Platform.OS === 'android') {
      Notifications.setNotificationChannelAsync('default', {
        name: 'default',
        sound: true,
        priority: 'max',
        importance: Notifications.AndroidImportance.HIGH,
        vibrate: [0, 250, 250, 250],
        lightColor: COLORS.primary
      })
    }
  }
  if (fontLoaded && client) {
    return (
      <ApolloProvider client={client}>
        <StatusBar
          translucent
          backgroundColor={'transparent'}
          barStyle={isDark ? 'light-content' : 'dark-content'}
        />
        <ConfigurationProvider>
          <UserProvider>
            <AnimatedSplash image={require('./assets/splash.png')}>
              <AppContainer />
            </AnimatedSplash>
          </UserProvider>
        </ConfigurationProvider>
        <FlashMessage duration={2000} position="center" />
      </ApolloProvider>
    )
  } else {
    return (
      <View style={[styles.flex, styles.mainContainer]}>
        <ActivityIndicator
          size="large"
          color={
            isDark
              ? THEME.Dark.colors.spinnerColor
              : THEME.Light.colors.spinnerColor
          }
        />
      </View>
    )
  }
}

const styles = StyleSheet.create({
  flex: {
    flex: 1
  },
  mainContainer: {
    justifyContent: 'center',
    alignItems: 'center'
  }
})
