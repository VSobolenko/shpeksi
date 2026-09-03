import { useTranslation } from 'react-i18next'
import { ADMIN_URL, DEMO_URL } from '../../config.js'
import styles from './GetStarted.module.css'

export default function GetStarted() {
  const { t } = useTranslation()

  return (
    <section className={styles.section} id="get-started">
      <div className={`container ${styles.inner}`}>
        <p className={styles.eyebrow}>{t('getStarted.eyebrow')}</p>
        <h2 className={styles.title}>{t('getStarted.title')}</h2>
        <p className={styles.subtitle}>{t('getStarted.subtitle')}</p>
        <div className={styles.actions}>
          <a
            className={styles.primary}
            href={DEMO_URL}
            target="_blank"
            rel="noopener noreferrer"
          >
            {t('getStarted.primaryCta')}
          </a>
          <a
            className={styles.secondary}
            href={ADMIN_URL}
            target="_blank"
            rel="noopener noreferrer"
          >
            {t('getStarted.secondaryCta')}
          </a>
        </div>
        <p className={styles.note}>{t('getStarted.note')}</p>
      </div>
    </section>
  )
}
