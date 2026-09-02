## Why

The platform now has a customer mobile app, a merchant admin panel, and a backend — but no public web presence. Anyone who hears about the product has no single page that introduces it, explains the pickup-only ordering flow, and points them to the apps. A marketing/landing site fills that gap: it is the brand's public face and the destination everyone sees when they want to learn about or start ordering from the product.

## What Changes

- Add a new top-level module `Website/` — a public marketing/landing site for the **"Pickup"** brand.
- Build it with **Vite + React 18** (matching the Admin Dashboard's modernized stack) as a single-page landing site, producing a **static production build** (`dist/`) plus a local dev server.
- Ship the site **multilingual** in seven languages — `en`, `ar`, `de`, `fr`, `km`, `ru`, `zh` — with `ar` rendered right-to-left and the initial language auto-detected from the visitor's browser/system locale (English fallback).
- Provide a standard landing-page content set: hero, value proposition, "how it works" (order → store prepares → pickup), feature highlights, menu showcase, about, FAQ, contact, and download/CTA links to the CustomerApp and Admin Dashboard.
- Follow the pickup-only model and neutral "Pickup" branding already established in the repo: no delivery, riders, couriers, or "Enatega" references anywhere.
- No GraphQL contract or backend changes; the site is static and does not call the GraphQL API.

## Capabilities

### New Capabilities

- `marketing-site`: The public "Pickup" marketing/landing website — its structure, content requirements, multilingual (RTL) behavior, pickup-only branding constraints, and static build/deploy contract.

### Modified Capabilities

<!-- None: this is a brand-new surface; it does not change the requirements of existing capabilities. -->

## Impact

- New module `Website/` (Vite + React 18 single-page landing site, i18n for seven languages).
- Root `README.md` — add the `Website/` module and its run/build commands.
- No changes to `backend/`, `Admin Dashboard/`, or `CustomerApp/` code; no GraphQL contract changes.
