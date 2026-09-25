import { useMutation, gql } from '@apollo/client'
import { useNavigation, useTheme } from '@react-navigation/native'
import * as Localization from 'expo-localization'
import React, { useContext, useState } from 'react'
import {
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  TouchableOpacity,
  View
} from 'react-native'
import {
  FilledTextField,
  CustomIcon,
  PikupoImage,
  FlashMessage,
  Spinner,
  TextDefault,
  WrapperView
} from '../../components'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { createUser } from '../../apollo/server'
import UserContext from '../../context/User'
import { alignment } from '../../utils/alignment'
import Analytics from '../../utils/analytics'
import { ICONS_NAME, NAVIGATION_SCREEN } from '../../utils/constant'
import { getNotificationTokenSafe } from '../../utils/pushToken'
// eslint-disable-next-line camelcase
import countryCodes from '../../utils/country_codes'
import { scale, verticalScale } from '../../utils/scaling'
import useStyle from './styles'
import i18n from '../../../i18n'

const CREATEUSER = gql`
  ${createUser}
`

const Logo = require('../../../assets/logo.png')

function Register() {
  const styles = useStyle()
  const { colors } = useTheme()
  const navigation = useNavigation()
  const inset = useSafeAreaInsets()
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [lastname, setLastname] = useState('')
  const [password, setPassword] = useState('')
  const [firstname, setFirstname] = useState('')
  const [loading, setLoading] = useState(false)
  const [emailError, setEmailError] = useState(null)
  const [phoneError, setPhoneError] = useState(null)
  const [lastnameError, setLastnameError] = useState(null)
  const [passwordError, setPasswordError] = useState(null)
  const [firstnameError, setFirstnameError] = useState(null)

  const { setTokenAsync } = useContext(UserContext)

  const [mutate] = useMutation(CREATEUSER, { onCompleted, onError })

  function validateCredentials() {
    let result = true

    setEmailError(null)
    setPasswordError(null)
    setPhoneError(null)
    setFirstnameError(null)
    setLastnameError(null)

    const emailRegex = /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,})+$/
    if (!emailRegex.test(email.trim())) {
      setEmailError(i18n.t('invalidEmail'))
      result = false
    }
    if (!password) {
      setPasswordError(i18n.t('passReq'))
      result = false
    }
    const phoneDigits = phone.replace(/\D/g, '')
    if (!/^\d{9,15}$/.test(phoneDigits)) {
      setPhoneError(i18n.t('invalidPhone'))
      result = false
    }
    if (!firstname.trim() || firstname.trim().length > 30) {
      setFirstnameError(i18n.t('firstNameReq'))
      result = false
    }
    if (!lastname.trim() || lastname.trim().length > 30) {
      setLastnameError(i18n.t('lastNameReq'))
      result = false
    }
    return result
  }

  async function onCompleted(data) {
    try {
      const trackingOpts = {
        id: data.createUser.userId,
        usernameOrEmail: data.createUser.email
      }
      Analytics.identify(data.createUser.userId, trackingOpts)
      Analytics.track(Analytics.events.USER_CREATED_ACCOUNT, trackingOpts)
      setTokenAsync(data.createUser.token)
      navigation.navigate(NAVIGATION_SCREEN.Menu)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  function onError(error) {
    try {
      FlashMessage({
        message: error.graphQLErrors[0].message
      })
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

  function renderJoinAction() {
    if (loading) return <Spinner />
    return (
      <TouchableOpacity
        testID="register-submit"
        style={styles.joinBtn}
        activeOpacity={0.7}
        onPress={async() => {
          if (validateCredentials()) {
            const user = {
              phone: `+${phone.replace(/\D/g, '')}`,
              email: email.toLowerCase().trim(),
              password,
              name: `${firstname.trim()} ${lastname.trim()}`,
              picture: ''
            }
            mutateLogin(user)
          }
        }}>
        <TextDefault bold>{i18n.t('signup')}</TextDefault>
      </TouchableOpacity>
    )
  }

  function updateCountryCode() {
    // `Localization.timezone` was removed from expo-localization (the time zone
    // now lives on `getCalendars()`), so this dereferenced `undefined` and threw
    // as soon as the phone field gained focus - registration was unreachable.
    const deviceTimeZone = Localization.getCalendars()[0]?.timeZone?.toLowerCase()
    const timezone = countryCodes.find(
      value => value.timezone.toLowerCase() === deviceTimeZone
    )
    if (!phone && timezone) {
      setPhone(String(timezone.country_code).replace(/\D/g, ''))
    }
  }

  return (
    <WrapperView>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.flex}>
        <ScrollView
          style={[styles.flex, { paddingTop: inset.top }]}
          contentContainerStyle={{ flexGrow: 1, paddingTop: verticalScale(20) }}
          showsVerticalScrollIndicator={false}
          alwaysBounceVertical={false}>
          <View style={styles.mainContainer}>
            <View style={styles.headerContainer}>
              <TouchableOpacity
                onPress={() => navigation.goBack()}
                style={[styles.backBtnWidth, styles.backBtn]}>
                <CustomIcon
                  name={ICONS_NAME.Back}
                  size={scale(20)}
                  color={colors.iconColor}
                />
              </TouchableOpacity>
              <TextDefault center H4 bold>
                {i18n.t('signup')}
              </TextDefault>
              <View style={styles.backBtnWidth} />
            </View>
            <View style={styles.subContainer}>
              <View style={[styles.flex, styles.upperContainer]}>
                <PikupoImage
                  imgStyle={[
                    styles.imgResponsive,
                    { backgroundColor: 'transparent' }
                  ]}
                  imgSource={Logo}
                  spinnerProps={{ style: styles.loadingView }}
                />
              </View>
              <View style={styles.width100}>
                <FilledTextField
                  testID="register-firstname"
                  error={firstnameError}
                  label="First name"
                  labelFontSize={scale(12)}
                  fontSize={scale(12)}
                  labelHeight={10}
                  activeLineWidth={0}
                  lineWidth={0}
                  textColor={colors.fontMainColor}
                  baseColor={colors.fontMainColor}
                  errorColor={colors.errorColor}
                  tintColor={colors.selected}
                  labelTextStyle={styles.labelStyle}
                  inputContainerStyle={styles.textContainer}
                  onChangeText={text => {
                    setFirstname(text)
                  }}
                  maxLength={30}
                />
                <FilledTextField
                  testID="register-lastname"
                  error={lastnameError}
                  label="Last name"
                  labelFontSize={scale(12)}
                  fontSize={scale(12)}
                  labelHeight={10}
                  activeLineWidth={0}
                  lineWidth={0}
                  textColor={colors.fontMainColor}
                  baseColor={colors.fontMainColor}
                  errorColor={colors.errorColor}
                  tintColor={colors.selected}
                  labelTextStyle={styles.labelStyle}
                  inputContainerStyle={styles.textContainer}
                  onChangeText={text => {
                    setLastname(text)
                  }}
                  maxLength={30}
                />
                <FilledTextField
                  testID="register-email"
                  error={emailError}
                  keyboardType={'email-address'}
                  label="Email address"
                  labelFontSize={scale(12)}
                  fontSize={scale(12)}
                  labelHeight={10}
                  activeLineWidth={0}
                  lineWidth={0}
                  textColor={colors.fontMainColor}
                  baseColor={colors.fontMainColor}
                  errorColor={colors.errorColor}
                  tintColor={colors.selected}
                  labelTextStyle={styles.labelStyle}
                  inputContainerStyle={styles.textContainer}
                  onChangeText={text => {
                    setEmail(text.toLowerCase().trim())
                  }}
                />
                <FilledTextField
                  testID="register-phone"
                  prefix="+"
                  value={phone}
                  error={phoneError}
                  keyboardType={'phone-pad'}
                  label="Mobile number"
                  labelFontSize={scale(12)}
                  activeLineWidth={0}
                  lineWidth={0}
                  fontSize={scale(12)}
                  labelHeight={10}
                  onFocus={updateCountryCode}
                  textColor={colors.fontMainColor}
                  baseColor={colors.fontMainColor}
                  errorColor={colors.errorColor}
                  tintColor={colors.selected}
                  labelTextStyle={styles.labelStyle}
                  inputContainerStyle={styles.textContainer}
                  onChangeText={text => {
                    setPhone(text.replace(/\D/g, ''))
                  }}
                  maxLength={15}
                />
                <FilledTextField
                  testID="register-password"
                  error={passwordError}
                  label="Password"
                  secureTextEntry={true}
                  labelFontSize={scale(12)}
                  fontSize={scale(12)}
                  labelHeight={10}
                  activeLineWidth={0}
                  lineWidth={0}
                  textColor={colors.fontMainColor}
                  baseColor={colors.fontMainColor}
                  errorColor={colors.errorColor}
                  tintColor={colors.selected}
                  labelTextStyle={styles.labelStyle}
                  inputContainerStyle={styles.textContainer}
                  onChangeText={text => {
                    setPassword(text.trim())
                  }}
                />
                <View style={[styles.marginTop5]}>{renderJoinAction()}</View>
                <TouchableOpacity
                  activeOpacity={0.7}
                  onPress={() =>
                    navigation.navigate(NAVIGATION_SCREEN.ForgotPassword)
                  }>
                  <TextDefault style={alignment.MTsmall} bold center>
                    {i18n.t('forgotPassword')}
                  </TextDefault>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </WrapperView>
  )
}

export default Register
