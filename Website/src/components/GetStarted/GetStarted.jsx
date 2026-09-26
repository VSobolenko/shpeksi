import { useTranslation } from 'react-i18next'
import { mailtoContact } from '../../config.js'
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
            href={mailtoContact({
              subject: t('mail.demoSubject'),
              body: t('mail.demoBody')
            })}
          >
            {t('getStarted.primaryCta')}
          </a>
          <a
            className={styles.secondary}
            href={mailtoContact({
              subject: t('mail.contactSubject'),
              body: t('mail.contactBody')
            })}
          >
            {t('getStarted.secondaryCta')}
          </a>
        </div>
        <p className={styles.note}>{t('getStarted.note')}</p>
      </div>
    </section>
  )
}
