import { useTranslation } from 'react-i18next'
import { ADMIN_URL, CUSTOMER_APP_URL } from '../../config.js'
import styles from './Download.module.css'

export default function Download() {
  const { t } = useTranslation()

  return (
    <section className={styles.section} id="download">
      <div className={`container ${styles.inner}`}>
        <p className={styles.eyebrow}>{t('download.eyebrow')}</p>
        <h2 className={styles.title}>{t('download.title')}</h2>
        <p className={styles.subtitle}>{t('download.subtitle')}</p>
        <div className={styles.actions}>
          <a
            className={styles.primary}
            href={CUSTOMER_APP_URL}
            target="_blank"
            rel="noopener noreferrer"
          >
            {t('download.customerCta')}
          </a>
          <a
            className={styles.secondary}
            href={ADMIN_URL}
            target="_blank"
            rel="noopener noreferrer"
          >
            {t('download.adminCta')}
          </a>
        </div>
        <p className={styles.note}>{t('download.merchantNote')}</p>
      </div>
    </section>
  )
}
