import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import Logo from '../Logo/Logo.jsx'
import LanguageSwitcher from '../LanguageSwitcher/LanguageSwitcher.jsx'
import styles from './Nav.module.css'

const LINKS = [
  { id: 'how-it-works', key: 'nav.howItWorks' },
  { id: 'features', key: 'nav.features' },
  { id: 'for-customers', key: 'nav.forCustomers' },
  { id: 'about', key: 'nav.about' },
  { id: 'faq', key: 'nav.faq' },
  { id: 'contact', key: 'nav.contact' }
]

export default function Nav() {
  const { t } = useTranslation()
  const [open, setOpen] = useState(false)

  const close = () => setOpen(false)

  return (
    <header className={styles.header}>
      <div className={`container ${styles.inner}`}>
        <a className={styles.brand} href="#top" onClick={close}>
          <span className={styles.logo}>
            <Logo />
          </span>
          <span className={styles.brandName}>{t('brand')}</span>
        </a>

        <nav
          className={open ? `${styles.nav} ${styles.navOpen}` : styles.nav}
          aria-label={t('footer.navLabel')}
        >
          {LINKS.map(link => (
            <a key={link.id} className={styles.link} href={`#${link.id}`} onClick={close}>
              {t(link.key)}
            </a>
          ))}
          <a className={styles.cta} href="#get-started" onClick={close}>
            {t('nav.getStarted')}
          </a>
        </nav>

        <div className={styles.actions}>
          <LanguageSwitcher />
          <button
            className={styles.toggle}
            type="button"
            aria-expanded={open}
            aria-label={t('nav.menuToggle')}
            onClick={() => setOpen(previous => !previous)}
          >
            <span />
            <span />
            <span />
          </button>
        </div>
      </div>
    </header>
  )
}
