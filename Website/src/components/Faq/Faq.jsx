import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import SectionHeading from '../SectionHeading/SectionHeading.jsx'
import styles from './Faq.module.css'

export default function Faq() {
  const { t } = useTranslation()
  const items = t('faq.items', { returnObjects: true })
  const [openIndex, setOpenIndex] = useState(0)

  return (
    <section className={styles.section} id="faq">
      <div className={`container ${styles.container}`}>
        <SectionHeading
          eyebrow={t('faq.eyebrow')}
          title={t('faq.title')}
          subtitle={t('faq.subtitle')}
        />
        <ul className={styles.list}>
          {items.map((item, index) => {
            const open = openIndex === index
            return (
              <li
                key={index}
                className={open ? `${styles.item} ${styles.itemOpen}` : styles.item}
              >
                <button
                  type="button"
                  className={styles.question}
                  aria-expanded={open}
                  onClick={() => setOpenIndex(open ? -1 : index)}
                >
                  <span>{item.question}</span>
                  <svg
                    className={open ? `${styles.chevron} ${styles.chevronOpen}` : styles.chevron}
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <polyline points="6 9 12 15 18 9" />
                  </svg>
                </button>
                <div className={styles.answerWrap} role="region">
                  <div className={styles.answer}>
                    <p>{item.answer}</p>
                  </div>
                </div>
              </li>
            )
          })}
        </ul>
      </div>
    </section>
  )
}
