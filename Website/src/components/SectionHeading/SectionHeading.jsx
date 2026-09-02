import styles from './SectionHeading.module.css'

export default function SectionHeading({ eyebrow, title, subtitle }) {
  return (
    <div className={styles.heading}>
      {eyebrow ? <p className={styles.eyebrow}>{eyebrow}</p> : null}
      <h2 className={styles.title}>{title}</h2>
      {subtitle ? <p className={styles.subtitle}>{subtitle}</p> : null}
    </div>
  )
}
