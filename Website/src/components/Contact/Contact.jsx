import { useTranslation } from 'react-i18next'
import { CONTACT_EMAIL, mailtoContact } from '../../config.js'
import SectionHeading from '../SectionHeading/SectionHeading.jsx'
import styles from './Contact.module.css'

function MailIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
      <polyline points="22,6 12,13 2,6" />
    </svg>
  )
}

export default function Contact() {
  const { t } = useTranslation()

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
              <MailIcon />
            </span>
            <h3 className={styles.label}>{t('contact.emailLabel')}</h3>
            <a
              className={styles.value}
              href={mailtoContact({
                subject: t('mail.contactSubject'),
                body: t('mail.contactBody')
              })}
            >
              {CONTACT_EMAIL}
            </a>
          </li>
        </ul>
      </div>
    </section>
  )
}
