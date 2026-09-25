import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import en from './translations/en'
import de from './translations/de'
import fr from './translations/fr'
import km from './translations/km'
import zh from './translations/zh'
import ru from './translations/ru'

const SUPPORTED = ['en', 'de', 'fr', 'km', 'zh', 'ru']

function detectLanguage() {
  const stored = localStorage.getItem('pikupo-language')
  if (stored && SUPPORTED.includes(stored)) return stored
  const nav = (navigator.language || navigator.userLanguage || 'en')
    .slice(0, 2)
    .toLowerCase()
  return SUPPORTED.includes(nav) ? nav : 'en'
}

const initialLng = detectLanguage()
if (!localStorage.getItem('pikupo-language')) {
  localStorage.setItem('pikupo-language', initialLng)
}

i18n.use(initReactI18next).init({
  resources: {
    en,
    de,
    fr,
    km,
    zh,
    ru
  },
  lng: initialLng,
  fallbackLng: 'en',
  debug: false,
  interpolation: {
    escapeValue: false
  }
})

export default i18n
