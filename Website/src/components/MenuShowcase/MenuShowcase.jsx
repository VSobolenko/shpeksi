import { useTranslation } from 'react-i18next'
import SectionHeading from '../SectionHeading/SectionHeading.jsx'
import styles from './MenuShowcase.module.css'

function DishArt() {
  return (
    <svg viewBox="0 0 120 100" className={styles.dishArt}>
      <path
        d="M20 55a40 40 0 0 1 80 0"
        fill="none"
        stroke="currentColor"
        strokeWidth="5"
        strokeLinecap="round"
      />
      <circle cx="60" cy="10" r="5" fill="currentColor" />
      <rect x="14" y="55" width="92" height="8" rx="4" fill="currentColor" />
    </svg>
  )
}

export default function MenuShowcase() {
  const { t } = useTranslation()
  const items = t('menu.items', { returnObjects: true })

  return (
    <section className={styles.section} id="menu">
      <div className="container">
        <SectionHeading
          eyebrow={t('menu.eyebrow')}
          title={t('menu.title')}
          subtitle={t('menu.subtitle')}
        />
        <ul className={styles.grid}>
          {items.map((item, index) => (
            <li key={index} className={styles.card}>
              <div className={styles.art} aria-hidden="true">
                <DishArt />
              </div>
              <div className={styles.body}>
                <div className={styles.row}>
                  <h3 className={styles.name}>{item.name}</h3>
                  <span className={styles.price}>{item.price}</span>
                </div>
                <p className={styles.description}>{item.description}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
