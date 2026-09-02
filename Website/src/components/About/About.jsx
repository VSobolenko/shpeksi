import { useTranslation } from 'react-i18next'
import styles from './About.module.css'

export default function About() {
  const { t } = useTranslation()
  const points = t('about.points', { returnObjects: true })

  return (
    <section className={styles.section} id="about">
      <div className="container">
        <div className={styles.grid}>
          <div className={styles.copy}>
            <p className={styles.eyebrow}>{t('about.eyebrow')}</p>
            <h2 className={styles.title}>{t('about.title')}</h2>
            <p className={styles.text}>{t('about.text')}</p>
          </div>
          <ul className={styles.points}>
            {points.map((point, index) => (
              <li key={index} className={styles.point}>
                <span className={styles.check} aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </span>
                <div>
                  <h3 className={styles.pointTitle}>{point.title}</h3>
                  <p className={styles.pointText}>{point.text}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
