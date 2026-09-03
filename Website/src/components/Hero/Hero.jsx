import { useTranslation } from 'react-i18next'
import styles from './Hero.module.css'

export default function Hero() {
  const { t } = useTranslation()

  return (
    <section className={styles.hero} id="top">
      <div className={`container ${styles.inner}`}>
        <div className={styles.copy}>
          <p className={styles.eyebrow}>{t('hero.eyebrow')}</p>
          <h1 className={styles.title}>{t('hero.title')}</h1>
          <p className={styles.subtitle}>{t('hero.subtitle')}</p>
          <div className={styles.actions}>
            <a className={styles.primary} href="#get-started">
              {t('hero.primaryCta')}
            </a>
            <a className={styles.secondary} href="#how-it-works">
              {t('hero.secondaryCta')}
            </a>
          </div>
        </div>
        <div className={styles.art} aria-hidden="true">
          <svg viewBox="0 0 320 300" className={styles.artSvg}>
            <circle cx="256" cy="64" r="86" fill="#ffffff" opacity="0.5" />
            <circle cx="60" cy="82" r="13" fill="#16a34a" opacity="0.9" />
            <circle cx="248" cy="212" r="10" fill="#ff8a4d" />
            <rect x="92" y="148" width="136" height="112" rx="18" fill="#ffffff" />
            <path
              d="M120 148v-22a40 40 0 0 1 80 0v22"
              fill="none"
              stroke="#ffffff"
              strokeWidth="14"
              strokeLinecap="round"
            />
            <circle cx="160" cy="196" r="26" fill="#16a34a" />
            <path
              d="M148 196l8 8 16-18"
              fill="none"
              stroke="#ffffff"
              strokeWidth="5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      </div>
    </section>
  )
}
