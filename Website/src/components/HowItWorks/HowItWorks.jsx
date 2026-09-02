import { useTranslation } from 'react-i18next'
import SectionHeading from '../SectionHeading/SectionHeading.jsx'
import styles from './HowItWorks.module.css'

export default function HowItWorks() {
  const { t } = useTranslation()
  const steps = t('howItWorks.steps', { returnObjects: true })

  return (
    <section className={styles.section} id="how-it-works">
      <div className="container">
        <SectionHeading
          eyebrow={t('howItWorks.eyebrow')}
          title={t('howItWorks.title')}
          subtitle={t('howItWorks.subtitle')}
        />
        <ol className={styles.steps}>
          {steps.map((step, index) => (
            <li key={index} className={styles.step}>
              <span className={styles.number}>{index + 1}</span>
              <h3 className={styles.stepTitle}>{step.title}</h3>
              <p className={styles.stepText}>{step.text}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}
