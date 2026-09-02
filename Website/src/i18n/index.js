import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

import en from './locales/en.json'
import ar from './locales/ar.json'
import de from './locales/de.json'
import fr from './locales/fr.json'
import km from './locales/km.json'
import zh from './locales/zh.json'

export const SUPPORTED_LANGUAGES = [
  { code: 'en', label: 'English', dir: 'ltr' },
  { code: 'ar', label: 'العربية', dir: 'rtl' },
  { code: 'de', label: 'Deutsch', dir: 'ltr' },
  { code: 'fr', label: 'Français', dir: 'ltr' },
  { code: 'km', label: 'ខ្មែរ', dir: 'ltr' },
  { code: 'zh', label: '中文', dir: 'ltr' }
]

const STORAGE_KEY = 'pickup.language'
const DEFAULT_LANGUAGE = 'en'

function isSupported(code) {
  return SUPPORTED_LANGUAGES.some(language => language.code === code)
}

function detectLanguage() {
  try {
    const saved = window.localStorage.getItem(STORAGE_KEY)
    if (saved && isSupported(saved)) return saved

    const browser = (navigator.language || '').slice(0, 2).toLowerCase()
    if (isSupported(browser)) return browser
  } catch (error) {
    // Ignore storage/access errors and fall back to the default.
  }
  return DEFAULT_LANGUAGE
}

const resources = {
  en: { translation: en },
  ar: { translation: ar },
  de: { translation: de },
  fr: { translation: fr },
  km: { translation: km },
  zh: { translation: zh }
}

export function dirFor(code) {
  const language = SUPPORTED_LANGUAGES.find(item => item.code === code)
  return language ? language.dir : 'ltr'
}

export function applyDocumentLanguage(code) {
  document.documentElement.lang = code
  document.documentElement.dir = dirFor(code)
}

i18n.use(initReactI18next).init({
  resources,
  lng: detectLanguage(),
  fallbackLng: DEFAULT_LANGUAGE,
  supportedLngs: SUPPORTED_LANGUAGES.map(language => language.code),
  interpolation: {
    escapeValue: false
  }
})

applyDocumentLanguage(i18n.language)

i18n.on('languageChanged', code => {
  applyDocumentLanguage(code)
  try {
    window.localStorage.setItem(STORAGE_KEY, code)
  } catch (error) {
    // Persistence is best-effort.
  }
})

export default i18n
