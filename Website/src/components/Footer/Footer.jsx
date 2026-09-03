import { useTranslation } from 'react-i18next'
import Logo from '../Logo/Logo.jsx'
import styles from './Footer.module.css'

const LINKS = [
  { id: 'how-it-works', key: 'nav.howItWorks' },
  { id: 'features', key: 'nav.features' },
  { id: 'for-customers', key: 'nav.forCustomers' },
  { id: 'about', key: 'nav.about' },
  { id: 'faq', key: 'nav.faq' },
  { id: 'contact', key: 'nav.contact' }
]

export default function Footer() {
  const { t } = useTranslation()
  const year = new Date().getFullYear()

  return (
    <footer className={styles.footer}>
      <div className={`container ${styles.inner}`}>
        <div className={styles.brandColumn}>
          <a className={styles.brand} href="#top">
            <span className={styles.logo}>
              <Logo />
            </span>
            <span className={styles.brandName}>{t('brand')}</span>
          </a>
          <p className={styles.tagline}>{t('footer.tagline')}</p>
        </div>

        <nav className={styles.links} aria-label={t('footer.navLabel')}>
          {LINKS.map(link => (
            <a key={link.id} href={`#${link.id}`}>
              {t(link.key)}
            </a>
          ))}
        </nav>
      </div>

      <div className={`container ${styles.bottom}`}>
        <p>
          © {year} {t('brand')}. {t('footer.rights')}
        </p>
      </div>
    </footer>
  )
}
