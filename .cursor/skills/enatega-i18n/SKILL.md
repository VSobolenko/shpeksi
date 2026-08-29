---
name: enatega-i18n
description: Add or edit user-facing strings across the Enatega localization files. Use when introducing new text in CustomerApp or editing translations.
disable-model-invocation: true
---

# Enatega localization

- CustomerApp uses `i18n-js`; translations live in `CustomerApp/src/translations/*.js`.
- Languages: `en`, `ar`, `de`, `fr`, `km`, `zh`.
- Every new user-facing string MUST be added to ALL language files with the same key.

## Workflow

1. Add the key to `en.js` (source of truth) with the English value.
2. Add the same key to every other language file with a translation (or the English fallback if unknown).
3. Use it in code via `i18n.t('key')` (match the existing helper/import).
4. Never leave a key present in `en.js` but missing from another language file.
