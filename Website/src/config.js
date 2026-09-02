// Configurable external links. Values come from VITE_* env vars with sensible
// fallbacks so the site is never left with a dead link when env is missing.

const GITHUB_FALLBACK = 'https://github.com/VSobolenko/shpeksi'

export const CUSTOMER_APP_URL =
  import.meta.env.VITE_CUSTOMER_APP_URL || GITHUB_FALLBACK

export const ADMIN_URL = import.meta.env.VITE_ADMIN_URL || GITHUB_FALLBACK
