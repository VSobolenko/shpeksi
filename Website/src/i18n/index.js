import i18n from 'i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import { initReactI18next } from 'react-i18next'

import en from './locales/en.json'
import ar from './locales/ar.json'
import de from './locales/de.json'
import fr from './locales/fr.json'
import km from './locales/km.json'
import ru from './locales/ru.json'
import zh from './locales/zh.json'

export const SUPPORTED_LANGUAGES = [
  { code: 'en', label: 'English', dir: 'ltr' },
  { code: 'ar', label: 'العربية', dir: 'rtl' },
  { code: 'de', label: 'Deutsch', dir: 'ltr' },
  { code: 'fr', label: 'Français', dir: 'ltr' },
  { code: 'km', label: 'ខ្មែរ', dir: 'ltr' },
  { code: 'ru', label: 'Русский', dir: 'ltr' },
  { code: 'zh', label: '中文', dir: 'ltr' }
]

const STORAGE_KEY = 'pickup.language'
const DEFAULT_LANGUAGE = 'en'

const resources = {
  en: { translation: en },
  ar: { translation: ar },
  de: { translation: de },
  fr: { translation: fr },
  km: { translation: km },
  ru: { translation: ru },
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

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: DEFAULT_LANGUAGE,
    supportedLngs: SUPPORTED_LANGUAGES.map(language => language.code),
    detection: {
      // localStorage first so an explicit choice wins over the browser language
      // on later visits; navigator is the first-visit fallback.
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: STORAGE_KEY,
      // Normalize regional codes (e.g. "ru-RU") to the supported base code ("ru").
      convertDetectedLanguage: lng => (lng || '').split('-')[0].toLowerCase()
    },
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
