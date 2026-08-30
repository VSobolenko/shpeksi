## Why

The repo ships only frontends (Admin Dashboard, CustomerApp, RiderApp) wired to a third-party demo GraphQL server, with no backend of its own, hardcoded secrets, a deprecated courier app, and a heavily outdated legacy stack. This change turns it into a production-ready, self-owned **food-ordering platform with self-collect pickup**: customer orders → store sees and prepares → customer picks up. No courier or delivery remains.

## What Changes

- **Add a Python backend** (`backend/`) — FastAPI + Strawberry GraphQL + Beanie/MongoDB + Redis, serving `/graphql` over HTTP and WebSocket, implementing the frontend GraphQL contract 1:1 (field/operation names fixed by the existing frontends).
- **Replace the demo endpoint** — point Admin and CustomerApp at the self-hosted backend instead of `https://enatega-singlevendor.up.railway.app/graphql`.
- **Implement auth + roles** — JWT (`Authorization: Bearer`), `adminLogin` vs customer `login`/`createUser`, role guard between admin and customer operations.
- **Implement the order lifecycle** — `placeOrder`, `orders`/`order`, statuses `PENDING → ACCEPTED → READY → COMPLETED` (+ `CANCELLED`), with realtime subscriptions `subscribePlaceOrder` and `orderStatusChanged`.
- **Support the legacy WebSocket protocol** — dual-protocol (`subscriptions-transport-ws` + `graphql-transport-ws`) on one endpoint, so the current Apollo v2 frontends keep working while the frontend migrates to `@apollo/client` 3.x.
- **Implement payments** — COD, Stripe (REST `/stripe/charge`, `/stripe/cancel`, success/failed redirects), PayPal (client-side, server stores `client_id`/`client_secret`/`sandbox`).
- **Implement notifications** — Firebase FCM push (`sendNotificationUser`, status-change pushes) and SMTP email (order confirmation, `forgotPassword`/`resetPassword`).
- **Remove delivery entirely (BREAKING)** — delete `RiderApp/`; strip rider/delivery queries, mutations, subscriptions, statuses (`PICKED`/`DELIVERED`), delivery charges, delivery address, rider tracking, and the assign-rider UI from Admin and CustomerApp.
- **Clean up** — remove hardcoded secrets to `.env`/`.env.example`, delete cached/dead files, unused dependencies, the stray `"npm"` dependency, and normalize i18n.
- **Modernize** — Admin Dashboard to React 18 + Vite, `@apollo/client` 3.x, chart.js 4, firebase modular, react-router v6, sass; CustomerApp to Expo SDK 50+ and `@apollo/client` 3.x.
- **Harden for production** — secrets fail-fast (no `change-me` in prod), health/readiness endpoints, Redis-backed pub/sub for multi-instance, authenticated MongoDB/Redis, TLS termination via reverse proxy, environment-driven CORS, database backups, structured logging, non-root Dockerfile + docker-compose, automated tests + CI, and safe error handling.
- **De-brand from Enatega** — rename the database (`pickup`), order prefix (`ORD`), backend package (`pickup-backend`), and app display name to "Pickup", leaving root policy/docs files untouched.

## Capabilities

### New Capabilities

- `backend/graphql-api`: The self-hosted GraphQL API surface (queries, mutations, configuration singleton, menu entities, users) and its auth/role model, matching the fixed frontend contract.
- `backend/orders`: The order lifecycle, pickup status queue, and realtime WebSocket subscriptions (`subscribePlaceOrder`, `orderStatusChanged`) with dual-protocol support.
- `backend/payments`: COD, Stripe (REST endpoints), and PayPal configuration handling.
- `backend/notifications`: Firebase FCM push notifications and SMTP email delivery.
- `pickup-order-flow`: The self-collect product flow across CustomerApp and Admin Dashboard, including the removal of all rider/delivery behavior.

### Modified Capabilities

None — no existing specs under `openspec/specs/`.

## Impact

- **New code**: `backend/` (FastAPI app, models, GraphQL schema/types/resolvers, services, integrations, tests), plus `.env.example` and README.
- **Modified frontends**:
  - `Admin Dashboard/` — Apollo operations in `src/apollo/server.js`, order/configuration/riders views, routes/sidebar, React 18 + Vite migration.
  - `CustomerApp/` — Apollo operations, order/cart/checkout screens, status components, translations (`src/translations/*.js`), Expo SDK upgrade.
- **Removed**: `RiderApp/` (whole module), rider/delivery code paths and dependencies across Admin and CustomerApp.
- **Config**: `.env`/`.env.example` for backend and Admin; `environment.js` repointed to self-hosted backend; secrets removed from source; `CORS_ORIGINS`, MongoDB/Redis credentials, and log level driven by environment.
- **Deployment**: non-root `Dockerfile` + `docker-compose.yml` (app + MongoDB + Redis) with healthchecks, authenticated stores, a TLS reverse proxy (Caddyfile), and a documented backup/restore and deploy runbook.
- **De-branding**: database renamed `enatega` → `pickup`, order prefix `ENATEGA` → `ORD`, backend package → `pickup-backend`, and frontend app display name "Enatega" → "Pickup" (root policy/docs files untouched).
- **Dependencies**: Apollo Client v2 → v3 (`@apollo/client`), `subscriptions-transport-ws` → dual-protocol backend + `@apollo/client` client, legacy React/Expo/firebase/chart.js/react-router upgrades.
