// Configurable external links. Values come from VITE_* env vars with sensible
// fallbacks so the site is never left with a dead link when env is missing.

const FALLBACK_URL = 'https://example.com'

export const DEMO_URL = import.meta.env.VITE_DEMO_URL || FALLBACK_URL

export const ADMIN_URL = import.meta.env.VITE_ADMIN_URL || FALLBACK_URL
