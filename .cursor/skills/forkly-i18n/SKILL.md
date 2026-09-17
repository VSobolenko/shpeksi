---
name: forkly-i18n
description: Add or edit user-facing strings across the Forkly localization files. Use when introducing new text in CustomerApp or Website, or editing translations.
disable-model-invocation: true
---

# Forkly localization

- CustomerApp uses `i18n-js`; translations live in `CustomerApp/translations/*.js`.
- CustomerApp languages: `en`, `ar`, `de`, `fr`, `km`, `ru`, `zh` (`ru` added for the RU/BY market).
- Website uses `i18next` with locale JSON in `Website/src/i18n/locales/*.json`
  (7 locales: `en`, `ar`, `de`, `fr`, `km`, `ru`, `zh`; `ar` is RTL).
- Every new user-facing string MUST be added to ALL language files for the module,
  with the same key.

## Workflow

1. Add the key to the module's English source (`en.js` / `en.json`) with the English value.
2. Add the same key to every other language file with a translation (or the English fallback if unknown).
3. Use it in code via `i18n.t('key')` (CustomerApp) or `t('key')` (Website), matching the existing helper/import.
4. Never leave a key present in `en` but missing from another language file.
