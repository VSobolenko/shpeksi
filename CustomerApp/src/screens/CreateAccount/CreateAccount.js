import { useMutation, gql } from '@apollo/client'
import { FontAwesome } from '@expo/vector-icons'
import { useNavigation, useTheme } from '@react-navigation/native'

import * as AppleAuthentication from 'expo-apple-authentication'

import * as Google from 'expo-auth-session/providers/google'
import React, { useContext, useEffect, useState } from 'react'
import { TouchableOpacity, View } from 'react-native'
import getEnvVars from '../../../environment'
import { login } from '../../apollo/server'
import {
  PikupoImage,
  FdEmailBtn,
  FdGoogleBtn,
  FlashMessage,
  RegistrationHeader,
  Spinner,
  TextDefault,
  WrapperView
} from '../../components'
import UserContext from '../../context/User'
import { alignment } from '../../utils/alignment'
import Analytics from '../../utils/analytics'
import { NAVIGATION_SCREEN } from '../../utils/constant'
import { getNotificationTokenSafe } from '../../utils/pushToken'
import { scale } from '../../utils/scaling'
import useStyle from './styles'
import i18n from '../../../i18n'

const {
  IOS_CLIENT_ID_GOOGLE,
  ANDROID_CLIENT_ID_GOOGLE,
  EXPO_CLIENT_ID_GOOGLE
} = getEnvVars()

const LOGIN = gql`
  ${login}
`

const Logo = require('../../../assets/logo.png')
const CreateAccount = () => {
  const styles = useStyle()
  const { colors } = useTheme()
  const navigation = useNavigation()
  const [enableApple, setEnableApple] = useState(false)
  const [loginButton, loginButtonSetter] = useState(null)
  const [loading, setLoading] = useState(false)

  const { setTokenAsync } = useContext(UserContext)

  useEffect(() => {
    checkIfSupportsAppleAuthentication()
  }, [])

  const [mutate] = useMutation(LOGIN, { onCompleted, onError })

  async function checkIfSupportsAppleAuthentication() {
    setEnableApple(await AppleAuthentication.isAvailableAsync())
  }

  async function onCompleted(data) {
    if (!data.login.is_active) {
      FlashMessage({
        message: i18n.t('cantLogin')
      })
      setLoading(false)
    } else {
      try {
        const trackingOpts = {
          id: data.login.userId,
          usernameOrEmail: data.login.email
        }
        Analytics.identify(data.login.userId, trackingOpts)
        Analytics.track(Analytics.events.USER_CREATED_ACCOUNT, trackingOpts)
        setTokenAsync(data.login.token)
        navigation.navigate(NAVIGATION_SCREEN.Menu)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
  }
  function onError(error) {
    try {
      FlashMessage({
        message: error.graphQLErrors[0].message
      })
      loginButtonSetter(null)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  async function mutateLogin(user) {
    setLoading(true)
    try {
      const notificationToken = await getNotificationTokenSafe()
      mutate({ variables: { ...user, notificationToken } })
    } catch (e) {
      console.error(e)
      setLoading(false)
    }
  }

  function renderAppleAction() {
    if (loading && loginButton === 'Apple') {
      return (
        <View style={styles.buttonBackground}>
          <Spinner backColor="rgba(0,0,0,0.1)" spinnerColor={colors.tagColor} />
        </View>
      )
    }
    return (
      <TouchableOpacity
        style={styles.appleBtn}
        onPress={async() => {
          try {
            const credential = await AppleAuthentication.signInAsync({
              requestedScopes: [
                AppleAuthentication.AppleAuthenticationScope.FULL_NAME,
                AppleAuthentication.AppleAuthenticationScope.EMAIL
              ]
            })
            if (credential) {
              const user = {
                appleId: credential.user,
                phone: '',
                email: credential.email,
                password: '',
                name:
                  credential.fullName.givenName +
                  ' ' +
                  credential.fullName.familyName,
                picture: '',
                type: 'apple'
              }
              mutateLogin(user)
            }

            loginButtonSetter('Apple')
            // signed in
          } catch (e) {
            if (e.code === 'ERR_CANCELLED') {
              // handle that the user canceled the sign-in flow
              loginButtonSetter(null)
            } else {
              // handle other errors
              loginButtonSetter(null)
            }
          }
        }}
      >
        <FontAwesome
          style={styles.marginLeft5}
          name="apple"
          size={scale(19)}
          color={colors.iconColor}
        />
        <TextDefault style={alignment.MLsmall} bold>
          {i18n.t('signupApple')}
        </TextDefault>
      </TouchableOpacity>
    )
  }

  const googleConfigured = Boolean(
    EXPO_CLIENT_ID_GOOGLE ||
      ANDROID_CLIENT_ID_GOOGLE ||
      IOS_CLIENT_ID_GOOGLE
  )

  // `useAuthRequest` throws when the client id for the *current* platform is
  // missing ("Client Id property `androidClientId` must be defined to use Google
  // auth on this platform"), and a throw inside the screen unmounts it — the
  // whole sign-in screen went blank. Every platform field therefore needs a
  // defined value; the button stays disabled while Google is unconfigured, so
  // the placeholder is never used for a real flow.
  const GOOGLE_CLIENT_ID_PLACEHOLDER = 'disabled.apps.googleusercontent.com'

  const [googleRequest, googleResponse, googlePromptAsync] =
    Google.useAuthRequest({
      expoClientId: EXPO_CLIENT_ID_GOOGLE || GOOGLE_CLIENT_ID_PLACEHOLDER,
      iosClientId: IOS_CLIENT_ID_GOOGLE || GOOGLE_CLIENT_ID_PLACEHOLDER,
      androidClientId: ANDROID_CLIENT_ID_GOOGLE || GOOGLE_CLIENT_ID_PLACEHOLDER,
      scopes: ['profile', 'email']
    })

  useEffect(() => {
    if (googleResponse?.type !== 'success') {
      if (
        googleResponse?.type === 'error' ||
        googleResponse?.type === 'dismiss'
      ) {
        loginButtonSetter(null)
        setLoading(false)
        if (googleResponse?.type === 'error') {
          FlashMessage({
            message: i18n.t('googleSignInFailed')
          })
        }
      }
      return
    }
    const { authentication } = googleResponse
    if (!authentication?.accessToken) {
      loginButtonSetter(null)
      setLoading(false)
      FlashMessage({ message: i18n.t('googleSignInFailed') })
      return
    }
    ;(async() => {
      try {
        setLoading(true)
        const userInfoResponse = await fetch(
          'https://www.googleapis.com/oauth2/v1/userinfo?alt=json',
          {
            headers: { Authorization: `Bearer ${authentication.accessToken}` }
          }
        )
        if (!userInfoResponse.ok) {
          throw new Error(`Google userinfo HTTP ${userInfoResponse.status}`)
        }
        const googleUser = await userInfoResponse.json()
        if (!googleUser?.email) {
          throw new Error('Google account email missing')
        }
        mutateLogin({
          phone: '',
          email: googleUser.email,
          password: '',
          name: googleUser.name || googleUser.email,
          picture: googleUser.picture || '',
          type: 'google'
        })
      } catch (e) {
        console.error(e)
        loginButtonSetter(null)
        setLoading(false)
        FlashMessage({ message: i18n.t('googleSignInFailed') })
      }
    })()
  }, [googleResponse])

  function renderGoogleAction() {
    const disabled = !googleConfigured || !googleRequest
    return (
      <FdGoogleBtn
        loadingIcon={loading && loginButton === 'Google'}
        disabled={disabled}
        onPressIn={() => {
          if (!disabled) loginButtonSetter('Google')
        }}
        onPress={() => {
          if (!disabled) googlePromptAsync()
        }}
      />
    )
  }
  function renderEmailAction() {
    return (
      <FdEmailBtn
        loadingIcon={loading && loginButton === 'Email'}
        onPress={() => {
          loginButtonSetter('Email')
          navigation.navigate(NAVIGATION_SCREEN.Register)
        }}
      />
    )
  }

  return (
    <WrapperView>
      <View style={[styles.mainContainer, styles.flex]}>
        <RegistrationHeader title={i18n.t('getStarted')} />
        <View style={styles.subContainer}>
          <View style={[styles.flex, styles.upperContainer]}>
            <PikupoImage
              imgStyle={styles.imgResponsive}
              imgSource={Logo}
              spinnerProps={{ style: styles.loadingView }}
            />
          </View>
          <View style={styles.width100}>
            <View style={alignment.MTmedium}>{renderGoogleAction()}</View>
            {enableApple && (
              <View style={alignment.MTmedium}>{renderAppleAction()}</View>
            )}

            <View style={alignment.MTmedium}>{renderEmailAction()}</View>
            <TouchableOpacity
              activeOpacity={0.7}
              style={styles.alreadyBtn}
              onPress={() => navigation.navigate(NAVIGATION_SCREEN.Login)}
            >
              <TextDefault style={[alignment.MLsmall]} bold>
                {i18n.t('alreadyMember')}
              </TextDefault>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </WrapperView>
  )
}
export default CreateAccount
