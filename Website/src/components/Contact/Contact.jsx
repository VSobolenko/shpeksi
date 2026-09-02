import { useTranslation } from 'react-i18next'
import SectionHeading from '../SectionHeading/SectionHeading.jsx'
import styles from './Contact.module.css'

const ITEMS = [
  { key: 'email', icon: 'mail' },
  { key: 'phone', icon: 'phone' },
  { key: 'address', icon: 'pin' }
]

function Icon({ name }) {
  if (name === 'mail') {
    return (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
        <polyline points="22,6 12,13 2,6" />
      </svg>
    )
  }
  if (name === 'phone') {
    return (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.12.9.34 1.79.66 2.64a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.44-1.23a2 2 0 0 1 2.11-.45c.85.32 1.74.54 2.64.66A2 2 0 0 1 22 16.92z" />
      </svg>
    )
  }
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
      <circle cx="12" cy="10" r="3" />
    </svg>
  )
}

export default function Contact() {
  const { t } = useTranslation()
  const email = t('contact.email')
  const phone = t('contact.phone')

  return (
    <section className={styles.section} id="contact">
      <div className="container">
        <SectionHeading
          eyebrow={t('contact.eyebrow')}
          title={t('contact.title')}
          subtitle={t('contact.subtitle')}
        />
        <ul className={styles.grid}>
          <li className={styles.card}>
            <span className={styles.icon}>
              <Icon name="mail" />
            </span>
            <h3 className={styles.label}>{t('contact.emailLabel')}</h3>
            <a className={styles.value} href={`mailto:${email}`}>
              {email}
            </a>
          </li>
          <li className={styles.card}>
            <span className={styles.icon}>
              <Icon name="phone" />
            </span>
            <h3 className={styles.label}>{t('contact.phoneLabel')}</h3>
            <a className={styles.value} href={`tel:${phone}`}>
              {phone}
            </a>
          </li>
          <li className={styles.card}>
            <span className={styles.icon}>
              <Icon name="pin" />
            </span>
            <h3 className={styles.label}>{t('contact.addressLabel')}</h3>
            <p className={styles.value}>{t('contact.address')}</p>
          </li>
        </ul>
      </div>
    </section>
  )
}
