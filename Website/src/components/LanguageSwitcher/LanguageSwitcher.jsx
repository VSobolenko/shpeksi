import { useTranslation } from 'react-i18next'
import { SUPPORTED_LANGUAGES } from '../../i18n/index.js'
import styles from './LanguageSwitcher.module.css'

export default function LanguageSwitcher() {
  const { i18n, t } = useTranslation()

  return (
    <label className={styles.label}>
      <span className="visually-hidden">{t('footer.languageLabel')}</span>
      <select
        className={styles.select}
        value={i18n.language}
        onChange={event => i18n.changeLanguage(event.target.value)}
      >
        {SUPPORTED_LANGUAGES.map(language => (
          <option key={language.code} value={language.code}>
            {language.label}
          </option>
        ))}
      </select>
    </label>
  )
}
