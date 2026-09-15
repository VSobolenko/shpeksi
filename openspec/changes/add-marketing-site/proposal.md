## Why

The platform now has a customer mobile app, a merchant admin panel, and a backend — but no public web presence that sells the platform itself to restaurants. The product is a white-label, self-pickup ordering solution; the merchants who would adopt it have no single page that explains what the platform is, what it does for them, and how to get started. A business-to-business marketing site fills that gap: it advertises the platform to restaurants and points them to a demo and the merchant panel.

## What Changes

- Add a new top-level module `Website/` — a public, **business-to-business** marketing/landing site for the **"Forkly"** white-label ordering platform.
- Build it with **Vite + React 18** (matching the Admin Dashboard's modernized stack) as a single-page landing site, producing a **static production build** (`dist/`) plus a local dev server.
- Ship the site **multilingual** in seven languages — `en`, `ar`, `de`, `fr`, `km`, `ru`, `zh` — with `ar` rendered right-to-left and the initial language auto-detected from the visitor's browser/system locale (English fallback).
- Position the site for **restaurants and merchants** (not consumers): white-label app, menu/order management, pickup-only (no delivery), and a "request a demo / get started" CTA plus a merchant-panel link.
- Provide a merchant-focused landing content set: hero, "how it works" (set up menu → receive orders → hand over at pickup), platform features, a "for your customers" section, about, FAQ for restaurant owners, contact, and a get-started/demo CTA.
- Follow the self-pickup-only model and "Forkly" branding already established in the repo: no delivery, riders, couriers, or third-party branding references anywhere.
- No GraphQL contract or backend changes; the site is static and does not call the GraphQL API.

## Capabilities

### New Capabilities

- `marketing-site`: The public "Forkly" marketing/landing website — its structure, B2B merchant-focused content requirements, multilingual (RTL) behavior, pickup-only branding constraints, and static build/deploy contract.

### Modified Capabilities

<!-- None: this is a brand-new surface; it does not change the requirements of existing capabilities. -->

## Impact

- New module `Website/` (Vite + React 18 single-page landing site, i18n for seven languages).
- Root `README.md` — add the `Website/` module and its run/build commands.
- No changes to `backend/`, `Admin Dashboard/`, or `CustomerApp/` code; no GraphQL contract changes.
