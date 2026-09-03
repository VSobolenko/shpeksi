## Context

The platform (customer app, admin dashboard, backend) already exists and is rebranded to the neutral "Pickup" brand with a pickup-only model. There is no public web surface. The marketing site is a new, standalone static module and does not call the GraphQL API. It is a **business-to-business** site: it sells the white-label ordering platform to restaurants/merchants, not food to consumers. It must match repo conventions: plain JavaScript (ES modules, no TypeScript), StandardJS style, and the seven-language requirement.

## Goals / Non-Goals

**Goals:**

- A fast, static, deploy-anywhere B2B marketing/landing site for "Pickup" aimed at restaurants/merchants.
- White-label positioning: sell the platform as "launch your own branded pickup ordering app" — never a consumer food menu.
- Multilingual (en, ar, de, fr, km, ru, zh) with correct RTL for Arabic.
- Consistent with the Admin Dashboard's Vite + React 18 stack and StandardJS conventions.
- Minimal new dependencies; no heavy UI framework.

**Non-Goals:**

- No backend integration, GraphQL calls, or dynamic content.
- No e-commerce/ordering functionality (ordering stays in the CustomerApp).
- No user accounts, analytics, or a CMS.
- No TypeScript (per repo convention).

## Decisions

### 1. Vite + React 18 (single-page), not Astro or static HTML
- **Why**: Reuses the exact toolchain the Admin Dashboard already uses (Vite + React 18), keeps one build system across web modules, and gives component-driven sections that are easy to keep consistent across seven languages.
- **Alternatives**: Astro would optimize static/SEO output but introduces a new framework/toolchain not used elsewhere; pure static HTML/CSS/JS would be simplest but makes seven-language, componentized, interactive sections (language switcher, FAQ accordion) tedious and error-prone.

### 2. Single-page landing with anchored sections, no router
- **Why**: A marketing page is one flow (scroll through sections); anchors + sticky nav + smooth scroll cover the need without a routing dependency.
- **Alternative**: React Router for separate `/about`, `/faq` pages — deferred; unnecessary for the initial site and adds a dependency.

### 3. i18n via `i18next` + `react-i18next` + `i18next-browser-languagedetector`, locale JSON resources
- **Why**: `i18next` is already the Admin Dashboard's i18n library, so it keeps the stack consistent. Locale content lives in `src/i18n/locales/{en,ar,de,fr,km,ru,zh}.json` as pure data, so every user-facing string is defined once per language and components render from keys.
- **Detection**: use `i18next-browser-languagedetector` (also already used by the Admin Dashboard) so the initial language is detected from the visitor's browser/system locale (navigator languages → localStorage → fallback), and the visitor's explicit choice persists in `localStorage`. Fallback language is `en`.
- **Alternative**: `i18n-js` (used by CustomerApp) is React Native-oriented; a hand-rolled context would reinvent i18next. Both rejected in favor of the Admin's proven web stack.
- **RTL**: the `<html>` element's `dir` and `lang` are set from the active locale (`dir="rtl"` for `ar`), and CSS uses logical properties where direction-sensitive.

### 4. Styling with CSS Modules + CSS variables (design tokens), no UI kit
- **Why**: A small, brand-consistent design system (color, spacing, typography, radius tokens) with CSS Modules keeps components scoped and dependency-free, consistent with StandardJS (no styled-components).
- **Alternative**: Tailwind is fast to iterate but adds a build dependency and a new styling paradigm not used elsewhere in the repo; SCSS mirrors the Admin's legacy `assets/scss` but Sass adds a compile step for marginal benefit here.

### 5. Configurable merchant links via `VITE_*` env
- **Why**: The demo/contact URL and the merchant panel URL are not fixed yet; exposing them via `.env.example` → `VITE_*` (e.g. `VITE_DEMO_URL`, `VITE_ADMIN_URL`) keeps the site deployable without hardcoding, honoring the secrets/env rule.
- **Fallback**: links default to a placeholder that is never broken so the CTA remains functional.

### 6. B2B content model (merchant-focused, no consumer menu)
- **Why**: The site's audience is restaurants/merchants adopting the platform, so the content sells the platform's value to a business buyer: white-label branding, menu/order management, pickup-only (no delivery fleet), and a "request a demo / get started" CTA.
- Sections: hero (launch your own pickup app), "how it works" for the merchant (set up menu → receive orders → hand over at pickup), platform features, a "for your customers" section (what the merchant's end customers experience), about, FAQ for restaurant owners, contact, get-started CTA. No consumer food menu showcase, no single-restaurant menu.

## Risks / Trade-offs

- [Arabic RTL layout breaks (flex/grid direction)] → set `dir="rtl"`, use CSS logical properties (`margin-inline-start`, `inset-inline`, etc.), and explicitly verify the `ar` locale in the runtime check.
- [Khmer/Chinese fonts render as tofu on some systems] → use a system font stack with broad fallbacks (`system-ui, -apple-system, "Segoe UI", "Noto Sans", sans-serif`); no remote fonts required.
- [Single-page client-rendered content is weaker for SEO/social previews] → set static `<title>`, meta description, Open Graph/Twitter tags, and a favicon/og-image in `index.html`; acceptable for an internal project.
- [App/demo URLs don't exist yet] → configurable `VITE_*` targets with sensible fallbacks; the CTA remains functional.
- [Locale drift — a string added in one language but missed in others] → the spec's language-completeness scenario is enforced by a review step and a translation-key parity check in tasks.
- [B2B framing drift — copy accidentally reverts to consumer "order your food"] → the spec's white-label positioning and pickup-only requirements are enforced in review; the source copy lives only in the locale JSON files, not inline in components.

## Migration Plan

1. Scaffold `Website/` with Vite (React 18, plain JS), `package.json`, `vite.config.js`, `index.html`, `.env.example`, and `.gitignore`.
2. Add i18n setup (`i18next`/`react-i18next` + `i18next-browser-languagedetector`) and the seven locale JSON files with the merchant-focused content set.
3. Build the section components and the page shell (nav, language switcher, footer) with merchant-focused copy.
4. `npm run dev` for local verification; `npm run build` produces `dist/`.
5. Deploy: serve `dist/` from any static host (or an internal static file server). Rollback is trivial (re-serve the previous `dist/`).

## Open Questions

- Exact demo/contact URL and merchant dashboard URL — deferred to configuration (`VITE_*`), no spec/approach change required.
