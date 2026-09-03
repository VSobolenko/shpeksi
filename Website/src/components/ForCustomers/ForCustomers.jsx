import { useTranslation } from 'react-i18next'
import SectionHeading from '../SectionHeading/SectionHeading.jsx'
import styles from './ForCustomers.module.css'

export default function ForCustomers() {
  const { t } = useTranslation()
  const items = t('forCustomers.items', { returnObjects: true })

  return (
    <section className={styles.section} id="for-customers">
      <div className="container">
        <SectionHeading
          eyebrow={t('forCustomers.eyebrow')}
          title={t('forCustomers.title')}
          subtitle={t('forCustomers.subtitle')}
        />
        <ul className={styles.grid}>
          {items.map((item, index) => (
            <li key={index} className={styles.card}>
              <h3 className={styles.cardTitle}>{item.title}</h3>
              <p className={styles.cardText}>{item.text}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
