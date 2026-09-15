## Why

The Forkly system (backend + Admin Dashboard + CustomerApp) is about to go to production. This is the final pre-release sweep: a full-system, real-user walkthrough of every surface to catch any bug, broken layout, dead button, contract drift, or leftover legacy/delivery branding before launch — fixing each finding through the fix-loop so the user meets no failures or rough edges.

## What Changes

- Verify the backend (FastAPI + Strawberry GraphQL + MongoDB + Redis) end-to-end: automated tests, byte-compile, and the pickup-flow smoke test over HTTP + WebSocket subscriptions.
- Verify the Admin Dashboard (Vite + React 18) via Playwright: login, dashboard, orders/status, catalog CRUD, coupons, customers, configuration, notifications, and admin profile.
- Verify the CustomerApp (Expo SDK 57 + React Native, package `com.forkly.app`) via Maestro on the `Medium_Phone` AVD: the full customer journey.
- Verify cross-cutting flows: order lifecycle, registration → customer list, admin catalog/coupon changes → customer.
- Audit branding ("Forkly", `FRK` order prefix, `forkly` database), six-language localization completeness, and secret hygiene.
- Fix every finding in the owning module via an implementer subagent + task review, preserving the GraphQL contract (snake_case, operation names 1:1) and the pickup-only model.

## Capabilities

### New Capabilities

- `preprod-sweep`: Final pre-release verification sweep acceptance criteria across the backend, Admin Dashboard, CustomerApp, and cross-cutting flows, including evidence and fix-loop requirements.

### Modified Capabilities

<!-- None: this sweep brings implementation into conformance with existing specs; it does not change product behavior requirements. -->

## Impact

- `backend/` — tests, services, GraphQL resolvers (fixes only).
- `Admin Dashboard/` — views, components, Apollo operations (fixes only).
- `CustomerApp/` — screens, Apollo operations, translations (fixes only).
- No GraphQL contract changes; no delivery/rider model changes.
