## 1. Scaffold

- [ ] 1.1 Create `Website/` as a Vite + React 18 (plain JS) project: `package.json`, `vite.config.js`, `index.html`, `.gitignore`, `.env.example`. Verify `npm install` and `npm run dev` start without errors.
- [ ] 1.2 Add dependencies `react`, `react-dom`, `i18next`, `react-i18next`, `i18next-browser-languagedetector`, and `@vitejs/plugin-react`. Verify `npm install` succeeds with no peer-dependency errors.

## 2. Internationalization

- [ ] 2.1 Add i18n init (`src/i18n/index.js`) wiring i18next + react-i18next + `i18next-browser-languagedetector`, detecting the initial language from the visitor's browser/system locale with `en` fallback and persisting the explicit choice. Verify the active language updates the document `lang` and `dir` attributes and that a browser set to a supported locale (e.g. `ru`) renders that locale on first load.
- [ ] 2.2 Create seven locale JSON files (`en`, `ar`, `de`, `fr`, `km`, `ru`, `zh`) containing the full landing content set. Verify every file has the same set of translation keys (parity check passes) and Russian renders fully.

## 3. Page shell

- [ ] 3.1 Build the app shell: sticky navigation, language switcher, and footer, with section anchors. Verify clicking a nav item scrolls to its section.
- [ ] 3.2 Implement RTL for Arabic (`dir="rtl"` on `<html>` when `ar` is active). Verify the `ar` locale renders right-to-left with correct text alignment.

## 4. Landing sections

- [ ] 4.1 Build the Hero section with a merchant-focused value proposition ("launch your own pickup ordering app") and a "request a demo / get started" primary CTA. Verify it renders translated copy and a working CTA in `en` and `ar`.
- [ ] 4.2 Build the "How it works" section from the merchant's perspective (set up menu → receive orders → hand over at pickup). Verify the three steps render in all seven languages.
- [ ] 4.3 Build the platform features section (white-label branding, menu/order management, pickup-only). Verify feature copy is white-label/merchant-focused and pickup-only (no delivery/rider wording, no consumer "order your food" framing).
- [ ] 4.4 Build the "For your customers" section (what the merchant's end customers experience — order ahead, live status, pickup reminders). Verify it renders with no consumer menu showcase.
- [ ] 4.5 Build the About, FAQ (accordion, restaurant-owner questions), and Contact sections. Verify the FAQ accordion toggles and the contact section renders contact info.
- [ ] 4.6 Build the Get-started/CTA section wired to configurable demo and merchant-panel URLs (with fallbacks). Verify CTAs resolve to the configured targets.

## 5. Styling and responsiveness

- [ ] 5.1 Create design tokens (CSS variables) and global styles, using CSS Modules for components. Verify styling applies and components are scoped.
- [ ] 5.2 Make the layout responsive and direction-safe using CSS logical properties. Verify no broken/overflowing content on a mobile (~375px) and desktop (~1280px) viewport.

## 6. SEO and metadata

- [ ] 6.1 Set `<title>`, meta description, Open Graph/Twitter tags, and add a favicon/og-image in `index.html`. Verify the tags are present in the built `dist/index.html`.

## 7. Build, audit, and docs

- [ ] 7.1 Run the production build. Verify `npm run build` completes with no errors and produces `dist/`.
- [ ] 7.2 Audit the site for pickup-only, white-label, merchant-focused branding. Verify no "Enatega", delivery, rider, or courier references remain, and no consumer "order your food" framing or single-restaurant menu showcase.
- [ ] 7.3 Do a runtime UI sweep: load the site in each language (including Arabic RTL and Russian) and at mobile + desktop widths, confirming no blank screens, missing translations, or dead navigation.
- [ ] 7.4 Update the root `README.md` to document the `Website/` module and its run/build commands.
