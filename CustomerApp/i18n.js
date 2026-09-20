import AsyncStorage from '@react-native-async-storage/async-storage'
import * as Localization from 'expo-localization'
import i18n from 'i18n-js'
import { de } from './translations/de'
import { en } from './translations/en'
import { fr } from './translations/fr'
import { km } from './translations/km'
import { zh } from './translations/zh'
import { ar } from './translations/ar'
import { ru } from './translations/ru'

// Only locales we actually ship may be handed to i18n-js, otherwise the UI
// would silently fall back to English.
const isSupported = code =>
  code != null && Object.prototype.hasOwnProperty.call(i18n.translations, code)

// Language to use when the user has never picked one: the first device language
// we ship, else English. Note `getLocales()` is the current expo-localization
// API - the old `Localization.locale` getter no longer exists (verified against
// the installed expo-localization 57.0.1), so reading it yielded `undefined`
// and pinned the app to English on iOS.
const deviceLanguage = () => {
  for (const locale of Localization.getLocales()) {
    const base = String(locale.languageCode).toLowerCase()
    if (isSupported(base)) return base
  }
  return i18n.defaultLocale
}

i18n.initAsync = async() => {
  i18n.fallbacks = true
  i18n.translations = { fr, en, km, zh, de, ar, ru }
  // An explicit choice in Settings always wins; otherwise follow the device.
  const saved = await AsyncStorage.getItem('pikupo-language')
  i18n.locale = isSupported(saved) ? saved : deviceLanguage()
}

export default i18n
